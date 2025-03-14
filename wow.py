import requests
from datetime import datetime, timezone

def futureEvents(country, plannedDate):
    # Construct the URL
    base_url = "https://jsonmock.hackerrank.com/api/events"
    first_page_url = f"{base_url}?country={country}&page=1"

    # Make the first API request
    response = requests.get(first_page_url)
    
    # Check if the request was successful
    if response.status_code != 200:
        print("Failed to fetch country information")
        return None
    
    # Extract data from the first page  
    json_data = response.json()
    total_pages = json_data['total_pages']
    data = json_data['data']

    # Fetch additional pages
    for page in range(2, total_pages + 1):  
        next_page_url = f"{base_url}?country={country}&page={page}"
        page_data = requests.get(next_page_url).json()['data']
        data.extend(page_data) 
    earliest_event = ''
    earliest_time = float('inf')
    latest_event = ''
    latest_time = float('-inf')

    # Process events
    for row in data:
        date = datetime.fromisoformat(row['date'].rstrip('Z'))
        unix_time = int(date.timestamp() * 1000)  # Convert to milliseconds
        
        if unix_time > plannedDate:
            print("Name:", row['name'], "Time:", unix_time)
            if unix_time < earliest_time:
                earliest_event = row['name']
                earliest_time = unix_time
            if unix_time > latest_time:
                latest_event = row['name']
                latest_time = unix_time
    return earliest_event, latest_event


print(futureEvents("Argentina", 1710527400000))
