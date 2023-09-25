import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from dash import dcc, html
from plotly.subplots import make_subplots


from modules import predictor

# ===== Helper functions ===== #
def create_posture_quality_graph(state):
    state = np.array(state)
    value_counts = np.unique(state, return_counts=True)
    fig = px.pie(values=value_counts[1], names=value_counts[0], color=value_counts[0])
    fig.update_layout(title_text="Percentage of time spent in each posture")

    return fig

def create_time_seated_graph(state, data):
    state = pd.Series(state)
    data_pd = data.to_pandas()
    data_pd["state"] = state
    fig = px.histogram(data_pd, x="index", color="state")
    fig.update_layout(title_text="Posture balance over time")

    return fig

def create_posture_balance_graph(state, data):
    MARKER_SIZE = 0.3
    fig = go.Figure()

    # Calculate horizontal balance
    total = data.sum()

    right = 0
    left = 0
    for i in range(11):
        if i % 2 == 0:
            right += total[f"p{str(i).zfill(2)}"][0]
        else:
            left += total[f"p{str(i).zfill(2)}"][0]

    boundary = max(right, left)
    h_balance = (right - left) / boundary

    # calculate vertical balance
    counts = np.unique(state, return_counts=True)
    forward = counts[1][counts[0] == "Leaning Forward"]
    backward = counts[1][counts[0] == "Leaning Backward"]
    neutral = counts[1][counts[0] == "Sitting Correctly"]

    if len(forward) == 0:
        forward = 0
    else:
        forward = forward[0]
    if len(backward) == 0:
        backward = 0
    else:
        backward = backward[0]
    if len(neutral) == 0:
        neutral = 0
    else:
        neutral = neutral[0]

    boundary = max(forward, backward, neutral)
    v_balance = (forward - backward) / boundary

    # Horizontal balance
    # Line
    fig.add_shape(type="line",
    x0=-2, y0=0, x1=2, y1=0,
    line=dict(color="LightSlateGray", width=3)
    )
    # Middle line
    fig.add_shape(type="line",
    x0= 0, y0=-MARKER_SIZE/2,
    x1= 0, y1= MARKER_SIZE/2,
    line=dict(color="LightSlateGray", width=3)
    )
    # Marker
    fig.add_shape(type="circle",
    x0= h_balance * 2 - MARKER_SIZE/2, y0=-MARKER_SIZE/2,
    x1= h_balance * 2 + MARKER_SIZE/2, y1= MARKER_SIZE/2,
    fillcolor="DarkSlateGray", line_color="DarkSlateGray")
    # Ttext
    fig.add_annotation(
    x=0, y=0.5,
    text="Horizontal Balance",
    showarrow=False,
    align="center"
    )
    # Text value
    fig.add_annotation(
    x=0, y=-0.5,
    text= str(round(h_balance, 2)),
    showarrow=False,
    align="center"
    )

    # Vertical balance
    # Line
    fig.add_shape(type="line",
    x0=4, y0=-1, x1=4, y1=1,
    line=dict(color="LightSlateGray",width=3)
    )
    # Middle line
    fig.add_shape(type="line",
    x0=4 - MARKER_SIZE/2, y0=0, x1=4 + MARKER_SIZE/2, y1=0,
    line=dict(color="LightSlateGray",width=3)
    )
    # Mmarker
    fig.add_shape(type="circle",
    x0=4 - MARKER_SIZE/2, y0= v_balance - MARKER_SIZE/2,
    x1=4 + MARKER_SIZE/2, y1= v_balance + MARKER_SIZE/2,
    fillcolor="DarkSlateGray", line_color="DarkSlateGray")
    # Text
    fig.add_annotation(
    x=4, y=1.5,
    text="Vertical Balance",
    showarrow=False,
    align="center"
    )
    # Text value
    fig.add_annotation(
    x=4, y=-1.5,
    text= str(round(v_balance, 2)),
    showarrow=False,
    align="center"
    )

    # Update layout
    fig.update_layout(
    title="Posture Balance",
    xaxis_range=[-4, 8],
    yaxis_range=[-2, 2],
    width=800,
    height=400,
    template="plotly_white",
    xaxis_showgrid=False,
    yaxis_showgrid=False,
    xaxis_visible=False,
    yaxis_visible=False,
    )

    return fig

def create_graphs() -> tuple[str, go.Figure, go.Figure, go.Figure]:
    day, state, data = predictor.get_last_active_day_data()
    posture_quality_graph = create_posture_quality_graph(state)
    time_seated_graph = create_time_seated_graph(state, data)
    posture_balance_graph = create_posture_balance_graph(state, data)

    day = day.strftime("%d/%m")
    return day, posture_quality_graph, posture_balance_graph, time_seated_graph

# ===== Variables ===== #
day, posture_quality_graph, posture_balance_graph, time_seated_graph = create_graphs()

# ===== Base layout ===== #
layout = html.Div([
    dbc.Row(justify="center", children=[
        dbc.Col([
            html.H2("General View", className="tabTitle"),
            dcc.Markdown(f"**{day}**", id="dateText", className="boldText"), 

            # Graphs
            html.H2("Time Seated"),
            dcc.Graph(id="timeSeatedGraph", figure=time_seated_graph),

            html.Br(),
            html.H2("Posture Quality"),
            dcc.Graph(id="postureQualityGraph", figure=posture_quality_graph),
            dcc.Graph(id="postureBalanceGraph", figure=posture_balance_graph),
        ], width=8, style={"textAlign": "center", "align-content": "center"}),
    ]),
])

