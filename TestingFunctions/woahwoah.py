import pandas as pd
import math

def calc_sucess_score(gamedata):
    recent_review_score = gamedata['Recent Review Score']
    recent_review_count = gamedata['Recent Review Count']

    all_review_score = gamedata['All Review Score']
    all_review_count = gamedata['All Review Count']

    player_hours = gamedata['Player Hours']
    days_since_release = gamedata['Days Since Release']

    current_players = gamedata['Current']
    peak_players = gamedata['Peak']
    success_score = (
        (recent_review_score * 0.2) +
        (all_review_score * 0.3) +
        (current_players/peak_players * 0.1) +
        (player_hours/days_since_release * 0.2) +
        (recent_review_count/all_review_count * 0.2)
    )

    return(math.log(success_score))

test = pd.read_csv('steam_top_games_03-08-2025_00-43-12.csv',converters={'Genres': pd.eval,'Tags': pd.eval})


test["Popularity Score"] = test.apply(calc_sucess_score,axis=1)
test_cleaned = test.dropna(subset=['Popularity Score'])
print(test_cleaned[['Game', 'Popularity Score']])