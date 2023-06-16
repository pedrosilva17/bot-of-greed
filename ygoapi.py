import json
import sqlite3
import time

import requests
from fuzzywuzzy import process

import constants


def save_all_archetypes():
    headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0'
}   
    request_1 = requests.get("https://yugipedia.com/api.php?action=query&list=categorymembers&cmtitle=Category:Archetypes&cmlimit=500&format=json", headers=headers).json()
    
    time.sleep(2)
    
    request_2 = requests.get(f"https://yugipedia.com/api.php?action=query&list=categorymembers&cmtitle=Category:Archetypes&cmcontinue={request_1['continue']['cmcontinue']}&cmlimit=500&format=json", headers=headers).json()
    
    archetype_list = [arch['title'] for arch in request_1['query']['categorymembers'] + request_2['query']['categorymembers'] if "Category:" not in arch['title']][1:]
    
    archetype_string = "\n".join(archetype_list)
    
    with open('archetypes.txt', 'w') as file:
        file.write(archetype_string)
    
    with open('archetypes.txt', 'r') as file:
        string = file.read()
    print(string.split('\n'))
    

def random_card():
    """
    Gets a random card using the random card API route.
    :return: A dictionary with the card image and the json response requested.
    """
    random_request = requests.get("https://db.ygoprodeck.com/api/v7/randomcard.php").json()
    # Skill cards are boring.
    while random_request["type"] == "Skill Card":
        random_request = requests.get("https://db.ygoprodeck.com/api/v7/randomcard.php").json()
    card_image = random_request["card_images"][0]["image_url"]
    return {"card": card_image, "data": random_request}


def query(args):
    """
    Builds the URL according to the user's chosen parameters and uses it to request info through the API.
    :param args: The parameters passed when the command was called.
    :return: A JSON-encoded response from the API.
    """
    link = "https://db.ygoprodeck.com/api/v7/cardinfo.php?"
    for param in args.keys():
        if (args[param] is not None) & (param != "name"):
            link += f'{param}='
            if param in ("linkmarker", "type", "race", "attribute"):
                for marker in args[param].split(","):
                    link += f'{marker.strip()},'
                link = link[:-1] + '&'
            elif param == "sort":
                match args[param].lower():
                    case "attack":
                        link += 'atk&'
                    case "defense":
                        link += 'def&'
                    case _:
                        link += f'{args[param]}&'
            else:
                link += f'{args[param]}&'
    link += "misc=yes&"
    result = requests.get(link).json()
    try:
        if args["name"] is not None:
            """
            Rate all of the results (without taking the name parameter into account) in terms of similarity with the
            name parameter in a scale of 0-100, using the fuzzywuzzy library. Then, filters the list to only include
            the top-rated names.
            """
            name_list = [result["data"][i]["name"] for i in range(0, len(result["data"]))]
            closest_match_list = process.extract(args["name"].lower(), name_list, limit=len(name_list))
            new_list = list(filter(lambda x: x[1] == closest_match_list[0][1],
                                   closest_match_list))
            print(new_list)
            if len(new_list) != 0 and new_list[0][1] >= 60:
                link += f'name={new_list[0][0].replace("&", "").replace("#", "")}'
            else:
                link += f'name={args["name"].replace("&", "").replace("#", "")}'
            result = requests.get(link).json()
            if len(result["data"]) > 1:
                result["data"] = [result["data"][0]]
        print(result)
        return result
    except KeyError:
        return result
    