import dash
from dash import dcc, html
import login_manager

dash.register_page(__name__, path='/create-account')

layout = html.Div([
    html.H3("Create Account"),
    dcc.Input(id="name", placeholder="Name"),
    dcc.Input(id="email", placeholder="Email"),
    dcc.Input(id="birthday", placeholder="Birthday (DD/MM/YYYY)", type="text"),
    dcc.Input(id="weight", placeholder="Weight", type="number", step=0.1, min=0),
    dcc.Input(id="password", placeholder="Password", type="password"),
    dcc.Input(id="confirm-password", placeholder="Confirm Password", type="password"),
    html.Button("Create Account", id="create-account-button", className="btn btn-primary"),
    dcc.Link(
        html.Button("Continue", id="continue-button", className="btn btn-primary", disabled=True),
        href="/train-model",
    ),
    html.Br(),
    html.A("Or login", href="/login"),
])

@dash.callback(
    dash.Output("create-account-button", "disabled"),
    dash.Input("name", "value"),
    dash.Input("email", "value"),
    dash.Input("birthday", "value"),
    dash.Input("weight", "value"),
    dash.Input("password", "value"),
    dash.Input("confirm-password", "value"),
)
def disable_create_account_button(name, email, birthday, weight, password, confirm_password):
    return name is None or email is None or birthday is None or weight is None or password is None or confirm_password is None or name == "" or email == "" or password == "" or confirm_password == "" or password != confirm_password

@dash.callback(
    dash.Output("continue-button", "disabled"),
    dash.Input("create-account-button", "n_clicks"),
    dash.State("name", "value"),
    dash.State("email", "value"),
    dash.State("birthday", "value"),
    dash.State("weight", "value"),
    dash.State("password", "value"),
    dash.State("confirm-password", "value"),
)
def create_account(n_clicks, name, email, birthday, weight, password, confirm_password):
    if n_clicks is None:
        return True
    data = {
        "name": name,
        "email": email,
        "birthday": birthday,
        "weight": weight,
    }
    if login_manager.register(email, password, data):
        print("Registered successfully")
        return False

    else:
        print("Failed to register")
        return True
