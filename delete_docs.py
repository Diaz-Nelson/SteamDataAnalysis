from pymongo import MongoClient
import creds

client = MongoClient(creds.CONNECTION_STRING)
db = client["SteamCollectedData"]
collection = db["Steam Data"]


collection.update_many(
    {},
    [
        {
            "$set": {
                "Current": {
                    "$convert": {
                        "input": {
                            "$cond": [
                                { "$eq": [{ "$type": "$Current" }, "string"] },
                                {
                                    "$replaceAll": {
                                        "input": "$Current",
                                        "find": ".",
                                        "replacement": ""
                                    }
                                },
                                "$Current"
                            ]
                        },
                        "to": "int",
                        "onError": None,
                        "onNull": None
                    }
                },

                "Peak": {
                    "$convert": {
                        "input": {
                            "$cond": [
                                { "$eq": [{ "$type": "$Peak" }, "string"] },
                                {
                                    "$replaceAll": {
                                        "input": "$Peak",
                                        "find": ".",
                                        "replacement": ""
                                    }
                                },
                                "$Peak"
                            ]
                        },
                        "to": "int",
                        "onError": None,
                        "onNull": None
                    }
                },

                "Player Hours": {
                    "$convert": {
                        "input": {
                            "$cond": [
                                { "$eq": [{ "$type": "$Player Hours" }, "string"] },
                                {
                                    "$replaceAll": {
                                        "input": "$Player Hours",
                                        "find": ".",
                                        "replacement": ""
                                    }
                                },
                                "$Player Hours"
                            ]
                        },
                        "to": "long",
                        "onError": None,
                        "onNull": None
                    }
                }
            }
        }
    ]
)
