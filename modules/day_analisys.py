from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from modules.base_app import app, DEBUG_STATE
from modules import database_manager, predictor
import polars as pl
import pandas as pd
import numpy as np

model = predictor.get_model()

# Base layout
layout = dbc.Row([
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
    ])

def make_layout(day, posture_quality, percent, tip, alerts):
    # Alerts
    alerts_list = [html.Div("⚠ Alertas:", className="appear", id="alertsTitle")]
    for alert in alerts:
        alerts_list.append(dcc.Markdown(alert, className="appear", id="alertsBody"))
    return dbc.Row([
        dbc.Col([
            dcc.Markdown(f"No dia **{day}**, a sua postura foi:", id="dateText"),
            html.Div(posture_quality, className="appear", id="postureText"),
            html.Div(f"Ou {percent}% correta.", className="appear", id="percentageText"),
            html.Div(tip, className="appear", id="tipText"),
        ], width=8),
        dbc.Col(class_name="panel", children=alerts_list),
    ])

def get_layout():
    last_day, last_day_data = database_manager.get_last_active_day_data()

    day = last_day.strftime("%d/%m")

    last_day_data = last_day_data.drop("index")
    evaluated_postures = model.predict(last_day_data.rows(named=False))
    evaluated_postures = pd.Series(evaluated_postures)
    percent = int(evaluated_postures.value_counts(normalize=True)["Sitting Correctly"] * 100)
    if percent < 50:
        posture_quality = "Ruim."
        tip = "Dica: Levantar-se a cada 50 minutos melhora a circulação sanguínea nos membros inferiores."
    elif percent < 65:
        posture_quality = "Razoável."
        tip = "Dica: Levantar-se a cada 50 minutos melhora a circulação sanguínea nos membros inferiores."
    elif percent < 80:
        posture_quality = "Boa."
        tip = "Dica: Levantar-se a cada 50 minutos melhora a circulação sanguínea nos membros inferiores."
    elif percent < 95:
        posture_quality = "Ótima."
        tip = "Dica: Levantar-se a cada 50 minutos melhora a circulação sanguínea nos membros inferiores."
    else:
        posture_quality = "Perfeita."
        tip = "Parabéns! Você está se sentando corretamente."
    alerts = []

    return make_layout(day, posture_quality, percent, tip, alerts)