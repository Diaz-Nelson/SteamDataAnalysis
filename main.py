import data_funcs as funcs
from datetime import datetime
from ml_funcs import forest_ml

start = datetime.now()

game_data,details_failed,game_failed,tags_failed = funcs.get_game_data(8)
print("Time taken to get data: ",datetime.now()-start)
print(game_data.head(10))

print("Game Failed: ",game_failed)
print("Details Failed: ",details_failed)
print("Tags Failed: ",tags_failed)

ans = input("Would you like to save this data to a CSV file? (y/n) ")

if ans.lower() == "y":
    ans = input("Use set format?(y/n) ")
    if ans.lower() == "y":
        today = str(datetime.now().date())
        file_name ="steam_top_games_{}".format((datetime.now()).strftime("%m-%d-%Y_%H-%M-%S"))
    else:
        file_name = input("Enter the name of the file you would like to save the data to: ")
    game_data.to_csv(f"{file_name}.csv", index=False)
    
    print(f"Data saved to {file_name}.csv!")

