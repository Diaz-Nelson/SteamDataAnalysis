import requests
from bs4 import BeautifulSoup
cookies = {
        "birthtime": "568022401",  # Fake birthdate (epoch time, 1988)
        "mature_content": "1",     # Accept mature content
        "lastagecheckage": "1-0-1988"  # Fake last age check
    }
review_score = {"Overwhelmingly Positive":9,"Very Positive":8,"Positive":7,"Mostly Positive":6,"Mixed":5,"Mostly Negative":4,"Negative":3,"Very Negative":2,"Overwhelmingly Negative":1}

def get_steam_reviews_tags(app_id):
    url = f"https://store.steampowered.com/app/{app_id}/"
    
    # Bypass age check by setting the 'wants_mature_content' cookie
    global cookies
    
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, cookies=cookies)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        tags = [tag.text.strip() for tag in soup.select(".app_tag")][:-1]
        review_summary = [[num.text.strip(), num.find_next_sibling("span").text.strip()[1:-1]] for i, num in enumerate(soup.select(".game_review_summary")) if i < 2]
        try:
            review_summary[0][1] = int(review_summary[0][1].replace(",",""))
            review_summary[1][1] = int(review_summary[0][1].replace(",",""))
        except:
            review_summary[1][1] = review_summary[0][1]

        return {"Tags": tags, "Recent Review Score": review_score[review_summary[0][0]], "Recent Review Count": review_summary[0][1],"All Review Score": review_score[review_summary[1][0]],"All Review Count": review_summary[1][1]}
    else:
        return {"Tags": None, "Recent Review Score": None,"Recent Review Count":None,"All Review Score":None,"All Review Count":None}

# Example: Get tags for Cyberpunk 2077 (App ID: 1091500)
tags = get_steam_reviews_tags(1091500)
print(tags)
