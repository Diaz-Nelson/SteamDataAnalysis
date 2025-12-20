from pymongo import MongoClient
import creds

client = MongoClient(creds.CONNECTION_STRING)
db = client["SteamCollectedData"]
collection = db["Steam Data"]

# Date to delete
target_date = "2025-12-01"

# Delete all documents with this date
result = collection.delete_many({"Date Collected": target_date})

print(f"Deleted {result.deleted_count} documents from the collection.")
