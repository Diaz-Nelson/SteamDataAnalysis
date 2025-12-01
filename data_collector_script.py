import os
import pandas as pd
from datetime import datetime
from functions import data_funcs
from pymongo import MongoClient
import creds


# 1. Connect to MongoDB
client = MongoClient(creds.CONNECTION_STRING)
db = client["SteamCollectedData"]
collection = db["Steam Data"]

# Steam Top Games Data from Web scraping
game_data, details_failed, game_failed, tags_failed = data_funcs.get_game_data(8)
print(game_data)
# Standardize today's date in ISO format
dateCollected = datetime.now().strftime("%Y-%m-%d")
game_data["Date Collected"] = dateCollected

# Directory for CSVs
data_dir = os.path.join(os.getcwd(), "Steam Combined Data")
os.makedirs(data_dir, exist_ok=True)

# Save Overall Data
overall_file = os.path.join(data_dir, "Steam_Overall_Data.csv")

if os.path.exists(overall_file):
    overall_df = pd.read_csv(overall_file,parse_dates=["Date Collected"],index_col=False)

    # Standardize existing dates to ISO format
    if "Date Collected" in overall_df.columns:
        overall_df["Date Collected"] = pd.to_datetime(overall_df["Date Collected"], errors="coerce").dt.strftime("%Y-%m-%d")

    # Check for today's entry
    if dateCollected in overall_df["Date Collected"].values:
        print("Data for today already exists in Steam_Overall_Data.csv, skipping save.")
    else:
        overall_df = pd.concat([overall_df, game_data], ignore_index=True)
        # 3. Convert to dictionary and upload
        data = overall_df.to_dict("records")
        collection.insert_many(data)
        overall_df.to_csv(overall_file, index=False)
        print("Saved updated Steam_Overall_Data.csv")
else:
    game_data.to_csv(overall_file, index=False)
    print("Created Steam_Overall_Data.csv")