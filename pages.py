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

    # Gets static data from cache to be used later
    steam_data = scd.load_all_steam_data()
    dates = scd.get_all_data_dates()
    daily_player_count_data = scd.daily_player_count()
    game_names = scd.get_all_game_names()

    # Create line chart dynamically based on choice
    fig = px.line(
        daily_player_count_data,
        x="Date Collected",
        y="Current",
        title=f"Top Steam Game's Total Player Count Over {len(dates)} Days",
        labels={"Player Count": "Player Count", "Date Collected": "Date"},
        markers= True
    )

    # Display the chart
    st.plotly_chart(fig, width="stretch")
    st.divider()

    st.header("Dataframe Comparisons")
    # Multiselect widget for genres
    selected_genres = st.multiselect('Select genres to filter by:', Genres)
    selected_tags = st.multiselect('Select tags to filter by:', Tags)
    # Text Input for Games
    search_query = st.selectbox("Enter Game Name",[""] + game_names)

    # Display DataFrame 
    selected_date = st.selectbox("A: Select a Date to view", dates, index=0)
    st.subheader(f"{selected_date} Data Overview")

    df_A = steam_data[steam_data["Date Collected"]==selected_date]
    filtered_data_df_A = df_A
    try:
        filtered_data_df_A = ff.filter_dfs(filtered_data_df_A,selected_genres,selected_tags,search_query)
    except Exception as e:
        st.write(f"Error filtering data. Error :{e}")

    st.write(filtered_data_df_A)

    st.subheader("Report Summary")
    try:
        # Flatten list columns (Genres, Tags)
        most_popular_genres = df_A['Genres'].explode().value_counts().head(3).index
        most_popular_tags = df_A['Tags'].explode().value_counts().head(3).index
    
    except Exception as e:
        st.warning(f"ERROR GETTING TAGS OR GENRES. Error:{e}")
        most_popular_genres = []
        most_popular_tags = []

    # Trending new games
    # Requires 'Rank' column (1 = highest) and 'Days Since Release' column
    trending_new_games = df_A[
        (df_A['Rank'] <= 20) &
        (df_A['Days Since Release'] <= 30)
    ]['Game'].unique().tolist()

    new_game_releases = df_A[df_A["Days Since Release"]<=15]["Game"].unique().tolist()

    # Top Row 
    col1,col2 = st.columns(2)
    with col1:
        st.metric("Most Popular Genres", f"{', '.join(most_popular_genres) if not most_popular_genres.empty else 'None'}")
    with col2:
        st.metric(f"Most Popular Tags", f"{', '.join(most_popular_tags) if not most_popular_tags.empty else 'None'}")

    # Bottom Row
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("** Trending New Games:**")
        st.info(', '.join(trending_new_games) if trending_new_games else 'None')
    with col4:
        st.markdown("** All New Releases:**")
        st.info(', '.join(new_game_releases) if new_game_releases else 'None')

    st.divider()

# Page that will handle tag evaluations
def tag_evaluation():
    dates = scd.get_all_data_dates()
    game_names = scd.get_all_game_names()
    # Display DataFrames
    date_selected = st.selectbox("Select a DataFrame to view", dates)

    # Sets subheader for the section
    st.subheader("Steam Data for " + date_selected)
    steam_data = scd.load_all_steam_data()
    steam_data = steam_data[steam_data["Date Collected"]==date_selected]

    st.subheader(f"Tags Comparison ({date_selected})")
    
    try: 
        tag_count = steam_data['Tags'].explode().value_counts()
        tag_distribution, mse, r2 = ml.forest_ml(steam_data)
        print(f"MSE: {mse}, R2: {r2}")
        tag_distribution = tag_distribution[["Tag","Importance"]]
        final_tag = tag_distribution.merge(tag_count.rename('# Of Games with Tag'),left_on="Tag",right_index=True)
        st.write(final_tag)
        fig, ax = plt.subplots(figsize=(5,5))
        tag_count.head(20).plot(kind='pie', ax=ax)
        ax.set_title("Tag Distribution")
        st.pyplot(fig,use_container_width=False)
    except Exception as e:
        st.write("Error filtering data, data may not contain tags")
        print(e)

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
            labels={metric_choice: f"{metric_choice} Player Count", "Date Collected": "Date"},
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)

# The help page that explains what each column displays, and how to navigate the dashboard
def help():
    st.header("Description")
    st.markdown("""
    This is a dashboard that allows you to compare Steam game data from different months.
    * **Overview:** Compare the data from two different dates.
    * **Tag Evaluation:** See the importance and distribution of tags in the data.
    * **Game Trend:** See how the player counts fluctuate for multiple games over time.
    """)

    st.header("Data Dictionary")
    st.markdown("""
    * **Game:** The name of the game
    * **Current:** The current number of players when the data was collected
    * **Peak:** The peak number of players that day
    * **Player Hours:** The number of hours played that day
    * **App ID:** The unique Steam ID of the game
    * **Release Date:** The date the game was released
    * **Genres:** The genres of the game (set by Steam)
    * **Tags:** The tags associated with the game (set by the Community)
    * **Days Since Release:** The number of days between the release date and data collection
    * **All Review Score:** The overall review score (higher = more positive)
    * **All Review Count:** The total number of reviews
    * **Recent Review Score:** The review score over the past month
    * **Recent Review Count:** The number of reviews in the past month
    """)
