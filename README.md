# Steam Gaming Trends Analysis

A data-driven project analyzing current gaming trends on Steam to uncover which tags and features contribute to a game's success. This tool tracks the top games on Steam daily and evaluates the effectiveness of various game tags using machine learning and visual analytics. 

## Project Summary

Between February 2025 and March 2025, I built a system that:

- Scrapes and collects data from the top 400 Steam games.
- Analyzes the relationship between game tags and overall success.
- Uses machine learning (Random Forest Regressor) to identify the most influential tags.
- Predicts a games possible success metric or current relevancy
- Visualizes key insights through an interactive Streamlit dashboard.

## Key Features

- **Real-time Trend Tracking**: Updated insights based on current top Steam games.
- **Tag Importance Analysis**: Discover which tags correlate with higher game success.
- **Tag Synergy Heatmap**: Explore how tags interact and which combinations historically perform best.
- **Success Score Model**: A custom formula to estimate how successful a game is based on multiple factors like user reviews, player engagement, and retention.
- **Automated Data-Scraping**: Steam Data is collected daily at 7 PM via automated Windows Scheduler script. 
- **Cloud Stored Data**: All collected data is saved online onto a Mongo Database for simple storage. 


##  Tech Stack

- **Python**: Core logic and data processing
- **Pandas & NumPy**: Data manipulation
- **scikit-learn**: Machine learning (RandomForestRegressor)
- **Matplotlib & Seaborn**: Data visualization
- **Streamlit**: Web-based interactive dashboard
- **Steam API + Web Scraping**: Data sourcing
- **Mongo Database**: Cloud Storage



##  Results

- **Model Accuracy**: Achieved a Mean Squared Error (MSE) of 0.03 and R² score of 0.6.
- **Top Tags Identified**: Certain tags like *Open World*, *Multiplayer*, and *Survival* showed strong positive correlations with game success.
- **Insightful Visualizations**: Dynamic charts help identify popular genre trends and successful tag synergies.

## Future Improvements

- Incorporate player retention metrics (e.g., playtime over weeks).
- Expand beyond top 400 games to improve generalizability.
- Add clustering to identify genre archetypes.
- Introduce temporal trend tracking (e.g., monthly tag performance changes).


## 🌐 Live Demo

[https://steamdataanalysisnd.streamlit.app/]

---

## 📬 Contact

Have feedback or ideas to collaborate? Feel free to reach out!
