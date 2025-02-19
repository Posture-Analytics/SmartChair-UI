import dash
import dash_bootstrap_components as dbc

from dash import html

external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    "https://fonts.googleapis.com/css2?family=Readex+Pro&display=swap"
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, use_pages=True, update_title=None)
app.title = "SmartChair"

app.layout = html.Div([
    html.H1("SmartChair"),
    dash.page_container
])


if __name__ == "__main__":
    app.run(debug=True)
