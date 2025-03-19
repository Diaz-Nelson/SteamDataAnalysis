import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import datetime
from creds import STEAM_KEY


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

# Gets the tags and review data for a given Steame Game
def get_steam_reviews_tags(app_id):
    url = f"https://store.steampowered.com/app/{app_id}/"
    
    # Bypass age check by setting the 'wants_mature_content' cookie
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
    """Fetches genres, release date, and Metacritic rating for a given game from the Steam API."""
    url = f"http://store.steampowered.com/api/appdetails?appids={app_id}&key={STEAM_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch data for {app_id}")
        get_game_failed+=1
        return {"Genres": ['None'], "Release Date": None}
    
    data = response.json()
    
    if not data[str(app_id)]["success"]:
        print(f"Failed to retrieve details for {app_id}")
        details_failed+=1
        return {"Genres": ['None'], "Release Date": None,'Days Since Release':None}

    game_details = data[str(app_id)]["data"]

    return {
        "Genres": [genre["description"] for genre in game_details.get("genres", [])],
        "Release Date": game_details.get("release_date", {}).get("date", "Unknown"),
        "Days Since Release": (datetime.datetime.now() - datetime.datetime.strptime(game_details.get("release_date", {}).get("date", "Unknown"), "%b %d, %Y")).days
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

    return final_data,details_failed,get_game_failed,tags_failed

def filter_data_by_genres(df, selected_genres):
    if selected_genres:
        # Filter rows where all selected genres are present in the Genres list
        filtered_df = df[df['Genres'].apply(lambda genres: all(genre in genres for genre in selected_genres))]
    else:
        filtered_df = df  # If no genres selected, return the whole DataFrame
    
    return filtered_df
def search_game(df, query):
    if query:
        # Filter the DataFrame where the 'Game' column contains the search query (case insensitive)
        filtered_df = df[df['Game'].str.contains(query, case=False, na=False)]
    else:
        filtered_df = df  # If no query is provided, return the whole DataFrame
    return filtered_df
def filter_data_by_tags(df, selected_tags):
    if selected_tags:
        # Filter rows where all selected genres are present in the Genres list
        filtered_df = df[df['Tags'].apply(lambda tags: all(tag in tags for tag in selected_tags))]
    else:
        filtered_df = df  # If no genres selected, return the whole DataFrame
    
    return filtered_df