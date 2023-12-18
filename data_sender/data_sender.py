import dash_bootstrap_components as dbc
import firebase_admin

from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from datetime import datetime, date
from firebase_admin import db
from firebase_admin import credentials

# ===== Firebase ===== #
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin = firebase_admin.initialize_app(cred, {"databaseURL": "https://friendly-bazaar-334818-default-rtdb.firebaseio.com"})

root_ref = db.reference("/fake_data_base64/")

# ===== Data Types ===== #
data_types = {
    "correct_posture": "~PZAZAZAZAZAZAZAZAZAZAZAZA",
    "leaning_forward": "~PAAAAAAAAAAAA0A0AZAZANANA",
    "leaning_backward": "~P0A0A0A0AAAAAAAAA0A0A0A0A",
    "unbalanced_posture": "~P0AAA0AAA0AAA0AAA0AAA0AAA",
    "not_sitting": "~PAAAAAAAAAAAAAAAAAAAAAAAA"
}

# ===== App ===== #
app = Dash(__name__, title = "SmartChair - Data Sender", external_stylesheets=[dbc.themes.LITERA], update_title=None)
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
                {"label": "Correct Posture", "value": "correct_posture"},
                {"label": "Leaning Forward", "value": "leaning_forward"},
                {"label": "Relaxed Posture", "value": "relaxed_posture"},
                {"label": "Unbalanced Posture", "value": "unbalanced_posture"},
                {"label": "Not Sitting", "value": "not_sitting"}
            ],
            value="correct_posture", style={"width":"100%"}
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
def send_data_callback(n_clicks: int, dataType: str, n_intervals: int) -> str:
    if n_clicks is None or n_clicks % 2 == 0:
        return "", "Send Data", "btn btn-lg btn-primary"
    else:
        # Get current time
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        # Send data
        date_ = date.today().strftime("%Y-%m-%d")
        timestamp = str(timestamp).replace(".", "")[:13]
        root_ref.child(date_).child(timestamp).set(
            data_types[dataType]
        )
        return f"Data {n_intervals} sent at {now.strftime('%H:%M:%S')}", "Stop Sending Data", "btn btn-lg btn-danger"

@app.callback(
    Output("dataToBeSentCard", "children"),
    Input("dataTypeDropdown", "value")
)
def update_data_to_be_sent_card(dataType: str) -> list[html.Div]:
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
        case "leaning_backward":
            return [
                html.Div(className="card-header", children=["Data to be sent"]),
                html.Div(className="card-body", children=[
                    html.H5(className="card-title", children=["Leaning Backward"]),
                    html.P(className="card-text", children=[str(data_types["leaning_backward"])])
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
