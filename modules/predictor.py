from modules import database_manager
from modules.base_app import app, DEBUG_STATE
import polars as pl
import pickle
import random

# ===== Load model ===== #
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

# ===== Helper functions ===== #
def get_model():
    return model

def get_current_data(named : bool = False) -> tuple[str, tuple]:
    current_data_ = pl.DataFrame()
    current_data = database_manager.get_current_data()
    if current_data.shape[0] == 0:
        state = ['Not Sitting']
    else:
        current_data = current_data.drop("index")
        current_data_ = current_data
        current_data = current_data.rows(named=False)
        state = model.predict(current_data)

    return state[0], current_data_

def get_last_active_day_data() -> tuple[str, pl.DataFrame]:
    day, data = database_manager.get_last_active_day_data()

    data = data.drop("index")
    state = model.predict(data)
    return day, state, data
