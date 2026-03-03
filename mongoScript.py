from pymongo import MongoClient
import creds

client = MongoClient(creds.CONNECTION_STRING)
db = client["SteamCollectedData"]
collection = db["Steam Data"]

pipeline = [
    {
        "$group": {
            "_id": {"appId": "$App ID", "date": "$Date Collected"},
            "count": {"$sum": 1}
        }
    },
    {"$match": {"count": {"$gt": 1}}}
]

duplicates = list(collection.aggregate(pipeline))
print(f"Number of duplicate groups remaining: {len(duplicates)}")
