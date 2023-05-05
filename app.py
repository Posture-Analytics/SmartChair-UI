from dash import Dash
from dash import dcc, html
import dash_bootstrap_components as dbc

external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    "https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap"
]

app = Dash(__name__, external_stylesheets=external_stylesheets, update_title=None)
app.title = 'SmartChair'

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
    dcc.Tabs([
        dcc.Tab(label="Visão Geral", className="tab"),
        dcc.Tab(label="Dados Analíticos", className="tab"),
        dcc.Tab(label="Selecionador de Tempo", className="tab")
    ]),
    html.Div(id="panelGraph")
])

if __name__ == '__main__':
    app.run_server(debug=True)