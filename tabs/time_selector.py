from dash import Dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from datetime import date, datetime

from modules import database_manager

layout = html.Div([
    dbc.Row(justify="evenly", children=[
        dbc.Col([
            html.H3("Time Selector"),
            dcc.DatePickerSingle(
                id='dateSelector',
                min_date_allowed=date(2022, 1, 1),
                max_date_allowed=date(2023, 12, 31),
                date=date(2023, 2, 22),
                display_format="DD/MM/YYYY",
            ),
            html.Button("Select", id="dateSelectorButton"),
        ], width=2),
        dbc.Col([
            html.H3("Selected Date"),
            html.Div(id="dateSelectText", children="No date selected.", className="appear"),
            html.Button("Download CSV", id="downloadButton"),
            dcc.Download(id="downloadData")
        ], width=2)
    ])
])

def define_app_callbacks(app):
    @app.callback(Output("dateSelectText", "children"),
              Input("dateSelector", "date"),
              Input("dateSelectorButton", "n_clicks"))
    def update_date_text(date, n_clicks):
        if n_clicks is not None:
            global data

            data = database_manager.get_data_from_day(date)
            if date is not None:
                return f"{data.shape[0]} rows selected."
            else:
                return "No date selected."
    
    @app.callback(Output("downloadData", "data"),
                  Input("downloadButton", "n_clicks"))
    def download_csv(n_clicks):
        if n_clicks is not None:
            global data

            data.write_csv("data.csv")
            return dcc.send_file("data.csv")