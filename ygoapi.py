import requests
from fuzzywuzzy import process


def random_card():
    """
    Gets a random card using the random card API route.
    :return: A dictionary with the card image and the json response requested.
    """
    random_request = requests.get("https://db.ygoprodeck.com/api/v7/randomcard.php").json()
    # Skill cards are boring.
    while random_request["type"] == "Skill Card":
        random_request = requests.get("https://db.ygoprodeck.com/api/v7/randomcard.php").json()
    card = random_request["card_images"][0]["image_url"]
    return {"card": card, "data": random_request}


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
        return result
    except KeyError:
        return result
