from Functions import data_funcs
from datetime import datetime

# Gets the time as soon as the program is ran to be used later to calculate the time taken to retrieve all the data from steam charts, Steam API, and cleaning it.
start = datetime.now()

# Retrives the data for today from all sources and saves the game data along with various details on the pipeline
game_data,details_failed,game_failed,tags_failed,dateCollected = data_funcs.get_game_data(8)

print(game_data.head(10))


file_name ="steam_top_games_{}".format((datetime.now()).strftime("%m-%d-%Y_%H-%M-%S"))

game_data.to_csv(f"Steam Data/{file_name}.csv", index=False)