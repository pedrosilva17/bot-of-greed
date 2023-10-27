import json
import os
import sqlite3
import urllib

import requests
import time

import utils
import constants


headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0"
}


def setup(
    get_artworks=False,
    get_card_images=False,
    get_archetypes=False,
    map_archetypes=False,
):
    if get_artworks:
        get_all_card_images(get_artworks=True)
    if get_card_images:
        get_all_card_images(get_artworks=False)
    if get_archetypes:
        get_all_archetypes()
    if map_archetypes:
        get_archetype_members()
    populate_database()
    return


def populate_database():
    """
    Writes the json data obtained from the API requests into a file, and populates the database with it.
    """
    print("Populating database...")
    request = requests.get(
        "https://db.ygoprodeck.com/api/v7/cardinfo.php?misc=yes"
    ).json()
    connection = sqlite3.connect("card-database.db")
    cursor = connection.cursor()
    sql_file = open("card-database.sql")
    sql_commands = sql_file.read()
    cursor.executescript(sql_commands)
    card_count = 0

    with open("setup_files/archetype_mapping.json", "r") as file:
        arch_mapping = json.loads(file.read())

    for card in request["data"]:
        card_id = card["id"]
        card_count += 1
        cursor.execute("INSERT INTO Cards('id') VALUES(?)", (card_id,))
        print(card_count)
        for parameter in card:
            if parameter == "id":
                pass
            elif parameter == "race":
                query_text = f"UPDATE Cards SET subtype = ? WHERE id = {card_id}"
                cursor.execute(query_text, (card[parameter],))
            elif parameter == "level" and "XYZ" in card["type"]:
                query_text = f"UPDATE Cards SET rank = ? WHERE id = {card_id}"
                cursor.execute(query_text, (card[parameter],))
            else:
                query_text = f"UPDATE Cards SET {parameter} = ? WHERE id = {card_id}"
                try:
                    match parameter:
                        case "card_prices":
                            cursor.execute(
                                query_text, (json.dumps(card[parameter][0]),)
                            )
                        case "misc_info":
                            cursor.execute(
                                query_text, (json.dumps(card[parameter][0]),)
                            )
                            try:
                                cursor.execute(
                                    f"UPDATE Cards SET beta_name = ? WHERE id = {card_id}",
                                    (card[parameter][0]["beta_name"],),
                                )
                            except KeyError:
                                pass
                        case "linkmarkers":
                            card[parameter].sort(key=constants.link_markers.index)
                            cursor.execute(query_text, (", ".join(card[parameter]),))
                        case "card_images" | "banlist_info":
                            cursor.execute(query_text, (json.dumps(card[parameter]),))
                        case "archetype":
                            archetype = arch_mapping.get(card["name"], "empty")
                            if archetype != "empty":
                                cursor.execute(query_text, (archetype,))
                        case _:
                            cursor.execute(query_text, (card[parameter],))
                except sqlite3.OperationalError:
                    continue
    connection.commit()
    cursor.close()
    connection.close()


def get_all_card_images(get_artworks=False):
    """
    Download all the available artworks/card images and save them locally in the "artworks"/"card_images" folder. Skips all cards that don't have
    an image available and displays their names in the console.
    """
    broken_id_list = []
    request = requests.get("https://db.ygoprodeck.com/api/v7/cardinfo.php?").json()
    counter = 0
    print("Downloading images...")
    for i in range(len(request["data"])):
        card_id = request["data"][i]["id"]
        if get_artworks:
            if os.path.exists(f"artworks/artwork_{card_id}.jpg"):
                print("skip")
                continue
            counter += 1
            image = f"https://images.ygoprodeck.com/images/cards_cropped/{card_id}.jpg"
        else:
            if os.path.exists(f"card_images/{card_id}.jpg"):
                print("skip")
                continue
            counter += 1
            image = f"https://images.ygoprodeck.com/images/cards/{card_id}.jpg"
        try:
            utils.save_image(image, card_id)
        except urllib.error.HTTPError:
            print("error!")
            broken_id_list.append(request["data"][i]["name"])
        print(counter)
        time.sleep(0.3)
    for i in broken_id_list:
        print(i)
    return


def get_all_archetypes():
    print("Getting archetypes...")
    request_1 = requests.get(
        "https://yugipedia.com/api.php?action=query&list=categorymembers&cmtitle=Category:Archetypes&cmlimit=500&format=json",
        headers=headers,
    ).json()

    time.sleep(0.5)

    request_2 = requests.get(
        f"https://yugipedia.com/api.php?action=query&list=categorymembers&cmtitle=Category:Archetypes&cmcontinue={request_1['continue']['cmcontinue']}&cmlimit=500&format=json",
        headers=headers,
    ).json()

    archetype_list = [
        arch["title"]
        for arch in request_1["query"]["categorymembers"]
        + request_2["query"]["categorymembers"]
        if "Category:" not in arch["title"]
    ][1:]

    archetype_string = "\n".join(archetype_list)

    with open("setup_files/archetypes.txt", "w") as file:
        file.write(archetype_string)

    with open("setup_files/archetypes.txt", "r") as file:
        string = file.read()
    print(string.split("\n"))


def get_archetype_members():
    print("Getting archetype members...")
    with open("setup_files/archetypes.txt", "r") as file:
        archetypes = file.read().split("\n")
    file.close()

    with open("setup_files/archetype_mapping.json", "r") as file:
        arch_mapping = json.loads(file.read())

    empty_archetypes = []

    counter = 1
    for arch in archetypes:
        try:
            request = requests.get(
                f"https://yugipedia.com/api.php?action=askargs&conditions=Archseries::{arch}]]OR[[{arch.lower()}&format=json",
                headers=headers,
            ).json()
            name_list = list(request["query"]["results"].keys())
        except AttributeError:
            print("empty archetype!")
            empty_archetypes.append(arch)
            continue
        for name in name_list:
            if arch_mapping.get(name, "empty") == "empty":
                arch_mapping[name] = arch
            else:
                arch_mapping[name] = arch_mapping.get(name) + "," + arch
        time.sleep(0.5) # Don't want to overload the API with requests
        print(f"{counter}/{len(archetypes)}")
        if counter % 5 == 0:
            json_obj = json.dumps(arch_mapping)
            with open("setup_files/archetype_mapping.json", "w") as file:
                file.write(json_obj)
            file.close()
        counter += 1

    print(arch_mapping)
    json_obj = json.dumps(arch_mapping)
    with open("setup_files/archetype_mapping.json", "w") as file:
        file.write(json_obj)
    file.close()

    print(empty_archetypes)
