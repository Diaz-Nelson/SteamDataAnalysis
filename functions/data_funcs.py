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
        "birthtime": "568022401",  # Artificial birthdate (epoch time, 1988)
        "mature_content": "1",     # Accept mature content
        "lastagecheckage": "1-0-1988"  # Artificial last age check
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
        try:
                
            soup = BeautifulSoup(response.text, "html.parser")
            # Get tags, excluding the last one
            tags = [tag.text.strip() for tag in soup.select(".app_tag")][:-1]
            if not tags:
                print("FAILED TO GET TAGS FOR",app_id)



            # Get review summary
            review_summary = soup.select(".user_reviews_summary_row .game_review_summary")
            review_summaries = [span.get_text(strip=True) for span in review_summary]

            review_count_summary = soup.select(".user_reviews_summary_row .responsive_hidden")
            # Extract review counts and convert to integers
            review_counts = []
            for span in review_count_summary:
                text = span.get_text(strip=True)
                text = text.replace("(", "").replace(")", "").replace(",", "")  # remove formatting
                try:
                    count = int(text)
                except ValueError:
                    count = None
                review_counts.append(count)
            return {
                "Tags": tags,
                "Recent Review Score": review_score.get(review_summaries[0], None),  # Use .get() to avoid KeyError
                "Recent Review Count": review_counts[0],
                "All Review Score": review_score.get(review_summaries[1], review_summaries[0]),
                "All Review Count": review_counts[1] if len(review_counts)>1 else review_counts[0]
            }
        except:
            print(f"Failed to get tags or Review Counts for {app_id} ")
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

def get_game_data(pages=2):
    """
    Scrapes Steam Charts data and enriches it with Steam API game details.

    Returns:
        final_data (pd.DataFrame): Combined dataset of base + details.
        details_failed (list): App IDs where Steam API details failed.
        get_game_failed (list): App IDs where base data fetch failed.
        tags_failed (list): App IDs where tag scraping failed (if enabled).
        date_collected (str): Date of data collection.
    """
    details_failed = []
    get_game_failed = []
    tags_failed = []
    
    print("[INFO] Scraping Steam Charts...")

    try:
        game_data = scrape_steam_charts(pages)
    except Exception as e:
        print(f"[ERROR] Failed to get base data: {e}")
        return pd.DataFrame(), details_failed, get_game_failed, tags_failed
    print("[INFO] Getting each game's details via Steam API...")
    try:
        game_details = game_data["App ID"].apply(get_game_details)
        details_df = pd.DataFrame(game_details.tolist())
    except Exception as e:
        print(f"[ERROR] Failed to retrieve game details: {e}")
        return game_data, details_failed, get_game_failed, tags_failed

    print("[INFO] Getting tags and reviews...")
    try:
        game_tags = game_data["App ID"].apply(get_steam_reviews_tags)
        tags_df = pd.DataFrame(game_tags.tolist())
    except Exception as e:
        print(f"[ERROR] Failed to scrape tags/reviews: {e}")
        return pd.concat([game_data, details_df], axis=1), details_failed, get_game_failed, tags_failed

    print("[INFO] Combining dataframes...")
    final_data = pd.concat([game_data, details_df, tags_df], axis=1)

    print("[SUCCESS] Game data successfully compiled.")
    return final_data, details_failed, get_game_failed, tags_failed