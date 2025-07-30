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

    curr_dir = os.getcwd()
    dataframes = os.listdir("Steam Data")
    # Multiselect widget for genres
    selected_genres = st.multiselect('Select genres to filter by:', Genres)
    selected_tags = st.multiselect('Select tags to filter by:', Tags)
    # Text Input for Games
    search_query = st.selectbox("Enter Game Name",[""] + scd.get_all_game_names())

    st.divider()

    # Display DataFrame A
    select_df_a = st.selectbox("A: Select a DataFrame to view", dataframes)
    filename_A = Path(select_df_a).stem  # removes extension
    clean_name_A = ff.clean_str(filename_A.replace("steam_top_games_", ""))

    st.subheader(f"{clean_name_A} Data Overview")

    df_a_raw_data = pd.read_csv(os.path.join(curr_dir, "Steam Data", select_df_a),converters={'Genres': pd.eval, 'Tags': pd.eval})
    filtered_data_df_a = df_a_raw_data
    try:
        filtered_data_df_a = ff.filter_dfs(filtered_data_df_a,selected_genres,selected_tags,search_query)
    except:
        st.write("Error filtering data")

    st.write(filtered_data_df_a)

    
    # Display DataFrame B
    select_df_b = st.selectbox("B: Select a DataFrame to view", dataframes)
    filename_B = Path(select_df_b).stem
    clean_name_B = ff.clean_str(filename_B.replace("steam_top_games_",""))
    st.subheader(f"{clean_name_B} Data Overview")
    select_df_b_raw_data = pd.read_csv(os.path.join(curr_dir, "Steam Data", select_df_b),converters={'Genres': pd.eval, 'Tags': pd.eval})

    filtered_data_df_b = select_df_b_raw_data
    try: 
        filtered_data_df_b = ff.filter_dfs(filtered_data_df_b,selected_genres,selected_tags,search_query)
    except:
        st.write("Error filtering data")

    st.write(filtered_data_df_b)
        
    st.divider()
    # Create bar plot
    st.subheader("Genre Counts Comparison (Feb vs. Mar)")
    GenreCounts = pd.read_csv(os.path.join(curr_dir,"Generated_Data","GenreCounts.csv"))    # Dashboard title

    fig, ax = plt.subplots(figsize=(10, 6))
    GenreCounts.set_index('Genres').plot(kind='bar', ax=ax)
    ax.set_xlabel("Genres")
    ax.set_ylabel("Count")
    ax.set_title("Genre Counts: February vs. March")


    # Display plot in the Streamlit app
    st.pyplot(fig,use_container_width=False)


# 
def tag_evaluation():
    dataframes = os.listdir("Steam Data")
    generated_data = os.listdir("Generated_Data")
    curr_dir = os.getcwd()

    # Display DataFrames
    select_df = st.selectbox("Select a DataFrame to view", dataframes)
    
    date = ff.clean_str((Path(select_df).stem).replace("steam_top_games_",""))
    # Multiselect widget for genres
    selected_genres = st.multiselect('Select genres to filter by:', Genres)
    selected_tags = st.multiselect('Select tags to filter by:', Tags)
    # Text Input for Games
    search_query = st.selectbox("Enter Game Name",[""] + scd.get_all_game_names())
    st.divider()

    st.subheader("Steam Data for " + date)
    data = pd.read_csv(os.path.join(curr_dir, "Steam Data", select_df),converters={'Genres': pd.eval, 'Tags': pd.eval})
    try:
        data = ff.filter_dfs(data,selected_genres,selected_tags,search_query)
        st.write(data)
    except:
        st.write("Failed to filter Data")
    st.divider()
    st.subheader(f"Tags Comparison ({date})")
    
    try: 
        tag_count = data['Tags'].explode().value_counts()
        tag_importance_path = "feature_importances_"+date+ ".csv"
        if tag_importance_path not in generated_data:
            st.write("Calculating Tag Importance")
            tag_distribution,x,y = ml.forest_ml(data)
        else:
            tag_distribution = pd.read_csv(os.path.join(curr_dir,"Generated_Data", tag_importance_path))
        tag_distribution = tag_distribution[["Tag","Importance"]]
        final_tag = tag_distribution.merge(tag_count.rename('# Of Games with Tag'),left_on="Tag",right_index=True)
        st.write(final_tag)
        st.divider()
        st.subheader("Tag Distribution for " + date)
        fig, ax = plt.subplots(figsize=(10, 6))
        tag_count.head(20).plot(kind='pie', ax=ax)
        ax.set_title("Tag Distribution")
        st.pyplot(fig,use_container_width=False)
    except:
        st.write("Error filtering data, data may not contain tags")
    
def compare_game_attributes_over_time():
    st.header("Game Stats Over Time")


    if "game_list" not in st.session_state:
        st.session_state.game_list = []
    

    # Text Input for Games
    search_query = st.selectbox("Enter Game Name",[""] + scd.get_all_game_names())

    if st.button("Add Game"):
        if search_query and search_query not in st.session_state.game_list:
            st.session_state.game_list.append(search_query)
    

    # Displays the games added to the game list, with the option to remove them 
    st.subheader("Your Game List:")
    for game in st.session_state.game_list:
        col1,col2 = st.columns([4,1])
        with col1:
            st.write(game)
        with col2:
            if st.button(f"❌", key=f"remove_{game}"):
                st.session_state.game_list.remove(game)
                st.rerun()

    if st.session_state.game_list:
            
        # Passes the game list to receive the games data over all of the dataframes
        data = vf.get_game_data_over_time(set(st.session_state.game_list))
        maximum_peak_count = int(data["Peak"].max())
        intervals = math.ceil((maximum_peak_count//10)/50000)*50000

        fig = px.line(
            data,
            x = "Date Collected",
            y = "Peak",
            color = "Game",
            title= "Peak Player Count Over Time",
            labels= {"Peak":"Peak Player Count","Date Collected":"Date"}
        )
        fig.add_trace(
        go.Scatter(
        x=data['Date Collected'],
        y=data['Peak'],
        mode='markers',
        name='Saved Points',
        marker=dict(size=8, color='red', symbol='circle')
    )
)
        st.plotly_chart(fig,use_container_width=True)
    else:
        st.write("Add Games to the List to see their trends")
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
