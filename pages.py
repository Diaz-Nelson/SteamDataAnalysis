import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

import data_funcs as funcs


def overview():
    st.header("Steam Data Comparison Overview")
    GenreCounts = pd.read_csv("GenreCounts.csv")    # Dashboard title


    # Multiselect widget for genres
    selected_genres = st.multiselect('Select genres to filter by:', ['Action', 'Adventure', 'RPG', 'Simulation', 'Indie', 'Free To Play', 'Strategy', 'Massively Multiplayer', 
                'Casual', 'Early Access', 'Sports', 'Utilities', 'Animation & Modeling', 'Design & Illustration', 
                'Racing', 'Video Production', 'Photo Editing', 'Game Development', 'Education', 'None', 'Audio Production', 'Software Training'])
    # Text Input for Games
    search_query = st.text_input('Search for a game:', '')


    # Display DataFrame
    st.subheader("February 13th Data Overview")
    feb_raw_data = pd.read_csv("steam_top_games_feb13.csv",converters={'Genres': pd.eval, 'Tags': pd.eval})
    if selected_genres:
        filtered_data_feb = funcs.filter_data_by_genres(feb_raw_data, selected_genres)
    else:
        filtered_data_feb = feb_raw_data
    if search_query:
        filtered_data_feb = funcs.search_game(filtered_data_feb, search_query)
    st.write(filtered_data_feb)


    # Display DataFrame
    st.subheader("March 13th Data Overview")
    march_raw_data = pd.read_csv("steam_top_games_03-13-2025_19-11-34.csv",converters={'Genres': pd.eval, 'Tags': pd.eval})
    if selected_genres:
        filtered_data_march = funcs.filter_data_by_genres(march_raw_data, selected_genres)
    else:
        filtered_data_march = march_raw_data

    if search_query:
        filtered_data_march = funcs.search_game(filtered_data_march, search_query)
    st.write(filtered_data_march)
        

    st.write()

    # Create bar plot
    st.subheader("Genre Counts Comparison (Feb vs. Mar)")

    fig, ax = plt.subplots(figsize=(10, 6))
    GenreCounts.set_index('Genres').plot(kind='bar', ax=ax)
    ax.set_xlabel("Genres")
    ax.set_ylabel("Count")
    ax.set_title("Genre Counts: February vs. March")


    # Display plot in the Streamlit app
    st.pyplot(fig,use_container_width=False)

def tag_evaluation():
    
    pass