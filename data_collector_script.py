import pandas as pd
from datetime import datetime
from functions import data_funcs
from pymongo import MongoClient
import creds

client = MongoClient(creds.CONNECTION_STRING)
db = client["SteamCollectedData"]
collection = db["Steam Data"]

game_data, details_failed, game_failed, tags_failed = data_funcs.get_game_data(8)

game_data = game_data.rename(columns=lambda c: c.strip())

game_data["Rank"] = pd.to_numeric(game_data["Rank"].str.replace(r"\.", "", regex=True), errors="coerce").astype("Int64")
game_data["App ID"] = pd.to_numeric(game_data["App ID"].str.replace(r"\.", "", regex=True), errors="coerce").astype("Int64")
game_data["Current"] = pd.to_numeric(game_data["Current"].str.replace(r"\.", "", regex=True), errors="coerce").astype("Int64")
game_data["Peak"] = pd.to_numeric(game_data["Peak"].str.replace(r"\.", "", regex=True), errors="coerce").astype("Int64")
game_data["Player Hours"] = pd.to_numeric(game_data["Player Hours"].str.replace(r"\.", "", regex=True), errors="coerce").astype("Int64")

dateCollected = datetime.now().strftime("%Y-%m-%d")
game_data["Date Collected"] = dateCollected

if collection.count_documents({"Date Collected": dateCollected}, limit=1) == 0:
    collection.insert_many(game_data.to_dict("records"))
    print("Inserted today's Steam data into MongoDB")
else:
    print("Data for today already exists in MongoDB, skipping insert")
