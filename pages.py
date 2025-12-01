# Standard Libraries
import math
from pathlib import Path
import os 
# Third-Party Data Libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
# Local Modules
from constants import Genres, Tags
from functions import filter_funcs as ff
from functions import ml_funcs as ml
from functions import visualization_funcs as vf
from functions import streamlit_cached_data as scd

# Main Front page of the dashboard, can compare 2 dataframes to each other as well as filter
def overview():
    st.header("Steam Data Comparison Overview")

    # Gets static data from cache to be used later
    steam_data = scd.load_all_steam_data()
    dates = scd.get_all_data_dates()
    
    game_names = scd.get_all_game_names()
    # Multiselect widget for genres
    selected_genres = st.multiselect('Select genres to filter by:', Genres)
    selected_tags = st.multiselect('Select tags to filter by:', Tags)
    # Text Input for Games
    search_query = st.selectbox("Enter Game Name",[""] + game_names)

    st.divider()

    # Display DataFrame A
    selected_date = st.selectbox("A: Select a Date to view", dates, index=len(dates) - 1)
    st.subheader(f"{selected_date} Data Overview")

    df_A = steam_data[steam_data["Date Collected"]==selected_date]
    filtered_data_df_A = df_A
    try:
        filtered_data_df_A = ff.filter_dfs(filtered_data_df_A,selected_genres,selected_tags,search_query)
    except:
        st.write("Error filtering data")

    st.write(filtered_data_df_A)

    
    st.subheader("Report Summary")
    try:
        # Flatten list columns (Genres, Tags)
        all_genres = [g for sublist in df_A['Genres'] for g in sublist]
        all_tags = [t for sublist in df_A['Tags'] for t in sublist]
        # Most popular genre
        most_popular_genre = pd.Series(all_genres).value_counts().idxmax()
        # Most popular tag
        most_popular_tag = pd.Series(all_tags).value_counts().idxmax()
    except:
        st.write("ERROR GETTING TAGS OR GENRES")
        most_popular_genre = "N/A"
        most_popular_tag = "N/A"

    # Trending new games
    # Requires 'Rank' column (1 = highest) and 'Days Since Release' column
    trending_new_games = df_A[
        (df_A['Rank'] <= 20) &
        (df_A['Days Since Release'] <= 30)
    ]['Game'].tolist()

    # Display in Streamlit
    st.write(f"**Most Popular Genre:** {most_popular_genre}")
    st.write(f"**Most Popular Tag:** {most_popular_tag}")
    st.write(f"**Trending New Games:** {', '.join(trending_new_games) if trending_new_games else 'None'}")
    st.divider()

# 
def tag_evaluation():
    dates = scd.get_all_data_dates()
    game_names = scd.get_all_game_names()
    # Display DataFrames
    date_selected = st.selectbox("Select a DataFrame to view", dates)
    
    # Multiselect widget for genres
    selected_genres = st.multiselect('Select genres to filter by:', Genres)
    selected_tags = st.multiselect('Select tags to filter by:', Tags)
    # Text Input for Games
    search_query = st.selectbox("Enter Game Name",[""] + game_names)
    st.divider()

    st.subheader("Steam Data for " + date_selected)
    steam_data = scd.load_all_steam_data()
    steam_data = steam_data[steam_data["Date Collected"]==date_selected]
    try:
        steam_data = ff.filter_dfs(steam_data,selected_genres,selected_tags,search_query)
        st.write(steam_data)
    except:
        st.write("Failed to filter Data")
    st.divider()
    st.subheader(f"Tags Comparison ({date_selected})")
    
    try: 
        tag_count = steam_data['Tags'].explode().value_counts()
        
        tag_distribution = tag_distribution[["Tag","Importance"]]
        final_tag = tag_distribution.merge(tag_count.rename('# Of Games with Tag'),left_on="Tag",right_index=True)
        st.write(final_tag)
        st.divider()
        st.subheader("Tag Distribution for " + date_selected)
        fig, ax = plt.subplots(figsize=(10, 6))
        tag_count.head(20).plot(kind='pie', ax=ax)
        ax.set_title("Tag Distribution")
        st.pyplot(fig,use_container_width=False)
    except:
        st.write("Error filtering data, data may not contain tags")

def compare_game_attributes_over_time():
    st.header("Game Stats Over Time")

    # Initialize the session state list if not already present
    if "game_list" not in st.session_state:
        st.session_state.game_list = []

    # Dropdown to pick a game
    search_query = st.selectbox("Select a Game to Add", [""] + scd.get_all_game_names())

    # Add selected game to the list
    if st.button("Add Game"):
        if search_query and search_query not in st.session_state.game_list:
            st.session_state.game_list.append(search_query)
            st.rerun()  # rerun immediately so UI updates

    # Display the current game list with remove buttons
    st.subheader("Your Game List:")
    if st.session_state.game_list:
        for game in st.session_state.game_list:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(game)
            with col2:
                if st.button("❌", key=f"remove_{game}"):
                    st.session_state.game_list.remove(game)
                    st.rerun()
    else:
        st.info("No games added yet. Use the dropdown to add games.")
        return  # Exit early if no games

    # Option to switch between Current and Peak counts
    metric_choice = st.radio(
        "Select which player count to display:",
        ("Current", "Peak"),
        horizontal=True
    )

    # If there are games selected, display their trends
    if st.session_state.game_list:
        data = vf.get_game_data_over_time(set(st.session_state.game_list))

        # Safeguard: skip if no matching data
        if data.empty:
            st.warning("No data found for the selected games.")
            return

        # Create line chart dynamically based on choice
        fig = px.line(
            data,
            x="Date Collected",
            y=metric_choice,
            color="Game",
            title=f"{metric_choice} Player Count Over Time",
            labels={metric_choice: f"{metric_choice} Player Count", "Date Collected": "Date"}
        )

        # Add red markers for points
        fig.add_trace(
            go.Scatter(
                x=data["Date Collected"],
                y=data[metric_choice],
                mode="markers",
                name="Data Points",
                marker=dict(size=6, color="red", symbol="circle")
            )
        )

        st.plotly_chart(fig, use_container_width=True)

# The help page that explains what each column displays, and how to navigate the dashboard
def help():
    st.header("Description")
    st.write("This is a dashboard that allows you to compare Steam game data from different months")
    st.write("The Overview page allows you to compare the data from two different months")
    st.write("The Tag Evaluation page allows you to see the importance of tags in the data")
    st.write("The Game Trend page allows you to see how the peak player counts fluctuates of multiple games")


    st.header("Columns")
    st.write("Game: The name of the game")
    st.write("Current: The current number of players when the data was collected")
    st.write("Peak: The peak number of players that day")
    st.write("Player Hours: The number of hours played that day")
    st.write("App ID: The ID of the game")
    st.write("Release Date: The date the game was released")
    st.write("Genres: The genres of the game set by Steam")
    st.write("Tags: The tags associated with the game set by the Community")
    st.write("Days Since Release: The number of days since the game was released since the data was collected")
    st.write("All Review Score: The review score of the game, the higher score the most positive reviews")
    st.write("All Review Count: The number of reviews")
    st.write("Recent Review Score: The review score of the game in the past month")
    st.write("Recent Review Count: The number of reviews in the past month")
