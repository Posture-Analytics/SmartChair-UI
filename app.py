import dash
import dash_bootstrap_components as dbc

from dash import dcc, html
from dash.dependencies import Input, Output

from modules import day_analysis, posture_monitoring
from modules.base_app import app, DEBUG_STATE
from tabs import realtime_data, time_selector, general_view

external_stylesheets = [
    dbc.themes.LITERA,
    "https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap"
]

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
    # Posture Monitoring Stats
    html.Div(id="postureMonitorContainer", children=[
        posture_monitoring.layout
    ]),
    day_analysis.get_layout(),
    html.Div(className="separator"),
    dcc.Tabs(id="tabsSelector", children=[
        dcc.Tab(label="General View", className="tab", value="General View"),
        dcc.Tab(label="Real Time Data", className="tab", value="Real Time Data"),
        dcc.Tab(label="Time Selector", className="tab", value="Time Selector")
    ]),
    html.Div(id="panelGraph", children=[
        html.Div(id="tabContent")
    ]),
    html.Div([
            html.Div(
                dcc.Link(
                    f"{page['name']} - {page['path']}", href=page["relative_path"]
                )
            )
            for page in dash.page_registry.values()
        ]),
])

@app.callback(Output("tabContent", "children"),
              Input("tabsSelector", "value"))
def render_content(tab: str) -> html.Div | None:
    match tab:
        case "General View":
            return general_view.layout
        case "Real Time Data":
            return realtime_data.layout
        case "Time Selector":
            return time_selector.layout
    return None

if __name__ == "__main__":
    app.run_server(debug=DEBUG_STATE, port=8000)
