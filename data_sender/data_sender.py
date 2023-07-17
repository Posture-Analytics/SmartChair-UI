# Dash
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
# Firebase
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime, timedelta, date, time

# ===== Firebase ===== #
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin = firebase_admin.initialize_app(cred, {'databaseURL': 'https://friendly-bazaar-334818-default-rtdb.firebaseio.com'})

root_ref = db.reference('/sensor_readings/')

# ===== Data Types ===== #
data_types = {
    "correct_posture": {
        "p00": 1500,
        "p01": 1500,
        "p02": 1500,
        "p03": 1500,
        "p04": 1500,
        "p05": 1500,
        "p06": 1500,
        "p07": 1500,
        "p08": 1500,
        "p09": 1500,
        "p10": 1500,
        "p11": 1500
    },
    "leaning_forward": {
        "p00": 0,
        "p01": 0,
        "p02": 0,
        "p03": 0,
        "p04": 0,
        "p05": 0,
        "p06": 3000,
        "p07": 3000,
        "p08": 3000,
        "p09": 3000,
        "p10": 3000,
        "p11": 3000
    },
    "relaxed_posture": {
        "p00": 3000,
        "p01": 3000,
        "p02": 3000,
        "p03": 3000,
        "p04": 0,
        "p05": 0,
        "p06": 0,
        "p07": 0,
        "p08": 3000,
        "p09": 3000,
        "p10": 3000,
        "p11": 3000
    },
    "unbalanced_posture": {
        "p00": 3000,
        "p01": 0,
        "p02": 3000,
        "p03": 0,
        "p04": 3000,
        "p05": 0,
        "p06": 3000,
        "p07": 0,
        "p08": 3000,
        "p09": 0,
        "p10": 3000,
        "p11": 0
    },
    "not_sitting": {
        "p00": 0,
        "p01": 0,
        "p02": 0,
        "p03": 0,
        "p04": 0,
        "p05": 0,
        "p06": 0,
        "p07": 0,
        "p08": 0,
        "p09": 0,
        "p10": 0,
        "p11": 0
    }
}

# ===== App ===== #
app = Dash(__name__, title="SmartChair - Data Sender", external_stylesheets=[dbc.themes.LITERA], update_title=None)
app.layout = dbc.Row([
    dbc.Col([
        # Title
        html.H1("SmartChair - Data Sender"),
        # Data Sender Controler
        html.Button("Send Data", id="sendDataButton", className="btn btn-lg btn-primary"),
        dcc.Interval(id="sendDataInterval", interval=500, n_intervals=0),
        # Data Sender Status
        html.Div(id="sendDataStatus"),
        html.Br(),
        # Type of Data
        html.Div("Type of Data", style={"margin":"1rem"}),
        dcc.Dropdown(
            id="dataTypeDropdown",
            options=[
                {'label': 'Correct Posture', 'value': 'correct_posture'},
                {'label': 'Leaning Forward', 'value': 'leaning_forward'},
                {'label': 'Relaxed Posture', 'value': 'relaxed_posture'},
                {'label': 'Unbalanced Posture', 'value': 'unbalanced_posture'},
                {'label': 'Not Sitting', 'value': 'not_sitting'}
            ],
            value='correct_posture', style={"width":"100%"}
        ),
        html.Br(),
        html.Div(className="card text-white bg-primary mb-3", children=[
            html.Div(className="card-header", children=["Data to be sent"]),
            html.Div(className="card-body", children=[
                html.H5(className="card-title", children=["Correct Posture"]),
                html.P(className="card-text", children=["The user is sitting correctly."])
            ])
        ], id="dataToBeSentCard", style={"width":"100%"}),
    ], width=8, style={"margin":"2rem", "display":"flex", "flex-direction":"column", "align-items":"center"})], justify="center"
)

@app.callback(
    [Output("sendDataStatus", "children"),
     Output("sendDataButton", "children"),
     Output("sendDataButton", "className")],
    Input("sendDataButton", "n_clicks"),
    Input("dataTypeDropdown", "value"),
    Input("sendDataInterval", "n_intervals")
)
def send_data_callback(n_clicks, dataType, n_intervals):
    if n_clicks is None or n_clicks % 2 == 0:
        return "", "Send Data", "btn btn-lg btn-primary"
    else:
        # Get current time
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        # Send data
        date_ = date.today().strftime("%Y-%m-%d")
        timestamp = str(timestamp).replace('.', '_')[:14]
        root_ref.child(date_).child(timestamp).set(
            data_types[dataType]
        )
        return f"Data {n_intervals} sent at {now.strftime('%H:%M:%S')}", "Stop Sending Data", "btn btn-lg btn-danger"
    

@app.callback(
    Output("dataToBeSentCard", "children"),
    Input("dataTypeDropdown", "value")
)
def update_data_to_be_sent_card(dataType):
    match dataType:
        case "correct_posture":
            return [
                html.Div(className="card-header", children=["Data to be sent"]),
                html.Div(className="card-body", children=[
                    html.H5(className="card-title", children=["Correct Posture"]),
                    html.P(className="card-text", children=[str(data_types["correct_posture"])])
                ])
            ]
        case "leaning_forward":
            return [
                html.Div(className="card-header", children=["Data to be sent"]),
                html.Div(className="card-body", children=[
                    html.H5(className="card-title", children=["Leaning Forward"]),
                    html.P(className="card-text", children=[str(data_types["leaning_forward"])])
                ])
            ]
        case "relaxed_posture":
            return [
                html.Div(className="card-header", children=["Data to be sent"]),
                html.Div(className="card-body", children=[
                    html.H5(className="card-title", children=["Relaxed Posture"]),
                    html.P(className="card-text", children=[str(data_types["relaxed_posture"])])
                ])
            ]
        case "unbalanced_posture":
            return [
                html.Div(className="card-header", children=["Data to be sent"]),
                html.Div(className="card-body", children=[
                    html.H5(className="card-title", children=["Unbalanced Posture"]),
                    html.P(className="card-text", children=[str(data_types["unbalanced_posture"])])
                ])
            ]
        case "not_sitting":
            return [
                html.Div(className="card-header", children=["Data to be sent"]),
                html.Div(className="card-body", children=[
                    html.H5(className="card-title", children=["Not Sitting"]),
                    html.P(className="card-text", children=[str(data_types["not_sitting"])])
                ])
            ]
# ===== Run ===== #
if __name__ == "__main__":
    app.run(debug=True, port=8080)
