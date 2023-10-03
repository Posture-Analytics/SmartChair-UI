import database_manager
import numpy as np
import pickle
import polars as pl

from datetime import date
from sklearn.ensemble import RandomForestClassifier

# ===== Load model ===== #
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

# Debug model
model = RandomForestClassifier()

# ===== Helper functions ===== #
def get_model() -> RandomForestClassifier:
    """Returns the fitted model."""
    return model

def get_current_data() -> tuple[str, pl.DataFrame]:
    """
    Gets the data currently being sent by the sensors and predicts the state.
    If there's no data being sent, it returns an empty DataFrame.

    Returns
    -------
    tuple[str, polars.DataFrame]
        The posture state and the data.
    """
    current_data = database_manager.get_current_data()
    if current_data.shape[0] == 0:
        state = ["Not Sitting"]
    else:
        current_data = current_data.drop("index")
        state = model.predict(current_data.rows(named=False))

    return state[0], current_data

def get_last_active_day_data() -> tuple[date, np.ndarray, pl.DataFrame]:
    """
    Gets the data from the last day that has data.

    Returns
    -------
    tuple[datetime.date, numpy.ndarray, polars.DataFrame]
        The last day with data, its posture states and the data.
    """
    day, data = database_manager.get_last_active_day_data()

    data_ = data
    data = data.drop("index")
    data = data.rows(named=False)
    state = model.predict(data)
    return day, state, data_
