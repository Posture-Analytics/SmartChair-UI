from dash import Dash
import dash_bootstrap_components as dbc


DEBUG_STATE = True
external_stylesheets = [
    dbc.themes.LITERA,
    "https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap"
]
app = Dash(__name__, external_stylesheets=external_stylesheets, update_title=None, suppress_callback_exceptions=True)
app.title = 'SmartChair'




