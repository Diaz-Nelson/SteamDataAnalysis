import streamlit as st
import pandas as pd
from functions import filter_funcs as ff
from pymongo import MongoClient
import streamlit as st
import ast

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

    list_columns = ["Genres", "Tags"]

    for col in list_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: 
                x if isinstance(x, list) 
                else ast.literal_eval(x) if isinstance(x, str) and x.startswith("[") 
                else []
            )

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