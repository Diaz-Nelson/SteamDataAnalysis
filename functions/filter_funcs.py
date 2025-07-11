from datetime import datetime

def filter_data_by_genres(df, selected_genres):
    if selected_genres:
        # Filter rows where all selected genres are present in the Genres list
        filtered_df = df[df['Genres'].apply(lambda genres: all(genre in genres for genre in selected_genres))]
    else:
        filtered_df = df
    
    return filtered_df

def search_game(df, query):
    if query:
        # Filter the DataFrame where the 'Game' column contains the search query (case insensitive)
        filtered_df = df[df['Game'].str.contains(query, case=False, na=False)]
    else:
        filtered_df = df 
    return filtered_df
def filter_data_by_tags(df, selected_tags):
    if selected_tags:
        # Filter rows where all selected genres are present in the Genres list
        filtered_df = df[df['Tags'].apply(lambda tags: all(tag in tags for tag in selected_tags))]
    else:
        filtered_df = df  # If no genres selected, return the whole DataFrame
    
    return filtered_df

def filter_dfs(df, genres=None, tags=None, query=""):
    if genres:
        df = filter_data_by_genres(df, genres)
    if tags:
        df = filter_data_by_tags(df, tags)
    if query:
        df = search_game(df, query)
    return df

def clean_str(fileName):
    try:
        fileName = datetime.strptime(fileName, "%m-%d-%Y_%H-%M-%S").strftime("%B %d, %Y at %I:%M:%S %p")
        return fileName
    except:
        return fileName