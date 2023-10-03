import dash
from dash import Dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import polars as pl
from modules.base_app import app, DEBUG_STATE

from tabs import realtime_data

# ===== Base App ===== #

# ===== App ===== #

app.layout = html.Div([
    # Header
    dbc.Row(className="header", justify="between", children=[
        dbc.Col([
            html.H3("SmartChair", className="headerElement", id="title"),
        ], width=2)
    ]),

    # Tabs
    html.Div(id="panelGraph", children=[
        realtime_data.layout
    ])
])

if __name__ == '__main__':
    app.run_server(debug=DEBUG_STATE, port=8000)