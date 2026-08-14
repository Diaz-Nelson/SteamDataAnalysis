# Steam Gaming Trends Analysis

A data-driven tool that tracks Steam's daily top games and applies machine learning to identify which tag combinations correlate with commercial success, giving publishers and developers a data-backed way to evaluate new game concepts.

## 🌐 Live Demo

[https://steamdataanalysisnd.streamlit.app/]

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
- **Success Score Model**: A well-tuned formula to estimate how successful a game currently is based on multiple factors like user reviews, player engagement, and retention.
- **Automated Data-Scraping**: Steam Data is collected daily at 7 PM via automated Windows Scheduler script. 
- **Cloud Stored Data**: All collected data is saved online onto a Mongo Database for simple storage and query.
- **Size**: Over 1 Year of Data Collection with 40k+ Rows of Historical Data


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
- **Top Tags Identified**: As of October 2025, certain tags like *Open World*, *Multiplayer*, and *Survival* showed strong positive correlations with game success.
- **Insightful Visualizations**: Dynamic charts help identify popular genre trends and successful tag synergies.

## Future Improvements

- Incorporate player retention metrics (e.g., playtime over weeks).
- Expand beyond top 400 games to improve generalizability.
- Add clustering to identify genre archetypes.
- Introduce temporal trend tracking (e.g., monthly tag performance changes).



---

## 📬 Contact

Have feedback or ideas to collaborate? Feel free to reach out @ nelsondiaz061603@gmail.com !
