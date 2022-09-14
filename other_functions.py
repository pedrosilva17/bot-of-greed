import urllib
import utils
import requests
import os


def get_all_artworks():
    """
    Download all the available artworks and save them locally in the "artworks" folder. Skips all cards that don't have
    an artwork stored and displays their names in the console.
    """
    broken_id_list = []
    request = requests.get("https://db.ygoprodeck.com/api/v7/cardinfo.php?").json()
    counter = 0
    for i in range(0, len(request["data"])):
        card_id = request["data"][i]["id"]
        if os.path.exists(f'artworks/artwork_{card_id}.jpg'):
            continue
        print("missing card!")
        counter += 1
        image = f'https://storage.googleapis.com/ygoprodeck.com/pics_artgame/{card_id}.jpg'
        try:
            utils.save_image(image, card_id)
        except urllib.error.HTTPError:
            print("error!")
            broken_id_list.append(request["data"][i]["name"])
    print(counter)
    for i in broken_id_list:
        print(i)
    return
