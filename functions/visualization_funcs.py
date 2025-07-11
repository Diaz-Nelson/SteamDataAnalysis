import os
import pandas as pd
from Functions import streamlit_cached_data as stc
curr_dir = os.getcwd()
dataframes = os.listdir("Steam Data")

# Returns a time series dataset with all the given games in a set sroted by Date Collected
def get_game_data_over_time(game_names:set):

    # Initializes an empty pandas dataframe to concact all relevant rows to it
    game_data = pd.DataFrame()

    # Receives all the dataframes from the streamlit cache
    dataframes = stc.load_all_steam_data().values()

    # Iterates thorugh all dataframes, 
    for df in dataframes:
        game_row = df.loc[df["Game"].isin(game_names)]
        game_data = pd.concat([game_data,game_row], ignore_index=True)
    game_data = game_data[["Game","Peak","Date Collected"]]
    game_data["Date Collected"] = pd.to_datetime(game_data["Date Collected"])
    game_data = game_data.sort_values("Date Collected")
    return game_data

