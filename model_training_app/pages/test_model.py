import dash
from dash import dcc, html, Input, Output, State
import login_manager
import pickle
import database_manager
import polars as pl

model = None

dash.register_page(__name__, path='/test-model', redirect_from=['/login'])

layout = html.Div([
    html.H3("Login"),
    dcc.Input(id="email", placeholder="Email", type="email"),
    html.Button("Login", id="login-button", className="btn btn-primary"),
    html.P(id="text"),
    html.Br(),
    html.A("Or create a new account", href="/create-account"),
    html.Br(),
    html.Br(),
    html.Div(id="PredictionCardDiv"),
    dcc.Interval(id="interval", interval=500, n_intervals=0),
])

@dash.callback(
    Output("login-button", "disabled"),
    Input("email", "value"),
)
def disable_login_button(email):
    return email is None or email == ""

@dash.callback(
    Output("text", "children"),
    Input("login-button", "n_clicks"),
    State("email", "value"),
)
def login(n_clicks, email):
    global model 

    if n_clicks is None:
        return ""
    user_id = login_manager.login(email)

    with open(f"model_training_app/models/model_{user_id}.pkl", "rb") as f:
        model = pickle.load(f)
    
    return f"Logged in as {email}."

@dash.callback(
    Output("PredictionCardDiv", "children"),
    Input("interval", "n_intervals"),
)
def predict(n_intervals):
    global model

    if model is None:
        return html.Div(className="card text-white bg-secondary mb-3", children=[
            html.Div(className="card-header", children="Model Prediction"),
            html.Div(className="card-body", children=[
                html.H5(className="card-title", children="No prediction yet"),
                html.P(className="card-text", children="Login to see the model prediction.")
            ])
        ], id="PredictionCard", style={"width":"100%"})

    data = database_manager.get_current_data()

    if data.shape[0] == 0:
        return html.Div(className="card text-white bg-secondary mb-3", children=[
            html.Div(className="card-header", children="Model Prediction"),
            html.Div(className="card-body", children=[
                html.H5(className="card-title", children="No prediction yet"),
                html.P(className="card-text", children="No data available yet.")
            ])
        ], id="PredictionCard", style={"width":"100%"})

    data = data.drop("index")
    data = data.rows(named=False)
    prediction = model.predict(data)
    
    return html.Div(className="card text-white bg-primary mb-3", children=[
            html.Div(className="card-header", children="Model Prediction"),
            html.Div(className="card-body", children=[
                html.H5(className="card-title", children=f"Prediction: {prediction}"),
                html.P(className="card-text", children="This is what your trained model predicted.")
            ])
        ], id="PredictionCard", style={"width":"100%"})

