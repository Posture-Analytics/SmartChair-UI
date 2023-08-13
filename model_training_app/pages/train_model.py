import dash
from dash import dcc, html, Input, Output, State
import login_manager
import random

dash.register_page(__name__, path='/train-model')

started = False

layout = html.Div([
    html.H3("Train Model"),
    html.H4("Pose 1 out of 12", id="pose-text"),
    html.Img(src="/assets/pose1.png", style={"width": "50%"}),
    html.Br(),
    html.Progress(id="progress", value='0', max='5000'),
    html.P("Stay in this pose for 5 seconds...", id="timer-text"),
    html.P("", id="instructions"),
    dcc.Interval(id="interval", interval=10, n_intervals=0),
    html.Button("Next", id="next-button", className="btn btn-secondary"),
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
def update_progress(n_intervals, progress):
    if int(progress) >= 5000:
        return False, progress, "Done!", "Get up before going to the next pose."
    
    # dummy code to simulate the chair detecting the user
    if progress == '0':
        reading = login_manager.get_last_reading(chance=0.99)
    else:
        reading = login_manager.get_last_reading(chance=0.01)

    if reading is None and progress == '0':
        return True, progress, "Stay in this pose for 5 seconds...", "You can start as soon as you're ready. The timer will start automatically when it detects you're sitting."
    elif reading is None:
        return True, progress, "Stay in this pose for 5 seconds...", "The chair cannot detect you. Please sit down as shown in the picture."
    else:
        return True, str(int(progress) + 20), f"Stay in this pose for {5 - (int(progress) // 1000)} seconds...", ""

@dash.callback(
    Output("next-button", "disabled"),
    Output("progress", "value"),
    Output("timer-text", "children"),
    Output("pose-text", "children"),
    Output("interval", "n_intervals"),
    Output("instructions", "children"),
    Input("next-button", "n_clicks"),
    prevent_initial_call=True,
)
def next_pose(n_clicks):

    if n_clicks is None:
        return True, '0', "Stay in this pose for 5 seconds...", "Pose 1 out of 12", 0, ""
    else:
        if n_clicks == 12:
            return True, '0', "", "Done!", 0, "You're done! You can now go back to the home page."

        return (True, 
                '0', 
                "Stay in this pose for 5 seconds...", 
                f"Pose {n_clicks + 1} out of 12", 0, 
                "You can start as soon as you're ready. The timer will start automatically when it detects you're sitting.")