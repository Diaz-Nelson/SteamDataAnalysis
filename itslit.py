import streamlit as st
from pages import overview, tag_evaluation, help, compare_game_attributes_over_time
# Set page layout to wide
st.set_page_config(layout="wide")




page = st.sidebar.radio("Navigation", ["Overview", "Tag Evaluation","Game Attribute Analysis","Help"])
# Dashboard title
st.title("Steam Data Analysis Dashboard")
if page == "Overview":
    overview()
elif page == "Tag Evaluation":
    tag_evaluation()
elif page == "Game Attribute Analysis":
    compare_game_attributes_over_time()
elif page == "Help":
    help()
