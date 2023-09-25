import dash
import polars as pl

from dash import dcc, html, Input, Output, State

import login_manager

dash.register_page(__name__, path="/train-model")

seconds = 2
interval = 1000
data = pl.DataFrame()
labels = pl.Series()
pose = 1

layout = html.Div([
    html.H3("Train Model"),
    dcc.Input(id="email", type="email", placeholder="Email"),
    html.H4("Pose 1 out of 12", id="pose-text"),
    html.Img(src="/assets/pose1.png", style={"width": "50%"}),
    html.Br(),
    html.Progress(id="progress", value="0", max=f"{seconds}000"),
    html.P(f"Stay in this pose for {seconds} seconds...", id="timer-text"),
    html.P("", id="instructions"),
    dcc.Interval(id="interval", interval=interval, n_intervals=0),
    html.Button("Next", id="next-button", className="btn btn-secondary"),
    html.Br(),
    html.Button("Train Model", id="train-button", className="btn btn-primary")
])

@dash.callback(
    Output("next-button", "disabled", allow_duplicate=True),
    Output("progress", "value", allow_duplicate=True),
    Output("timer-text", "children", allow_duplicate=True),
    Output("instructions", "children", allow_duplicate=True),
    Input("interval", "n_intervals"),
    State("progress", "value"),
    prevent_initial_call=True,
)
def update_progress(n_intervals: int, progress: str) -> tuple[bool, str, str]:
    global data, labels

    if int(progress) >= seconds * 1000:
        return False, progress, "Done!", "Get up before going to the next pose."

    reading = login_manager.get_current_data()

    if reading is None and progress == "0":
        return True, progress, f"Stay in this pose for {seconds} seconds...", "You can start as soon as you're ready. The timer will start automatically when it detects you're sitting."
    elif reading is None:
        return True, progress, f"Timer stopped.", "The chair cannot detect you. Please sit down as shown in the picture."
    else:
        # If it's the first reading, set data to be the reading
        if data.shape[0] == 0:
            data = reading
            labels = pl.Series([str(pose)])
        # Else, append the reading to data
        else:
            data = data.vstack(reading)
            labels = labels.append(pl.Series([str(pose)]))
        return True, str(int(progress) + interval), f"Stay in this pose for {seconds - (int(progress) // 1000)} seconds..."

@dash.callback(
    Output("next-button", "disabled"),
    Output("progress", "value"),
    Output("timer-text", "children"),
    Output("pose-text", "children"),
    Output("interval", "n_intervals"),
    Output("instructions", "children", allow_duplicate=True),
    Input("next-button", "n_clicks"),
    prevent_initial_call=True,
)
def next_pose(n_clicks: int) -> tuple[bool, str, str, str, int, str]:
    global pose

    if n_clicks is None:
        return True, "0", f"Stay in this pose for {seconds} seconds...", "Pose 1 out of 12", 0, ""
    else:
        pose += 1
        if pose > 12:
            return True, "0", "", "Done!", 0, "You're done! You can now go back to the home page."

        return (True,
                "0",
                f"Stay in this pose for {seconds} seconds...",
                f"Pose {pose} out of 12", 0,
                "You can start as soon as you're ready."
                "The timer will start automatically when it detects you're sitting.")

@dash.callback(
    Output("train-button", "disabled"),
    Output("instructions", "children"),
    Input("train-button", "n_clicks"),
    State("email", "value"),
    prevent_initial_call=True,
)
def train_model(n_clicks: int, email: str) -> tuple[bool, str]:
    global data, labels

    if n_clicks is None:
        return False, ""
    else:
        if login_manager.train_model(data, labels, email):
            return True, "Model trained successfully!"
        else:
            return False, "Error training model. Please try again."
