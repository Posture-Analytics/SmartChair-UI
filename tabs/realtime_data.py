import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import polars as pl

from dash import dcc, html, Input, Output
from plotly.subplots import make_subplots

from modules import predictor
from modules.base_app import app
from modules.z_generator import points, is_back_point, generate_z

# ===== Helper functions ===== #
def create_contour_graph(data: pl.DataFrame) -> go.Figure:
    """
    Creates a figure with two heatmaps.
    """
    z = generate_z(data)
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
    data : pl.DataFrame
        The data to use.

    Returns
    -------
    go.Figure
        The figure with the graph.
    """
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

# ===== Base layout ===== #
layout = html.Div([
    dbc.Row(justify="center", children=[
        dbc.Col([
            html.H2("Real Time Data", className="tabTitle"),
            dcc.Graph(id="realTimeContourGraph"),
            dcc.Graph(id="realTimeUnbalanceGraph"),
            dcc.Interval(id="realTimeGraphsInterval", interval=500, n_intervals=0)
        ], width=8, style={"textAlign": "center", "align-content": "center"}),
    ]),
])

# ===== Callbacks ===== #
@app.callback(Output("realTimeContourGraph", "figure"),
              Output("realTimeUnbalanceGraph", "figure"),
              Input("realTimeGraphsInterval", "n_intervals"))
def update_real_time_graphs(n: int) -> tuple[go.Figure, go.Figure]:
    state, data = predictor.get_current_data()

    if state == "Not Sitting":
        return go.Figure(), go.Figure()

    contour_graph = create_contour_graph(data)
    unbalance_graph = create_unbalance_graph(data)

    return contour_graph, unbalance_graph
