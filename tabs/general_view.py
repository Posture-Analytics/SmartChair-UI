from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
import numpy as np
import polars as pl
import pandas as pd
from modules import predictor

# ===== Helper functions ===== #
def create_posture_quality_graph(state):
    state = np.array(state)
    value_counts = np.unique(state, return_counts=True)
    fig = px.pie(values=value_counts[1], names=value_counts[0], color=value_counts[0])
    fig.update_layout(title_text="Percentage of time spent in each posture")

    return fig

def create_time_seated_graph(state, data):
    state = pd.Series(state)
    data_pd = data.to_pandas()
    data_pd['state'] = state
    fig = px.histogram(data_pd, x="index", color="state")
    fig.update_layout(title_text="Posture balance over time")

    return fig

def create_posture_balance_graph(data):
    return go.Figure()

def create_graphs():
    day, state, data = predictor.get_last_active_day_data()
    posture_quality_graph = create_posture_quality_graph(state)
    posture_balance_graph = create_posture_balance_graph(data)
    time_seated_graph = create_time_seated_graph(state, data)

    day = day.strftime("%d/%m")
    return day, posture_quality_graph, posture_balance_graph, time_seated_graph

# ===== Variables ===== #
day, posture_quality_graph, posture_balance_graph, time_seated_graph = create_graphs()

# ===== Base layout ===== #
layout = html.Div([
    dbc.Row(justify="center", children=[
        dbc.Col([
            html.H2("General View", className="tabTitle"),
            dcc.Markdown(f"**{day}**", id="dateText", className="boldText"), 

            # Graphs
            html.H2("Time Seated"),
            dcc.Graph(id="timeSeatedGraph", figure=time_seated_graph),

            html.Br(),
            html.H2("Posture Quality"),
            dcc.Graph(id="postureQualityGraph", figure=posture_quality_graph),
            dcc.Graph(id="postureBalanceGraph", figure=posture_balance_graph),
        ], width=8, style={"textAlign": "center", "align-content": "center"}),
    ]),
])

