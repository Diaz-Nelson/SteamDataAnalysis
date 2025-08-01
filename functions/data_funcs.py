import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import streamlit as st
import os
import re

try:
    from creds import STEAM_KEY
except ImportError:
    STEAM_KEY = st.secrets["STEAM_KEY"]

# Global variables to keep track of failed requests
get_game_failed = 0
details_failed = 0
tags_failed = 0
steam_rejections = 0
# Bypass age check by setting the 'wants_mature_content' cookie
cookies = {
        "birthtime": "568022401",  # Fake birthdate (epoch time, 1988)
        "mature_content": "1",     # Accept mature content
        "lastagecheckage": "1-0-1988"  # Fake last age check
    }
review_score = {"Overwhelmingly Positive":9,"Very Positive":8,"Positive":7,"Mostly Positive":6,"Mixed":5,"Mostly Negative":4,"Negative":3,"Very Negative":2,"Overwhelmingly Negative":1}

# Gets the tags and review data for a given Steam Game
def get_steam_reviews_tags(app_id):
    url = f"https://store.steampowered.com/app/{app_id}/"
    
    global cookies
    global tags_failed
    global steam_rejections

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, cookies=cookies)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # Get tags, excluding the last one
        tags = [tag.text.strip() for tag in soup.select(".app_tag")][:-1]

        # Get review summary
        review_summary = [[num.text.strip(), num.find_next_sibling("span").text.strip()[1:-1]] for i, num in enumerate(soup.select(".game_review_summary")) if i < 2]

        if len(review_summary) == 0:
            print(f"Failed to retrieve review summary for {app_id}")
            tags_failed += 1
            return {"Tags": [None], "Recent Review Score": None, "Recent Review Count": None, "All Review Score": None, "All Review Count": None}

        # Convert review counts to integers
        try:
            review_summary[0][1] = int(review_summary[0][1].replace(",", ""))
        except ValueError:
            review_summary[0][1] = None  # Set to None if conversion fails

        try:
            if len(review_summary) > 1:
                review_summary[1][1] = int(review_summary[1][1].replace(",", ""))
            else:
                review_summary.append([review_summary[0][0], review_summary[0][1]])  # Duplicate the first review if only one exists
        except ValueError:
            review_summary[1][1] = review_summary[0][1]


        return {
            "Tags": tags,
            "Recent Review Score": review_score.get(review_summary[0][0], None),  # Use .get() to avoid KeyError
            "Recent Review Count": review_summary[0][1],
            "All Review Score": review_score.get(review_summary[1][0], None),
            "All Review Count": review_summary[1][1]
        }

    else:
        print(f"Failed to get response from STEAM for {app_id}")
        steam_rejections += 1
        return {"Tags": [None], "Recent Review Score": None, "Recent Review Count": None, "All Review Score": None, "All Review Count": None}

def get_game_details(app_id):
    global details_failed
    global get_game_failed

    url = f"http://store.steampowered.com/api/appdetails?appids={app_id}&key={STEAM_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch data for {app_id}")
        get_game_failed += 1
        return {
            "Genres": ['None'],
            "Release Date": None,
            "Days Since Release": None
        }

    data = response.json()

    if not data.get(str(app_id), {}).get("success", False):
        print(f"Failed to retrieve details for {app_id}")
        details_failed += 1
        return {
            "Genres": ['None'],
            "Release Date": None,
            "Days Since Release": None
        }

    game_data = data[str(app_id)]["data"]
    genres = [genre["description"] for genre in game_data.get("genres", [])]

    release_str = game_data.get("release_date", {}).get("date", "").strip()
    days_since_release = None

    try:
        if release_str and release_str.lower() != "coming soon":
            release_date = datetime.strptime(release_str, "%b %d, %Y")
            days_since_release = (datetime.now() - release_date).days
    except ValueError:
        # Optional: log invalid format for debug
        print(f"Invalid date format for {app_id}: '{release_str}'")

    return {
        "Genres": genres or ['None'],
        "Release Date": release_str if release_str else None,
        "Days Since Release": days_since_release
    }

def scrape_steam_charts(pages):
    url = "https://steamcharts.com/top"
    headers = {"User-Agent": "Mozilla/5.0"}
    game_data = []
    for i in range(1,pages):
        url = f"https://steamcharts.com/top/p.{i}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch page {i}")
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table",{"class":"common-table"})
        for row in table.find_all("tr")[1:]:
            columns = row.find_all("td")
            rank = columns[0].text.strip()
            game = columns[1].text.strip()
            current_players = columns[2].text.strip()
            peak_players = columns[4].text.strip()
            hours = columns[5].text.strip()
            app_link = columns[1].find("a")["href"]
            app_id = app_link.split("/")[-1]
            game_data.append({"Rank": rank, "Game": game, "Current": current_players, "Peak": peak_players, "App ID": app_id, "Player Hours": hours})
    return pd.DataFrame(game_data)

# Main data pipeline function, calls all webstracping and API calling functions, combining all data into one dataframe, keeping track of how many failures appear
def get_game_data(pages:2):
    global details_failed
    global get_game_failed
    print("Scraping Steam Charts...")
    game_data = scrape_steam_charts(pages)
    # Gets each games details using Steam's own API, then turns the series into a dataframe
    print("Getting Each Games Details...")
    game_details = game_data["App ID"].apply(get_game_details)
    details_df = pd.DataFrame(game_details.tolist())
    # Gets each games tags and review data from Steam, then turns the series into a dataframe
    print("Getting Each Games Tags and Reviews...")
    game_tags = game_data["App ID"].apply(get_steam_reviews_tags)
    tags_df = pd.DataFrame(game_tags.tolist())
    print("Combining Data...")
    final_data = pd.concat([game_data, details_df,tags_df], axis=1)

    date_collected = datetime.now().strftime("%m-%d-%Y")
    final_data["Date Collected"] = date_collected

    return final_data,details_failed,get_game_failed,tags_failed, date_collected


def add_date_col(folder_path = "Steam Data"):
  # Regex pattern to match date from filename: steam_top_games_06-24-2025_13-46-33.csv
    date_pattern = re.compile(r"steam_top_games_(\d{2}-\d{2}-\d{4})_\d{2}-\d{2}-\d{2}\.csv")

    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            match = date_pattern.search(filename)
            if match:
                date_collected = match.group(1)  # Extracted date as MM-DD-YYYY
                file_path = os.path.join(folder_path, filename)
                df = pd.read_csv(file_path)

                # Only add the column if it doesn't already exist
                if "Date Collected" not in df.columns:
                    df["Date Collected"] = date_collected
                    df.to_csv(file_path, index=False)
                    print(f"Added 'Date Collected' to: {filename}")
                else:
                    print(f"'Date Collected' already exists in: {filename}")