import streamlit as st
from pages import overview
from pages import tag_evaluation

# Set page layout to wide
st.set_page_config(layout="wide")




page = st.sidebar.radio("Navigation", ["Overview", "Tag Evaluation"])
# Dashboard title
st.title("Steam Data Analysis Dashboard")
if page == "Overview":
    overview()
elif page == "Tag Evaluation":
    tag_evaluation()
