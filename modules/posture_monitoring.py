from dash import Dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from modules.base_app import app, DEBUG_STATE
import random

# Base layout
layout = html.Div(className="panel monitorPanel", children=[
    html.Div(["Você está usando a cadeira e sentado "], className="postureMonitorText"),
    html.Div(["corretamente"], className="postureMonitorText correct"),
    html.Div(["."], className="postureMonitorText"),
    dcc.Interval(id='postureMonitorInterval', interval=500, n_intervals=0)
])

@app.callback(Output('postureMonitorContainer', 'children'),
                Input('postureMonitorInterval', 'n_intervals'))
def update_posture_monitor(n):
    if DEBUG_STATE:
        state = ['correto', 'curvado', 'desbalanceado', 'sem uso'][random.randint(0, 3)]
    match state:
        case 'correto':
            return html.Div(className="panel monitorPanel", children=[
                html.Div(["Você está usando a cadeira e sentado "], className="postureMonitorText"),
                html.Div(["corretamente"], className="postureMonitorText correct"),
                html.Div(["."], className="postureMonitorText"),
                dcc.Interval(id='postureMonitorInterval', interval=500, n_intervals=0)
            ])
        case 'curvado':
            return html.Div(className="panel monitorPanel", children=[
                html.Div(["Você está usando a cadeira e sentado "], className="postureMonitorText"),
                html.Div(["de maneira curvada"], className="postureMonitorText incorrect"),
                html.Div(["."], className="postureMonitorText"),
                dcc.Interval(id='postureMonitorInterval', interval=500, n_intervals=0)
            ])
        case 'desbalanceado':
            return html.Div(className="panel monitorPanel", children=[
                html.Div(["Você está usando a cadeira e sentado "], className="postureMonitorText"),
                html.Div(["de maneira desbalanceada"], className="postureMonitorText incorrect"),
                html.Div(["."], className="postureMonitorText"),
                dcc.Interval(id='postureMonitorInterval', interval=500, n_intervals=0)
            ])
        case 'sem uso':
            return dcc.Interval(id='postureMonitorInterval', interval=500, n_intervals=0)
