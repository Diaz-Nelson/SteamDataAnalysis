import os
import pandas as pd
from functions import streamlit_cached_data as scd
curr_dir = os.getcwd()
dataframes = os.listdir("Steam Data")

# Returns a time series dataset with all the given games in a set sroted by Date Collected
def get_game_data_over_time(game_names:set):

    # Initializes an empty pandas dataframe
    game_data = pd.DataFrame()

    # Receives all the dataframes from the streamlit cache
    df = scd.load_all_steam_data()

    game_data = df[df["Game"].isin(game_names)][["Game", "Peak", "Date Collected"]]
    game_data = game_data.sort_values("Date Collected")

    return game_data

