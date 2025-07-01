import os
import pandas as pd

curr_dir = os.getcwd()
dataframes = os.listdir("Steam Data")

def get_game_data_over_time(game_names:set):
    curr_dir = os.getcwd()
    dataframes = os.listdir("Steam Data")
    game_data = pd.DataFrame()

    for df_file in dataframes:
        df = pd.read_csv(os.path.join(curr_dir, "Steam Data", df_file),converters={'Genres': pd.eval, 'Tags': pd.eval})
        game_row = df.loc[df["Game"].isin(game_names)]
        game_data = pd.concat([game_data,game_row], ignore_index=True)
    game_data["Date Collected"] = pd.to_datetime(game_data["Date Collected"])
    game_data = game_data.sort_values("Date Collected")
    return game_data

