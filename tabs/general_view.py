from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from modules import predictor

# ===== Helper functions ===== #
def create_posture_quality_graph(state):
    pass

def create_posture_balance_graph(data):
    pass

def create_graphs():
    day, state, data = predictor.get_last_active_day_data()
    posture_quality_graph = create_posture_quality_graph(state)
    posture_balance_graph = create_posture_balance_graph(data)

    return day, posture_quality_graph, posture_balance_graph

# ===== Variables ===== #
day, posture_quality_graph, posture_balance_graph = create_graphs()

# ===== Base layout ===== #
layout = html.Div([
    dbc.Row(justify="center", children=[
        dbc.Col([
            html.H2("General View", className="tabTitle"),
            html.P(day, id="dateText"),

            # Graphs
            html.H2("Time Seated"),
            dcc.Graph(id="timeSeatedGraph"),

            html.Br(),
            html.H2("Posture Quality"),
            dcc.Graph(id="postureQualityGraph", figure=posture_quality_graph),
            dcc.Graph(id="postureBalanceGraph", figure=posture_balance_graph),
        ], width=8, style={"textAlign": "center", "align-content": "center"}),
    ]),
])

