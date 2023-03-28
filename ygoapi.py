import json
import sqlite3

import requests
from fuzzywuzzy import process

import constants


def setup():
    """
    Writes the json data obtained from the API requests into a file, and populates the database with it.
    """
    request = requests.get("https://db.ygoprodeck.com/api/v7/cardinfo.php?misc=yes").json()
    # with open("cards.json", "w") as file:
    #    json.dump(request, file)
    connection = sqlite3.connect("card-database.db")
    cursor = connection.cursor()
    sql_file = open("card-database.sql")
    sql_commands = sql_file.read()
    cursor.executescript(sql_commands)
    card_count = 0
    for card in request['data']:
        card_id = card['id']
        card_count += 1
        cursor.execute("INSERT INTO Cards('id') VALUES(?)", (card_id,))
        print(card_count)
        for parameter in card:
            if parameter == 'id':
                pass
            elif parameter == 'race':
                query_text = f"UPDATE Cards SET subtype = ? WHERE id = {card_id}"
                cursor.execute(query_text, (card[parameter],))
            elif parameter == 'level' and "XYZ" in card['type']:
                query_text = f"UPDATE Cards SET rank = ? WHERE id = {card_id}"
                cursor.execute(query_text, (card[parameter],))
            else:
                query_text = f"UPDATE Cards SET {parameter} = ? WHERE id = {card_id}"
                try:
                    match parameter:
                        case 'card_prices':
                            cursor.execute(query_text, (json.dumps(card[parameter][0]),))
                        case 'misc_info':
                            cursor.execute(query_text, (json.dumps(card[parameter][0]),))
                            try:
                                cursor.execute(f"UPDATE Cards SET beta_name = ? WHERE id = {card_id}",
                                               (card[parameter][0]['beta_name'],))
                            except KeyError:
                                pass
                        case 'linkmarkers':
                            card[parameter].sort(key=constants.link_markers.index)
                            cursor.execute(query_text, (", ".join(card[parameter]),))
                        case 'card_images' | 'banlist_info':
                            cursor.execute(query_text, (json.dumps(card[parameter]),))
                        case _:
                            cursor.execute(query_text, (card[parameter],))
                except sqlite3.OperationalError:
                    continue
    connection.commit()
    cursor.close()
    connection.close()
    return


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
