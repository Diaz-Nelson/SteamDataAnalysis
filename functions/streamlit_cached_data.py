import streamlit as st
import os
import pandas as pd

@st.cache_data
def load_all_steam_data():
    dataframes = {}
    data_dir = os.path.join(os.getcwd(), "Steam Data")
    for file in os.listdir(data_dir):
        if file.endswith(".csv"):
            df = pd.read_csv(
                os.path.join(data_dir, file),
                converters={'Genres': pd.eval, 'Tags': pd.eval}
            )
            dataframes[file] = df
    return dataframes

@st.cache_data
def get_all_game_names():
    dataframes = load_all_steam_data()
    large_dataframe = pd.concat(dataframes.values(),ignore_index=True)
    game_names = large_dataframe['Game'].unique()
    return list(game_names)