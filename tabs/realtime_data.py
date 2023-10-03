from dash import Dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import datetime
from modules import predictor
from modules.base_app import app

# ===== Low RAM mode ===== #
LOWRAM = False

# ===== Variables ===== #
data_history = {}

# ===== Helper functions ===== #
def create_unbalance_graph(data) -> go.Figure:
    """
    Quantifies how assymetric the seat and backrest are.
    """
    if LOWRAM:
        return None
    
    asymmetry_data = {
        'F - seat top': data['p10'][0] - data['p11'][0],
        'E - seat top-mid': data['p08'][0] - data['p09'][0],
        'D - seat bottom-mid': data['p06'][0] - data['p07'][0],
        'C - seat bottom': data['p04'][0] - data['p05'][0],
        'B - backrest top': data['p02'][0] - data['p03'][0],
        'A - backrest bottom': data['p00'][0] - data['p01'][0]
    }
    color_list = np.where(np.array(list(asymmetry_data.values())) > 0, '#2986EB', '#EB6963')
    fig = px.bar(x=list(asymmetry_data.values()), y=list(asymmetry_data.keys()), orientation='h')
    fig.update_layout(title_text="Pressure Asymmetry",
                    xaxis_title="Left - Right",
                    yaxis_title="Part of seat",
                    xaxis=dict(range=[-512, 512]),
                    showlegend=False)
    fig.update_traces(marker_color=color_list)
    return fig

def create_bar_graph(data) -> go.Figure:
    """
    Creates a bar graph with the pressure data.
    """
    if LOWRAM:
        return None

    fig = go.Figure()
    fig.add_trace(go.Bar(x=data.columns, y=data.row(0), name='Pressure'))
    fig.update_layout(title_text="Pressure Data",
                    xaxis_title="Sensor",
                    yaxis_title="Pressure",
                    yaxis_range=[0, 4096],
                    showlegend=True)
    return fig

def create_line_graph(data) -> go.Figure:
    """
    Creates a line graph with the pressure data
    along the time.
    """
    limit = 50
    
    # If there's new data
    if data.shape[0] > 0:
        # Save the data in the history
        if len(data_history) == 0:
            for key in data.columns:
                data_history[key] = []
            data_history['time'] = []
        for key in data.columns:
            data_history[key].append(data[key][0])
        data_history['time'].append(datetime.datetime.now())
        
        # If the history is too long, remove the first elements
        if len(data_history['time']) > limit:
            for key in data_history.keys():
                data_history[key] = data_history[key].pop(0)

    # Create the figure
    fig = go.Figure()
    for key in data_history.keys():
        if key != 'time':
            fig.add_trace(go.Scatter(x=data_history['time'], y=data_history[key], name=key))

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
            html.P("Debug text", id="debugText", className="debugText"),
            dcc.Graph(id="realTimeUnbalanceGraph"),
            dcc.Graph(id="realTimeBarGraph"),
            dcc.Graph(id="HistoryLineGraph"),
            dcc.Interval(id='realTimeGraphsInterval', interval=2000, n_intervals=0)
        ], width=8, style={"textAlign": "center", "align-content": "center"}),
    ]),
])

# ===== Callbacks ===== #
@app.callback(Output('debugText', 'children'),
              Output('realTimeUnbalanceGraph', 'figure'),
              Output('realTimeBarGraph', 'figure'),
              Output('HistoryLineGraph', 'figure'),
              Input('realTimeGraphsInterval', 'n_intervals'))
def update_real_time_graphs(n):
    state, data = predictor.get_current_data()
    
    if data.shape[0] == 0:
        return state, go.Figure(), go.Figure(), create_line_graph(data)

    unbalance_graph = create_unbalance_graph(data)
    bar_graph = create_bar_graph(data)
    line_graph = create_line_graph(data)

    return state, unbalance_graph, bar_graph, line_graph
