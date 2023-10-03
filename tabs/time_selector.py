import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import polars as pl

from dash import dcc, html
from dash.dependencies import Input, Output, State
from datetime import date, datetime
from plotly.subplots import make_subplots
from typing import Optional

from modules import database_manager
from modules.base_app import app, DEBUG_STATE
from modules.z_generator import points, is_back_point, generate_z

# ===== Variables ===== #
marks = None
is_processed = False
data = pl.DataFrame()

# ===== Helper functions ===== #
def date_to_string(date: datetime) -> str:
    """
    Converts a datetime to a string.

    Parameters
    ----------
    date : datetime.datetime
        The datetime to convert.

    Returns
    -------
    str
    """
    return date.strftime("%d/%m/%Y %H:%M:%S")

def calculate_marks(data: pl.DataFrame) -> dict[int, str]:
    """
    Calculates the marks for the slider.

    Parameters
    ----------
    data : polars.DataFrame
        The data to use.

    Returns
    -------
    dict[int, str]
        Dictionary mapping the indices to the date strings.
    """
    n = len(data)
    dates: pl.Series = data["index"]
    if n < 2:
        return None
    marks = {0: date_to_string(dates[0]), len(data) - 1: date_to_string(dates[-1])}
    if n >= 5:
        half_index = n // 2
        marks[half_index] = date_to_string(dates[half_index])
        index = half_index // 2
        marks[index] = date_to_string(dates[index])
        marks[n - index] = date_to_string(dates[n - index])
    return marks

def create_heatmaps_fig(z: tuple[list[list[int]]]) -> go.Figure:
    """
    Creates a figure with two heatmaps.

    Parameters
    ----------
    z : tuple[list[list[int]]]
        The data to use.
    """
    label = dict(font_size=14)
    contours = dict(start=0, end=4608, showlines= False)
    template = "Value: %{z:.2f}<extra></extra>"

    fig = make_subplots(rows=1, cols=2, subplot_titles=("Seat", "Backrest"))
    fig.add_trace(go.Contour(z=z[0], connectgaps=True, contours=contours, hoverlabel=label,
                                colorscale="Blues", hovertemplate=template), row=1, col=1)
    fig.add_trace(go.Contour(z=z[1], connectgaps=True, contours=contours, hoverlabel=label,
                                colorscale="Blues", hovertemplate=template), row=1, col=2)

    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)

    for key in points:
        fig.add_annotation(x=points[key][1], y=points[key][0], text=key, showarrow=False, font=dict(size=12),
                           row=1, col=1 + is_back_point(key))

    return fig

def calculate_contour_average_plot() -> go.Figure:
    """
    Calculates the average of all the data and returns a contour plot.
    Used to make the app.layout more readable.
    """
    global data

    # Calculate the average of each sensor
    z = generate_z(data[:, :-1].mean())

    fig = create_heatmaps_fig(z)
    fig.update_layout(height=700, width=1200, title_text="Average Heatmap")

    return fig

def calculate_asymmetry_plot() -> go.Figure:
    """
    Quantifies how assymetric the seat and backrest are.
    """
    global data

    # Calculate the average of each sensor
    avg = data.mean()
    asymmetry_data = {
        "F - seat top": avg[0, 10] - avg[0, 11],
        "E - seat top-mid": avg[0, 8] - avg[0, 9],
        "D - seat bottom-mid": avg[0, 6] - avg[0, 7],
        "C - seat bottom": avg[0, 4] - avg[0, 5],
        "B - backrest top": avg[0, 2] - avg[0, 3],
        "A - backrest bottom": avg[0, 0] - avg[0, 1]
    }
    color_list = np.where(np.array(list(asymmetry_data.values())) > 0, "#2986EB", "#EB6963")
    fig = px.bar(x=list(asymmetry_data.values()), y=list(asymmetry_data.keys()), orientation="h")
    fig.update_layout(height=400, width=800,
                    title_text="Pressure Asymmetry",
                    xaxis_title="Left - Right",
                    yaxis_title="Part of seat",
                    xaxis=dict(range=[-512, 512]),
                    showlegend=False)
    fig.update_traces(marker_color=color_list)
    return fig

def calculate_time_seated_plot(granularity: int = 10, threshold: int = 500) -> go.Figure:
    """
    Calculates the time spent sitting on the seat.

    Parameters
    ----------
    granularity : int
        The granularity of the data in seconds.
    threshold : int
        The threshold of the pressure to be considered sitting
    """
    global data

    times = data["index"]
    time_start = times[0]
    time_end = times[-1]

    intervals_classified = []

    interval_start = time_start
    last_data_idx = 0
    # Pass through all intervals
    while interval_start < time_end:
        interval_class = None
        interval_data = []

        # Pass through all data points
        while times[last_data_idx] < (interval_start + datetime.timedelta(seconds=granularity)):
            interval_data.append(data[last_data_idx].mean(axis=1)[0])
            last_data_idx += 1
            if last_data_idx >= len(data):
                break

        # If there is no data in the interval
        if len(interval_data) == 0:
            interval_class = "No data"
        else:
            # Classify the interval based on the average pressure
            interval_mean = np.mean(interval_data)
            if interval_mean > threshold:
                interval_class = "Sitting"
            else:
                interval_class = "Not sitting"

        # Join the intervals if they are the same
        if len(intervals_classified) > 0 and intervals_classified[-1]["class"] == interval_class:
            # Update the end of the interval
            intervals_classified[-1]["end"] = interval_start + datetime.timedelta(seconds=granularity)

        # If the interval is different, add it to the list
        else:
            intervals_classified.append({
                "class": interval_class,
                "start": interval_start,
                "end": interval_start + datetime.timedelta(seconds=granularity)
            })

        # Move to the next interval
        interval_start += datetime.timedelta(seconds=granularity)

    intervals_classified = pl.DataFrame(intervals_classified)

    # Create a horizontal bar chart where the x axis is the time and the y axis is the classification
    fig = px.timeline(x_start=intervals_classified["start"],
                    x_end=intervals_classified["end"],
                    y=intervals_classified["class"],
                    color=intervals_classified["class"],
                    color_discrete_map={"No data": "white", "Sitting": "#2986EB", "Not sitting": "#EB6963"}
                    )

    fig.update_traces(marker_line_width=0)
    fig.update_layout(title_text="Time spent sitting on the seat",
                    xaxis_title="Time",
                    yaxis_title="Sitting",
                    bargap=0
                    )
    return fig

def calculate_line_plot() -> go.Figure:
    """
    Calculates the line plot of the pressure over time.
    """
    global data
    global is_processed

    if not is_processed:
        times = data["index"]
        seconds = datetime.timedelta(seconds=30)
        # Find the indices of sudden jumps in time
        temp = np.abs(times[:-1] - times[1:]) > seconds
        bad = temp.arg_true() + 1

        # If there are sudden jumps in time and the values are not 0,
        # then add a new data point with 0 values to make the line plot
        # more readable and continuous
        if len(bad) > 0:
            is_processed = True
            epsilon = datetime.timedelta(milliseconds=1)
            extension = []

            for idx in bad:
                # Append the new time points to the list
                if data[idx - 1].max(axis=1)[0] > 0:
                    extension.append(times[idx - 1] + epsilon)
                if data[idx].max(axis=1)[0] > 0:
                    extension.append(times[idx] - epsilon)

            if len(extension) > 0:
                zeros = [[0 for _ in range(13)] for _ in range(len(extension))]
                for i in range(len(extension)):
                    zeros[i][12] = extension[i]
                temp = pl.DataFrame(zeros,
                    schema={col: dtype for col, dtype in zip(data.columns, data.dtypes)})
                data.extend(temp)
                data = data.sort("index")


    fig = go.Figure()
    for col in data.columns[:-1]:
        fig.add_scatter(x=data["index"], y=data[col], name=col, mode="lines")
    fig.update_layout(title="Pressure over time", xaxis_title="Time",
                      yaxis_title="Pressure", hovermode="x unified")
    return fig

# ===== Layout ===== #
layout = html.Div([
    dbc.Row(justify="center", children=[
        dbc.Col([
            html.H2("Time Selector", className="tabTitle"),
            html.Br(),
            html.H3("Select a date", className="tabSubtitle"),
            html.P("List of dates with data:", className="tabText"),
            dcc.Dropdown(	
                id="datePicker",
                options=[{"label": day, "value": day} for day in database_manager.get_list_of_days()],
                clearable=False,
                className="dropdown"
            ),
            html.Br(),
            dcc.DatePickerSingle(
                id="dateSelector",
                min_date_allowed=date(2022, 1, 1),
                max_date_allowed=date(2023, 12, 31),
                display_format="DD/MM/YYYY",
            ),
            html.Button("Select", id="dateSelectorButton", className="btn btn-light"),
            html.Div(id="dateSelectText", children="No date selected."),
            html.Button("Download CSV", id="downloadButton", className="btn btn-lg btn-primary"),
            dcc.Download(id="downloadData"),
            html.Br(),

            # Fast data visualzization Graphs
            dcc.Graph(id="lineGraph"),
            dcc.Graph(id="timeSeatedGraph"),

            html.Br(),
            dcc.Slider(
                id="frameSlider",
                min=0,
                max=len(data) - 1,
                step=1,
                value=len(data) - 1,
                marks=None,
            ),
            html.Div(id="playerControls", children=[
                html.Button("Play", id="playButton", n_clicks=0, style={"display": "inline-block"},
                            className="btn btn-light"),
                html.Fieldset([
                    html.Label(children="Speed:", style={"display": "inline-block"},
                               className="form-label alignCenter"),
                    dcc.Input(id="playSpeed", type="number", style={"display": "inline-block"},
                              className="form-control alignCenter", value=1),
                ], style={"display": "inline-block"}),
                dcc.Interval(id="playInterval", 
                interval=1000, 
                n_intervals=0),
            ]),

            # Graphs
            dcc.Graph(id="contourGraphFrame"),
            html.Br(),
            html.H2("Summary Plots"),
            dcc.Graph(id="contourGraphAvg"),
            dcc.Graph(id="asymmetryGraph"),
            dcc.Graph(id="timeSeatedGraph"),
            dcc.Graph(id="lineGraph"),
        ], width=8, style={"textAlign": "center", "align-content": "center"}),
    ]),
])

# ===== Callbacks ===== #
@app.callback(Output("dateSelectText", "children"),
            Output("timeSeatedGraph", "figure"),
            Output("lineGraph", "figure"),
            State("dateSelector", "date"),
            Input("dateSelectorButton", "n_clicks"))
def update_date_text(date: datetime, n_clicks: int) -> tuple[str, go.Figure, go.Figure]:
    if n_clicks is not None:
        global data

        data = database_manager.get_data_from_day(date)
        if date is not None:
            return f"{data.shape[0]} rows selected.", calculate_time_seated_plot(), calculate_line_plot()
        else:
            return "No date selected.", None, None

@app.callback(Output("downloadData", "data"),
                Input("downloadButton", "n_clicks"))
def download_csv(n_clicks: Optional[int]):
    if n_clicks is not None:
        global data

        data.write_csv("data.csv")
        return dcc.send_file("data.csv")

@app.callback(Output("dateSelector", "date"),
            Input("datePicker", "value"))
def update_date_picker(value):
    return value

# # slider text
# @app.callback(Output("dateDisplay", "children"),
#                 Input("frameSlider", "value"))
# def update_date_display(frame_number):
#     return date_to_string(data[frame_number, "index"])

# # contour plot
# @app.callback(Output("contourGraphFrame", "figure"),
#                 Input("frameSlider", "value"))
# def update_contour_plot(frame_number):
#     z = generate_z(data[frame_number, :-1])

#     fig = create_heatmaps_fig(z)
#     fig.update_layout(height=700, width=1200, title_text="Heatmap")

#     return fig

# # play button
# @app.callback(Output("frameSlider", "value"),
#                 Input("playButton", "n_clicks"),
#                 Input("playInterval", "n_intervals"),
#                 State("frameSlider", "value"),
#                 State("playSpeed", "value"))
# def update_slider(n_clicks, _n_intervals, frame_number, speed):
#     # if speed is None, pause
#     if speed is None:
#         return frame_number

#     if n_clicks == 0:
#         return frame_number
#     if n_clicks % 2 != 0:  # play
#         if frame_number == len(data) - 1:  # if it"s the last frame, reset
#             return 0
#         return frame_number + 1
#     return frame_number  # pause

# @app.callback(Output("playButton", "children"),
#                 Input("playButton", "n_clicks"))
# def update_play_button(n_clicks):
#     if n_clicks % 2 == 0:
#         return "Play"
#     return "Pause"

# # play interval
# @app.callback(Output("playInterval", "interval"),
#                 Input("playSpeed", "value"))
# def update_play_interval(speed):
#     if speed == 0:
#         return 10_000_000
#     return 1000 / speed

# # select data button
# @app.callback(Output("dateSelectorButton", "children"),
#                 Output("frameSlider", "marks"),
#                 Output("frameSlider", "max"),
#                 Output("contourGraphFrameAvg", "figure"),
#                 Output("asymmetryGraph", "figure"),
#                 Output("timeSeatedGraph", "figure"),
#                 Output("lineGraph", "figure"),
#                 Input("dateSelectorButton", "n_clicks"),
#                 State("datePicker", "date"),
#                 State("timePickerStart", "value"),
#                 State("timePickerEnd", "value"))
# def select_data(n_clicks, date):
#     global data
#     global marks
#     global is_processed

#     if n_clicks == 0:
#         return ["Select",
#                 marks,
#                 len(data) - 1,
#                 calculate_contour_average_plot(),
#                 calculate_asymmetry_plot(),
#                 calculate_time_seated_plot(),
#                 calculate_line_plot()]

#     data = database_manager.get_data_from_day(date)
#     is_processed = False
#     marks = calculate_marks(data)

#     print("data downloaded")

#     if len(data) == 0:
#         return ["No data selected",
#                 None,
#                 0,
#                 None,
#                 None,
#                 None,
#                 None]

#     print("marks", marks)

#     return [f"{len(data)} frames selected",
#             marks,
#             len(data) - 1,
#             calculate_contour_average_plot(),
#             calculate_asymmetry_plot(),
#             calculate_time_seated_plot(),
#             calculate_line_plot()]
