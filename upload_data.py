import pandas as pd
from pymongo import MongoClient
import creds


# 1. Connect to MongoDB
client = MongoClient(creds.CONNECTION_STRING)
db = client["SteamCollectedData"]
collection = db["Steam Data"]

# 2. Read CSV
df = pd.read_csv("Steam Combined Data/Steam_Overall_Data.csv")

# 3. Convert to dictionary and upload
data = df.to_dict("records")
collection.insert_many(data)

print("Data uploaded successfully!")
