import os
import urllib

import requests

import utils


def get_all_artworks():
    """
    Download all the available artworks and save them locally in the "artworks" folder. Skips all cards that don't have
    an artwork stored and displays their names in the console.
    """
    broken_id_list = []
    request = requests.get("https://db.ygoprodeck.com/api/v7/cardinfo.php?").json()
    counter = 0
    for i in range(len(request["data"])):
        card_id = request["data"][i]["id"]
        if os.path.exists(f'artworks/artwork_{card_id}.jpg'):
            print("skip")
            continue
        counter += 1
        image = f'https://images.ygoprodeck.com/images/cards_cropped/{card_id}.jpg'
        try:
            utils.save_image(image, card_id)
        except urllib.error.HTTPError:
            print("error!")
            broken_id_list.append(request["data"][i]["name"])
        print(counter)
    for i in broken_id_list:
        print(i)
    return


def get_all_card_images():
    broken_id_list = []
    request = requests.get("https://db.ygoprodeck.com/api/v7/cardinfo.php?").json()
    counter = 0
    for i in range(len(request["data"])):
        card_id = request["data"][i]["id"]
        if os.path.exists(f'card_images/{card_id}.jpg'):
            print("skip")
            continue
        counter += 1
        image = f'https://images.ygoprodeck.com/images/cards/{card_id}.jpg'
        try:
            utils.save_card(image, card_id)
        except urllib.error.HTTPError:
            print("error!")
            broken_id_list.append(request["data"][i]["name"])
        print(counter)
    for i in broken_id_list:
        print(i)
    return
