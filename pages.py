import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os 
from functions import data_funcs as funcs
from functions import ml_funcs as ml
from constants import Tags,Genres

def overview():
    st.header("Steam Data Comparison Overview")

    dataframes = os.listdir("Steam Data")
    # Multiselect widget for genres
    selected_genres = st.multiselect('Select genres to filter by:', Genres)
    selected_tags = st.multiselect('Select tags to filter by:', Tags)
    # Text Input for Games
    search_query = st.text_input('Search for a game:', '')

    st.divider()

    # Display DataFrame A
    select_df_a = st.selectbox("A: Select a DataFrame to view", dataframes)
    st.subheader(select_df_a.replace("steam_top_games_","")[:-4] + " Data Overview")
    df_a_raw_data = pd.read_csv("Steam Data\\"+select_df_a,converters={'Genres': pd.eval, 'Tags': pd.eval})

    filtered_data_df_a = df_a_raw_data
    try:
        if selected_genres:
            filtered_data_df_a = funcs.filter_data_by_genres(filtered_data_df_a, selected_genres)
            
        if selected_tags:
            filtered_data_df_a = funcs.filter_data_by_tags(filtered_data_df_a, selected_tags)

        if search_query:
            filtered_data_df_a = funcs.search_game(filtered_data_df_a, search_query)
    except:
        st.write("Error filtering data")

    st.write(filtered_data_df_a)

    
    # Display DataFrame B
    select_df_b = st.selectbox("B: Select a DataFrame to view", dataframes)

    st.subheader(select_df_b.replace("steam_top_games_","")[:-4] + " Data Overview")
    select_df_b_raw_data = pd.read_csv("Steam Data\\"+ select_df_b,converters={'Genres': pd.eval, 'Tags': pd.eval})

    filtered_data_df_b = select_df_b_raw_data
    try: 
        if selected_genres:
            filtered_data_df_b = funcs.filter_data_by_genres(filtered_data_df_b, selected_genres)
        if selected_tags:
            filtered_data_df_b = funcs.filter_data_by_tags(filtered_data_df_b, selected_tags)
        if search_query:
            filtered_data_df_b = funcs.search_game(filtered_data_df_b, search_query)
    except:
        st.write("Error filtering data")

    st.write(filtered_data_df_b)
        
    st.divider()
    # Create bar plot
    st.subheader("Genre Counts Comparison (Feb vs. Mar)")
    GenreCounts = pd.read_csv("Generated_Data\\GenreCounts.csv")    # Dashboard title

    fig, ax = plt.subplots(figsize=(10, 6))
    GenreCounts.set_index('Genres').plot(kind='bar', ax=ax)
    ax.set_xlabel("Genres")
    ax.set_ylabel("Count")
    ax.set_title("Genre Counts: February vs. March")


    # Display plot in the Streamlit app
    st.pyplot(fig,use_container_width=False)

def tag_evaluation():
    dataframes = os.listdir("Steam Data")
    generated_data = os.listdir("Generated_Data")
    # Display DataFrame A
    select_df_a = st.selectbox("A: Select a DataFrame to view", dataframes)
    date = select_df_a.replace("steam_top_games_","")[:-4]
    st.subheader("Steam Data for " + date)
    data = pd.read_csv("Steam Data\\"+select_df_a,converters={'Genres': pd.eval, 'Tags': pd.eval})
    st.divider()
    st.write(data)
    st.divider()
    st.subheader(f"Tags Comparison ({date})")
    tag_count = data['Tags'].explode().value_counts()

    tag_importance_path = "feature_importances_"+date+ ".csv"
    try: 
        if tag_importance_path not in generated_data:
            st.write("Calculating Tag Importance")
            tag_distribution,x,y = ml.forest_ml(data)
            if st.button("Save Tag Importance"):
                tag_distribution.to_csv("Generated_Data/" + tag_importance_path,index=False)
                st.write("Data saved to ",tag_importance_path)      
        else:
            tag_distribution = pd.read_csv("Generated_Data/" + tag_importance_path)
        tag_distribution = tag_distribution[["Tag","Importance"]]
        final_tag = tag_distribution.merge(tag_count.rename('# Of Games with Tag'),left_on="Tag",right_index=True)
    except:
        st.write("Error filtering data")
    
    st.write(final_tag)