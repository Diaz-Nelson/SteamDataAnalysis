from functions import data_funcs
from datetime import datetime
from functions import ml_funcs


# Gets the time as soon as the program is ran to be used later to calculate the time taken to retrieve all the data from steam charts, Steam API, and cleaning it.
start = datetime.now()

# Retrives the data for today from all sources and saves the game data along with various details on the pipeline
game_data,details_failed,game_failed,tags_failed,dateCollected = data_funcs.get_game_data(8)

# Calculates the time taken to retreive the data, then shows a snippet of the Dataframe. It then provides details over how many 
print("Time taken to get data: ",datetime.now()-start)
print(game_data.head(10))

print("Game Failed: ",game_failed)
print("Details Failed: ",details_failed)
print("Tags Failed: ",tags_failed)
print("Date Collected:",dateCollected)
ans = input("Would you like to save this data to a CSV file? (y/n) ")

if ans.lower() == "y":
    ans = input("Use set format?(y/n) ")
    if ans.lower() == "y":

        file_name ="steam_top_games_{}".format((datetime.now()).strftime("%m-%d-%Y_%H-%M-%S"))
    else:
        file_name = input("Enter the name of the file you would like to save the data to: ")
    game_data.to_csv(f"Steam Data/{file_name}.csv", index=False)

    
    print(f"Data saved to {file_name}.csv!")

