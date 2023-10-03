import dash_bootstrap_components as dbc
import pandas as pd

from dash import dcc, html

from modules.base_app import app, DEBUG_STATE
from modules import database_manager, predictor

model = predictor.get_model()

# Base layout
layout = dbc.Row([
        # Posture Evaluation
        dbc.Col([
            dcc.Markdown("On the day **26/04**, your posture was:", id="dateText"),
            html.Div("Good.", className="appear", id="postureText"),
            html.Div("Or 74% correct.", className="appear", id="percentageText"),
            dbc.Row([
                dbc.Col(["Tip: Standing up every 50 minutes improves blood circulation in the lower limbs."],
                        className="appear", width=8)
            ]),
        ], width=8),
        # Alerts
        dbc.Col(class_name="panel", children=[
            html.Div("⚠ Alerts:", className="appear", id="alertsTitle"),
            dcc.Markdown("You remained sitting for more than **2 hours**.", className="appear", id="alertsBody"),
        ]),
    ])

def make_layout(day: str, posture_quality: str, percent: int, tip: str, alerts: list[str]) -> dbc.Row:
    # Alerts
    alerts_list = [html.Div("⚠ Alerts:", className="appear", id="alertsTitle")]
    for alert in alerts:
        alerts_list.append(dcc.Markdown(alert, className="appear", id="alertsBody"))
    if len(alerts_list) == 1:
        alerts_list.append(dcc.Markdown("*No alerts.*", className="appear", id="alertsBody"))
    return dbc.Row([
        dbc.Col([
            dcc.Markdown(f"On the day **{day}**, your posture was:", id="dateText"),
            html.Div(posture_quality, className="appear", id="postureText"),
            html.Div(f"Or {percent}% correct.", className="appear", id="percentageText"),
            dbc.Row([
                dbc.Col(tip, className="appear", width=8)
            ]),
        ], width=8),
        dbc.Col(class_name="panel", children=alerts_list),
    ])

def get_layout() -> dbc.Row:
    last_day, last_day_data = database_manager.get_last_active_day_data()

    day = last_day.strftime("%d/%m")

    last_day_data = last_day_data.drop("index")
    evaluated_postures = model.predict(last_day_data.rows(named=False))
    try:
        percent = int((evaluated_postures == "Sitting Correctly").sum() / len(evaluated_postures) * 100)
        if percent < 50:
            posture_quality = "Bad."
            tip = "Tip: Standing up every 50 minutes improves blood circulation in the lower limbs."
        elif percent < 65:
            posture_quality = "Regular."
            tip = "Tip: Standing up every 50 minutes improves blood circulation in the lower limbs."
        elif percent < 80:
            posture_quality = "Good."
            tip = "Tip: Standing up every 50 minutes improves blood circulation in the lower limbs."
        elif percent < 95:
            posture_quality = "Great."
            tip = "Tip: Standing up every 50 minutes improves blood circulation in the lower limbs."
        else:
            posture_quality = "Perfect."
            tip = "Congratulations! You are sitting correctly."
    except:
        posture_quality = "Unexpected data."
        percent = 0
        tip = "Tip: Standing up every 50 minutes improves blood circulation in the lower limbs."
    alerts = []

    return make_layout(day, posture_quality, percent, tip, alerts)
