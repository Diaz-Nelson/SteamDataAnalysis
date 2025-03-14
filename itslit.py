import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

import data_funcs as funcs
from pages import overview

# Set page layout to wide
st.set_page_config(layout="wide")




page = st.sidebar.radio("Navigation", ["Overview", "Tag Evaluation"])
# Dashboard title
st.title("Steam Data Analysis Dashboard")
if page == "Overview":
    overview()
elif page == "Tag Evaluation":
    st.write("Tag Evaluation")
    st.write("Coming soon!")
