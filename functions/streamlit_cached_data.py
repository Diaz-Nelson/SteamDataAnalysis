import streamlit as st
import os
import pandas as pd
from functions import filter_funcs as ff

@st.cache_data
def load_all_steam_data():
    steam_data = pd.read_csv(os.path.join("Steam Combined Data","Steam_Overall_Data.csv"),converters={
        "Genres": ff.safe_literal_eval,
        "Tags": ff.safe_literal_eval
    })
    return steam_data

@st.cache_data
def get_all_game_names():
    dataframe = load_all_steam_data()
    game_names = dataframe['Game'].unique()
    return list(game_names)

def get_all_data_dates():
    dataframe = load_all_steam_data()
    dates = dataframe["Date Collected"].unique()
    return list(dates)