import pandas as pd
import sklearn as sk
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score
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
        (recent_review_score * math.log(recent_review_count)) +
        (all_review_score * math.log(all_review_count)) +
        (current_players/peak_players )+
        (math.log(player_hours)/days_since_release) +
        (math.log(days_since_release)/math.log(current_players))+ 
        (recent_review_count/all_review_count)
    )

    return(math.log(success_score))

def forest_ml(data):
    tags_expanded = pd.DataFrame(data['Tags'].tolist(), index=data.index).stack().reset_index(level=1, drop=True)
    tag_dummies = pd.get_dummies(tags_expanded).groupby(level=0).sum()

    data['Popularity'] = data.apply(calc_sucess_score, axis=1)
    data = data.dropna(subset=['Tags','Popularity'])
    test_with_tags = pd.concat([data, tag_dummies], axis=1).dropna()

    X = test_with_tags.drop(columns=['Game','Genres','Tags','Popularity','App ID','Release Date','Rank','Days Since Release','All Review Score','All Review Count','Recent Review Score','Recent Review Count','Current','Peak','Player Hours'])
    y = test_with_tags['Popularity']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    
    importances = model.feature_importances_

    # Create a DataFrame with the feature importances
    feature_importances = pd.DataFrame({
        'Tag': X.columns,
        'Importance': importances
    }).sort_values(by='Importance', ascending=False)
    return feature_importances, mse, r2