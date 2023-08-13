import dash
from dash import dcc, html, Input, Output, State
import login_manager

dash.register_page(__name__, path='/login')

layout = html.Div([
    html.H3("Login"),
    dcc.Input(id="email", placeholder="Email", type="email"),
    dcc.Input(id="password", placeholder="Password", type="password"),
    html.Button("Login", id="login-button", className="btn btn-primary"),
    html.Br(),
    html.A("Or create a new account", href="/create-account"),
])

@dash.callback(
    Output("login-button", "disabled"),
    Input("email", "value"),
    Input("password", "value"),
)
def disable_login_button(email, password):
    return email is None or password is None or email == "" or password == ""

@dash.callback(
    Output("login-button", "n_clicks"),
    Input("login-button", "n_clicks"),
    State("email", "value"),
    State("password", "value"),
)
def login(n_clicks, email, password):
    if n_clicks is None:
        return 0
    if login_manager.login(email, password):
        print("Logged in successfully")
    else:
        print("Failed to log in")
    return n_clicks
