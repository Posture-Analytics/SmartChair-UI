import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import polars as pl

from dash import dcc, html, Input, Output
from datetime import datetime
from plotly.subplots import make_subplots
from modules import predictor
from modules.base_app import app
from modules.z_generator import points, is_back_point, generate_z

# ===== Low RAM mode ===== #
LOWRAM = True

# ===== Variables ===== #
data_history = {}

# ===== Helper functions ===== #
def create_contour_graph(data: pl.DataFrame) -> go.Figure:
    """
    Creates a figure with two heatmaps representing the posture for
    the seat and backrest, respectively.

    Parameters
    ----------
    data : polars.DataFrame
        The data to use.

    Returns
    -------
    plotly.graph_objects.Figure
        The figure with the graph.
    """
    z = generate_z(data.drop("index"))
    label = dict(font_size=14)
    contours = dict(start=0, end=4608, showlines= False)
    template = "Value: %{z:.2f}<extra></extra>"

    fig = make_subplots(rows=1, cols=2, subplot_titles=("Seat", "Backrest"))
    fig.add_trace(go.Contour(z=z[0], connectgaps=True, contours=contours, hoverlabel=label,
                                colorscale="Blues", hovertemplate=template), row=1, col=1)
    fig.add_trace(go.Contour(z=z[1], connectgaps=True, contours=contours, hoverlabel=label,
                                colorscale="Blues", hovertemplate=template), row=1, col=2)

    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)

    for key in points:
        fig.add_annotation(x=points[key][1], y=points[key][0], text=key, showarrow=False,
                           font=dict(size=12), row=1, col=1 + is_back_point(key))

    return fig

def create_unbalance_graph(data: pl.DataFrame) -> go.Figure:
    """
    Quantifies how assymetric the seat and backrest are.

    Parameters
    ----------
    data : polars.DataFrame
        The data to use.

    Returns
    -------
    plotly.graph_objects.Figure
        The figure with the graph.
    """
    if LOWRAM:
        return None

    asymmetry_data = {
        "F - seat top": data[0, 10] - data[0, 11],
        "E - seat top-mid": data[0, 8] - data[0, 9],
        "D - seat bottom-mid": data[0, 6] - data[0, 7],
        "C - seat bottom": data[0, 4] - data[0, 5],
        "B - backrest top": data[0, 2] - data[0, 3],
        "A - backrest bottom": data[0, 0] - data[0, 1]
    }
    color_list = np.where(np.array(list(asymmetry_data.values())) > 0, "#2986EB", "#EB6963")
    fig = px.bar(x=list(asymmetry_data.values()), y=list(asymmetry_data.keys()), orientation="h")
    fig.update_layout(title_text="Pressure Asymmetry",
                    xaxis_title="Left - Right",
                    yaxis_title="Part of seat",
                    xaxis=dict(range=[-512, 512]),
                    showlegend=False)
    fig.update_traces(marker_color=color_list)
    return fig

def create_bar_graph(data: pl.DataFrame) -> go.Figure:
    """
    Creates a bar graph with the pressure data.

    Parameters
    ----------
    data : polars.DataFrame
        The data to use.

    Returns
    -------
    plotly.graph_objects.Figure
        The figure with the graph.
    """
    if LOWRAM:
        return None

    fig = go.Figure()
    fig.add_trace(go.Bar(x=data.columns, y=data.row(0), name="Pressure"))
    fig.update_layout(title_text="Pressure Data",
                    xaxis_title="Sensor",
                    yaxis_title="Pressure",
                    yaxis_range=[0, 4096],
                    showlegend=True)
    return fig

def create_line_graph(data: pl.DataFrame) -> go.Figure:
    """
    Creates a line graph with the pressure data along the time.

    Parameters
    ----------
    data : polars.DataFrame
        The data to use.

    Returns
    -------
    plotly.graph_objects.Figure
        The figure with the graph.
    """
    if LOWRAM:
        return None

    # If there"s new data
    if data.shape[0] > 0:
        # Save the data in the history
        if len(data_history) == 0:
            for key in data.columns:
                data_history[key] = []
            data_history["time"] = []
        for key in data.columns:
            data_history[key].append(data[key][0])
        data_history["time"].append(datetime.now())

    # Create the figure
    fig = go.Figure()
    for key in data_history.keys():
        if key != "time":
            fig.add_trace(go.Scatter(x=data_history["time"], y=data_history[key], name=key))

    # Update the layout
    fig.update_layout(title_text="Pressure Data",
                    xaxis_title="Time",
                    yaxis_title="Pressure",
                    hovermode="x unified",
                    showlegend=True)

    return fig

# ===== Base layout ===== #
layout = html.Div([
    dbc.Row(justify="center", children=[
        dbc.Col([
            html.H2("Real Time Data", className="tabTitle"),
            dcc.Graph(id="realTimeContourGraph"),
            dcc.Graph(id="realTimeUnbalanceGraph"),
            dcc.Graph(id="realTimeBarGraph"),
            dcc.Graph(id="HistoryLineGraph"),
            dcc.Interval(id="realTimeGraphsInterval", interval=500, n_intervals=0)
        ], width=8, style={"textAlign": "center", "align-content": "center"}),
    ]),
])

total = []
data_time = []
countour = []
unbalance = []
bar = []
line = []

# ===== Callbacks ===== #
@app.callback(Output("realTimeContourGraph", "figure"),
              Output("realTimeUnbalanceGraph", "figure"),
              Output("realTimeBarGraph", "figure"),
              Output("HistoryLineGraph", "figure"),
              Input("realTimeGraphsInterval", "n_intervals"))
def update_real_time_graphs(n: int) -> tuple[go.Figure, ...]:
    from time import time
    start_total = time()
    start = time()
    state, data = predictor.get_current_data()
    data_time.append(time() - start)

    if data.shape[0] == 0:
        return go.Figure(), go.Figure(), go.Figure(), create_line_graph(data)

    start = time()
    contour_graph = create_contour_graph(data)
    countour.append(time() - start)
    start = time()
    unbalance_graph = create_unbalance_graph(data)
    unbalance.append(time() - start)
    start = time()
    bar_graph = create_bar_graph(data)
    bar.append(time() - start)
    start = time()
    line_graph = create_line_graph(data)
    line.append(time() - start)

    total.append(time() - start_total)

    if n % 5 == 0:
        for name, l in zip(
            ("Data", "Contour", "Unbalance", "Bar", "Line", "Total"),
            (data_time, countour, unbalance, bar, line, total)
        ):
            print(f"{name}: {np.mean(l[-5:])}")

    return contour_graph, unbalance_graph, bar_graph, line_graph
