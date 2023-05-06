from dash import Dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import polars as pl

# external tabs
from tabs import time_selector, general_view, analytic_data

external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    "https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap"
]

app = Dash(__name__, external_stylesheets=external_stylesheets, update_title=None, suppress_callback_exceptions=True)
app.title = 'SmartChair'
data = pl.DataFrame()

app.layout = html.Div([
    # Header
    dbc.Row(className="header", justify="between", children=[
        dbc.Col([
            html.H3("SmartChair", className="headerElement", id="title"),
        ], width=2),
        dbc.Col(className="alignRight", children=[
            html.A("Luís Fernando Laguardia", className="headerElement", id="username"),
            html.Img(src="https://yt3.googleusercontent.com/XzyXdpLZBe2Mci_xqo2h-UynYktaAXL4FNdoPL_jAWJn16aiHkiilmYxqaOP6AANFQno4RBn=s176-c-k-c0x00ffffff-no-rj", className="headerElement", id="profilePic"),
        ], width=3)
    ]),
    dbc.Row([
        # Posture Evaluation
        dbc.Col([
            dcc.Markdown("No dia **26/04**, a sua postura foi:", id="dateText"),
            html.Div("Boa.", className="appear", id="postureText"),
            html.Div("Ou 74% correta.", className="appear", id="percentageText"),
            html.Div("Dica: Levantar-se a cada 50 minutos melhora a circulação sanguínea nos membros inferiores.", className="appear", id="tipText"),
        ], width=8),
        # Alerts
        dbc.Col(class_name="panel", children=[
            html.Div("⚠ Alertas:", className="appear", id="alertsTitle"),
            dcc.Markdown("Você passou mais de **2 horas sentado** sem se levantar.", className="appear", id="alertsBody"),
        ]),
    ]),
    html.Div(className="separator"),
    dcc.Tabs(id="tabsSelector", children=[
        dcc.Tab(label="General View", className="tab", value="General View"),
        dcc.Tab(label="Analytic Data", className="tab", value="Analytic Data"),
        dcc.Tab(label="Time Selector", className="tab", value="Time Selector")
    ]),
    html.Div(id="panelGraph", children=[
        html.Div(id="tabContent")
    ])
])

@app.callback(Output('tabContent', 'children'),
              Input('tabsSelector', 'value'))
def render_content(tab):
    match tab:
        case "General View":
            return general_view.layout
        case "Analytic Data":
            return analytic_data.layout
        case "Time Selector":
            return time_selector.layout

if __name__ == '__main__':
    time_selector.define_app_callbacks(app)
    app.run_server(debug=True)