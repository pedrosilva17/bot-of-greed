import urllib
import utils
import requests
import os


def get_all_artworks():
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


get_all_artworks()

#
#
# def get_artwork(id):
#     return f'https://storage.googleapis.com/ygoprodeck.com/pics_artgame/{id}.jpg'


# def random_by_type(option):
#     cardlist = fil.filter(option, normalresponse)
#     limit = len(cardlist)
#     select = rand.randint(0, limit-1)
#     print(cardlist[select]["type"])
#     print(cardlist[select]["card_images"][0]["image_url"])


# if find_name.lower().split(" ")[0] == original_name.split(" ")[0]:
#     priority = 1
#     word_match = 1
#     boundary = min(len(find_name.lower().split(" ")), len(original_name.split(" ")))
#     for j in range(1, boundary):
#         if find_name.lower().split(" ")[j] == original_name.split(" ")[j]:
#             word_match += 1
#         elif (find_index != -1) & (find_index <= lowest_find_index):
#             lowest_find_index = find_index
#             if word_difference <= lowest_word_difference:
#                 args["name"] = find_name
#                 lowest_word_difference = word_difference
#     if highest_word_match <= word_match:
#         args["name"] = find_name
#         highest_word_match = word_match
# if (priority == 0) & (find_index != -1) & (find_index <= lowest_find_index):
#     lowest_find_index = find_index
#     if word_difference <= lowest_word_difference:
#         args["name"] = find_name
#         lowest_word_difference = word_difference

# def test(args):
#    response = requests.get(f"https://db.ygoprodeck.com/api/v7/cardinfo.php?type={args}").json()
#    print(response)
#    return response

"""Saving"""
"""
try:
    if len(response["data"]) == 1:
        short_response = response["data"][0]
        artwork = ygo.get_artwork(short_response["card_images"][0]["id"])
        dominant_color = get_dominant_color(artwork)
        boolean = True
        embed = discord.Embed(title=short_response["name"], description=short_response["desc"],
                              color=discord.Colour.from_rgb
                              (dominant_color[0], dominant_color[1], dominant_color[2]))
        embed.set_thumbnail(url=artwork)
        attributes = ["Type", "Race", "Archetype", "Level", "Link Rating", "ATK", "DEF", "Scale", "Link Markers"]
        for i in attributes:
            try:
                match i:
                    case "Link Rating":
                        embed.add_field(name=i, value=short_response["linkval"], inline=boolean)
                    case "ATK":
                        try:
                            if short_response["misc_info"][0]["question_atk"] == 1:
                                embed.add_field(name=i, value="?", inline=boolean)
                        except KeyError:
                            embed.add_field(name=i, value=short_response[i.lower()], inline=boolean)
                    case "DEF":
                        try:
                            if short_response["misc_info"][0]["question_atk"] == 1:
                                embed.add_field(name=i, value="?", inline=boolean)
                        except KeyError:
                            embed.add_field(name=i, value=short_response[i.lower()], inline=boolean)
                    case "Link Markers":
                        link_str = ", ".join(short_response["linkmarkers"])
                        embed.add_field(name=i, value=link_str, inline=boolean)
                    case _:
                        embed.add_field(name=i, value=short_response[i.lower()], inline=boolean)
            except KeyError:
                if i == "Archetype":
                    embed.add_field(name=i, value="N/A", inline=boolean)
                pass
        await ctx.send(embed=embed)
        print(short_response)
        return
    else:
        card_list = ""
        long_response = response["data"]
        right_bound = len(long_response), 20
        if max(right_bound) <= 20:
            await ctx.send("More than one card found. Here is the complete list:")
        else:
            await ctx.send("A lot of cards found! Here are the first 20:")
        for i in range(0, min(right_bound)):
            card_list += f'{long_response[i]["name"]} - {long_response[i]["type"]} - {long_response[i]["race"]}\n'
        await ctx.send(card_list)
        return
except KeyError:
    if response['error'].find("No card matching") != -1:
        new_value = response['error'].replace("see https://db.ygoprodeck.com/api-guide/", "type '/search info True'")
        response['error'] = new_value
    await ctx.send(f"Sorry, an error has occurred. Check it out:\n\n{response['error']}")
return
"""
