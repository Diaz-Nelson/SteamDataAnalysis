import streamlit as st
import os
import pandas as pd
from functions import filter_funcs as ff
from pymongo import MongoClient
import streamlit as st


try:
    from creds import CONNECTION_STRING
except ImportError:
    CONNECTION_STRING = st.secrets["CONNECTION_STRING"]

@st.cache_data(ttl=600)
def load_all_steam_data():
    client = MongoClient(CONNECTION_STRING)
    db = client["SteamCollectedData"]
    collection = db["Steam Data"]
    data = list(collection.find({}))
    df = pd.DataFrame(data)
    df.drop(columns=["_id"], inplace=True)
    return df


@st.cache_data
def get_all_game_names():
    dataframe = load_all_steam_data()
    game_names = dataframe['Game'].unique()
    return list(game_names)

def get_all_data_dates():
    dataframe = load_all_steam_data()
    dates = dataframe["Date Collected"].unique()
    return list(dates)