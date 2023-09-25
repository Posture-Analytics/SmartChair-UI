import dash_bootstrap_components as dbc

from dash import dcc, html
from dash.dependencies import Input, Output

from modules.base_app import app
from modules import predictor

# ===== Base layout ===== #
layout = html.Div(className="panel monitorPanel", children=[
    html.Div(["You are using the chair and sitting "], className="postureMonitorText"),
    html.Div(["correctly"], className="postureMonitorText correct"),
    html.Div(["."], className="postureMonitorText"),
    dcc.Interval(id="postureMonitorInterval", interval=500, n_intervals=0)
])

# ===== Callbacks ===== #
@app.callback(Output("postureMonitorContainer", "children"),
                Input("postureMonitorInterval", "n_intervals"))
def update_posture_monitor(n: int) -> dcc.Interval:
    state, _ = predictor.get_current_data()
    match state:
        case "Sitting Correctly":
            return html.Div(className="panel monitorPanel", children=[
                html.Div(["You are using the chair and sitting "], className="postureMonitorText"),
                html.Div(["correctly"], className="postureMonitorText correct"),
                html.Div(["."], className="postureMonitorText"),
                dcc.Interval(id="postureMonitorInterval", interval=1000, n_intervals=0)
            ])
        case "Leaning Forward":
            return html.Div(className="panel monitorPanel", children=[
                html.Div(["You are using the chair and sitting "], className="postureMonitorText"),
                html.Div(["leaning forward"], className="postureMonitorText incorrect"),
                html.Div(["."], className="postureMonitorText"),
                dcc.Interval(id="postureMonitorInterval", interval=1000, n_intervals=0)
            ])
        case "Leaning Backward":
            return html.Div(className="panel monitorPanel", children=[
                html.Div(["You are using the chair and sitting "], className="postureMonitorText"),
                html.Div(["leaning backwards"], className="postureMonitorText incorrect"),
                html.Div(["."], className="postureMonitorText"),
                dcc.Interval(id="postureMonitorInterval", interval=1000, n_intervals=0)
            ])
        case "Unbalanced":
            return html.Div(className="panel monitorPanel", children=[
                html.Div(["You are using the chair and sitting "], className="postureMonitorText"),
                html.Div(["in an unbalanced way"], className="postureMonitorText incorrect"),
                html.Div(["."], className="postureMonitorText"),
                dcc.Interval(id="postureMonitorInterval", interval=1000, n_intervals=0)
            ])
        case "Not Sitting":
            return dcc.Interval(id="postureMonitorInterval", interval=2000, n_intervals=0)
