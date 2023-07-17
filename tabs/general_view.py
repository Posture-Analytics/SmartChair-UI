from dash import Dash
from dash import dcc, html
import dash_bootstrap_components as dbc

# ===== Layout ===== #
layout = html.Div([
    dbc.Row(justify="center", children=[
        dbc.Col([
            html.H2("General View", className="tabTitle"),
            html.P("14/07", id="dateText"),

            # Graphs
            html.H2("Time Seated"),
            dcc.Graph(id="timeSeatedGraph"),

            html.Br(),
            html.H2("Posture Quality"),
            dcc.Graph(id="postureQualityGraph"),
            dcc.Graph(id="postureBalanceGraph")
        ], width=8, style={"textAlign": "center", "align-content": "center"}),
    ]),
])