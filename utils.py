import math
import re

import disnake
import requests
from PIL import Image
from disnake.utils import get

import Embeds
import constants


def count_whole_words(substring, string_list: list):
    pattern = re.compile(r'\b{}\b'.format(substring), re.IGNORECASE)
    count = 0
    if ' ' in substring:
        string = ' '.join(string_list)
        matches = pattern.findall(string.lower())
        count = len(matches)
    else:
        for string in string_list:
            matches = pattern.findall(string.lower())
            count += len(matches)
    return count


# def embed_builder(ctx, embed_type, response=None, subtype=None, time=None):
#     """
#     Build a specific embed depending on the function where it is called.
#     Parameters:
#     -----------
#     :param ctx: The invocation context of the command.
#     :param embed_type: What the embed is used for (display information from /info, cards from /draw, the /guess game,
#     etc.
#     :param response: The JSON-encoded response obtained previously, defaults to None in case a request was not made
#     before.
#     :param subtype: Specifies the use of the embed further (for example, the type of game in /guess).
#     :param time: The uptime of the bot (displayed in /info).
#
#     :return: The new embed and optionally some information required for the command (for example, the name of the
#     randomly chosen card).
#     """
#
#     match embed_type:
#         case "Info":
#             embed = disnake.Embed(title="My name is Bot of Greed!",
#                                   description="I am a Discord bot created by [Pedro Silva]"
#                                               "(https://github.com/pedrosilva17), "
#                                               "that uses the [YGOPRODeck Database](https://db.ygoprodeck.com/) API.\n"
#                                               "All of my commands are slash commands.",
#                                   color=constants.greed_green)
#             file = disnake.File("profile.png", "profile.png")
#             embed.set_thumbnail(url="attachment://profile.png")
#             embed.add_field(name=f"{constants.emojis['alarm_clock']} I've been awake since:",
#                             value=f"<t:{time}:R>",
#                             inline=False)
#             embed.add_field(name=f"{constants.emojis['red_question_mark']} Having trouble with a command?",
#                             value="Use /guide and specify it in the command parameter.",
#                             inline=False)
#
#             return embed, file
#         case "Draw":
#             """
#             Creates and saves the image of the two cards combined. This is done because only 1 big image is allowed per embed.
#             """
#             card_a = queries.random_card()
#             card_b = queries.random_card()
#             join_two_images(card_a["id"], card_b["id"])
#             file = disnake.File("output/two_cards.jpg", "two_cards.jpg")
#
#             embed = disnake.Embed(title="Pot of Greed activates!", color=constants.greed_green)
#             embed.set_image(url="attachment://two_cards.jpg")
#             embed.set_footer(text=f"It's {card_a['name']} and {card_b['name']}!")
#             return embed, file
#         case "Guess":
#             file = None
#             card = queries.random_card()
#             name = card["name"]
#             match subtype:
#                 case "Card Text":
#                     desc = card["desc"]
#                     desc = desc.replace(name, "***Card Name***") + "\n\nWhich card is this?"
#                     embed = disnake.Embed(
#                         title="Guess the card!",
#                         color=constants.hat_purple,
#                         description=desc
#                     )
#                     thumbnail = disnake.File("artworks/artwork_81210420.jpg", "thumbnail.jpg")
#                     embed.set_thumbnail(url="attachment://thumbnail.jpg")
#                     return embed, thumbnail, name, card
#                 case "Artwork":
#                     error = True
#                     """
#                     In case the chosen card doesn't have an image in the database, choose another card
#                     """
#                     while error:
#                         images = dict(card).get("card_images")
#                         for i in range(0, len(json.loads(images))):
#                             card_id = json.loads(images)[i]["id"]
#                             try:
#                                 file = disnake.File(f"artworks/artwork_{card_id}.jpg", filename="artwork.jpg")
#                                 error = False
#                                 break
#                             except FileNotFoundError:
#                                 continue
#                         if error:
#                             card = queries.random_card()
#                             name = card["name"]
#                     embed = disnake.Embed(
#                         title="Guess the card!",
#                         color=constants.hat_purple
#                     )
#                     embed.set_image(url="attachment://artwork.jpg")
#                     return embed, file, name, card
#                 case "Guide":
#                     file = disnake.File("artworks/artwork_81210420.jpg", filename="magical_hats.jpg")
#                     help_guide = open('help/guess_help.txt', 'r').read().rstrip('\n')
#                     embed = disnake.Embed(
#                         title="Minigame: Guess",
#                         description=help_guide,
#                         color=constants.hat_purple)
#                     embed.set_thumbnail(
#                         url="attachment://magical_hats.jpg")
#                     return embed, file
#         case "Search":
#             match subtype:
#                 case "Card":
#                     start = timeit.default_timer()
#                     file = None
#                     if type(response) == str: # If card(s) not found, response is a simple error message
#                         embed = Embeds.ErrorEmbedBuilder(error_message=response)
#                         return embed
#                     right_bound = len(response)
#                     found_artwork = False
#                     if len(response) == 1:
#                         card_info = response[0]
#                         card_image_list = card_info["card_images"]
#                         for i in range(0, len(card_image_list)):
#                             card_id = card_image_list[i]["id"]
#                             try:
#                                 file = disnake.File(f"artworks/artwork_{card_id}.jpg",
#                                                     filename=f"thumb_{card_id}.jpg")
#                                 found_artwork = True
#                                 break
#                             except FileNotFoundError:
#                                 continue
#                         if not found_artwork:
#                             card_id = "back"
#                             file = disnake.File(f"artworks/artwork_{card_id}.jpg",
#                                                 filename=f"thumb_{card_id}.jpg")
#                         color = get_color_by_type(card_info["type"])
#                         card_parameters = ""
#                         for parameter in constants.attributes:
#                             short_attr = constants.short_terms[parameter]
#                             value = card_info.get(short_attr)
#                             if value == None: continue
#                             match parameter:
#                                 case "Attack" | "Defense":
#                                     try:
#                                         if card_info["misc_info"][f"question_{short_attr}"] == 1:
#                                             card_parameters += f"**{short_attr.upper()}**: ? "
#                                     except KeyError:
#                                         card_parameters += f"**{short_attr.upper()}**: {value} "
#                                 case "Link Markers":
#                                     marker_emojis = "".join([constants.link_marker_emojis[marker] for marker in value.split(", ")])
#                                     card_parameters += f"**{parameter}**: {marker_emojis}\n"
#                                 case _:
#                                     if parameter in ["Level", "Rank", "Pendulum Scale"]:
#                                         emoji = get(ctx.guild.emojis,
#                                                     name=str(short_attr).replace(" ", "_").replace("-", "_"))
#                                     else:
#                                         emoji = get(ctx.guild.emojis,
#                                                     name=str(value).lower().replace(" ", "_").replace("-", "_"))
#                                     card_parameters += f"**{parameter}**: {value} "
#                                     if emoji is not None:
#                                         card_parameters += f"{emoji} "
#                                     if parameter in ['Archetype', 'Attribute', 'Subtype', 'Pendulum Scale']:
#                                         card_parameters += "\n"
#                         formats = ""
#                         for format in card_info["misc_info"]["formats"]:
#                             if format.lower() in ["tcg", "ocg", "goat"]:
#                                 try:
#                                     formats += f"{format} ({card_info['banlist_info'][f'ban_{format.lower()}']}), "
#                                 except KeyError:
#                                     formats += f"{format} (Unlimited), "
#                             else:
#                                 formats += f'{format}, '
#                         formats = formats[:-2]
#                         embed = Embeds.SearchEmbedBuilder(title=card_info["name"],
#                                                           description=card_parameters,
#                                                           color=color,
#                                                           response=card_info)
#
#                         return embed
#                     else:
#                         pages = []
#                         cards_left = right_bound
#                         page_count = 1
#                         page_max_results = 10
#                         while cards_left > 0:
#                             for i in range(0, right_bound, 10):
#                                 if i == 0:
#                                     embed = disnake.Embed(title=f'Found {len(response)} results.',
#                                                             color=constants.greed_green)
#                                 else:
#                                     embed = disnake.Embed(color=constants.greed_green)
#                                 for j in range(min(10, cards_left)):
#                                     curr_card_info = response[i+j]
#                                     embed.add_field(name=curr_card_info["name"],
#                                                     value=f'{curr_card_info["type"]} | {curr_card_info["subtype"]}',
#                                                     inline=False)
#                                 cards_left -= 10
#                                 embed.set_footer(text=f'Page {page_count}/{math.ceil(right_bound / page_max_results)}')
#                                 page_count += 1
#                                 pages.append(embed)
#                         return pages, file
#                 case "Guide":
#                     file = disnake.File("artworks/artwork_74191528.jpg", filename="card_of_fate.jpg")
#                     help_search_1 = open('help/search_help_1.txt', 'r').read().rstrip('\n')
#                     help_search_2 = open('help/search_help_2.txt', 'r').read().rstrip('\n')
#                     embed_1 = disnake.Embed(
#                         title="Command: Search",
#                         description=help_search_1,
#                         color=constants.fate_blue)
#                     embed_1.set_footer(text='Page 1/2')
#                     embed_1.set_thumbnail(
#                         url="attachment://card_of_fate.jpg")
#                     embed_2 = disnake.Embed(
#                         title="Command: Search",
#                         description=help_search_2,
#                         color=constants.fate_blue)
#                     embed_2.set_footer(text='Page 2/2')
#                     embed_2.set_thumbnail(
#                         url="attachment://card_of_fate.jpg")
#                     embeds = [embed_1, embed_2]
#                     return embeds, file


def search_wrapper(ctx, response):
    if type(response) == str:  # If card(s) not found, response is a simple error message
        embed = Embeds.ErrorEmbedBuilder(response)
        return embed
    elif len(response) == 1:
        card_info = response[0]
        card_image_list = card_info["card_images"]
        found_artwork = False
        emoji = None
        for i in range(0, len(card_image_list)):
            card_id = card_image_list[i]["id"]
            try:
                file = disnake.File(f"artworks/artwork_{card_id}.jpg", filename=f"thumb_card.jpg")
                found_artwork = True
                break
            except FileNotFoundError:
                continue
        if not found_artwork:
            for i in range(0, len(card_image_list)):
                card_id = card_image_list[i]["id"]
                try:
                    file = disnake.File(f"card_images/{card_id}.jpg", filename=f"thumb_card.jpg")
                    found_artwork = True
                    break
                except FileNotFoundError:
                    continue
        if not found_artwork:
            card_id = "back"
            file = disnake.File(f"artworks/artwork_{card_id}.jpg",
                                filename=f"thumb_card.jpg")
        color = get_color_by_type(card_info["type"])
        card_parameters = ""
        for parameter in constants.attributes:
            short_attr = constants.short_terms[parameter]
            value = card_info.get(short_attr)
            if value is None:
                continue
            match parameter:
                case "Attack" | "Defense":
                    try:
                        if card_info["misc_info"][f"question_{short_attr}"] == 1:
                            card_parameters += f"**{short_attr.upper()}**: ? "
                    except KeyError:
                        card_parameters += f"**{short_attr.upper()}**: {value} "
                case "Link Markers":
                    marker_emojis = "".join([constants.link_marker_emojis[marker]
                                             for marker in value.split(", ")])
                    card_parameters += f"**{parameter}**: {marker_emojis}\n"
                case _:
                    if parameter in ["Level", "Rank", "Pendulum Scale"]:
                        emoji = get(ctx.guild.emojis,
                                    name=str(short_attr).replace(" ", "_").replace("-", "_"))
                    else:
                        emoji = get(ctx.guild.emojis,
                                    name=str(value).lower().replace(" ", "_").replace("-", "_"))
                    if parameter == "Archetype" and " (archetype)" in value:
                        value = value.replace(" (archetype)", "")

                    card_parameters += f"**{parameter}**: {value} "
                    if emoji is not None:
                        card_parameters += f"{emoji} "
                    if parameter in ['Archetype', 'Attribute', 'Subtype', 'Pendulum Scale']:
                        card_parameters += "\n"
        formats = ""
        for _format in card_info["misc_info"]["formats"]:
            if _format.lower() in ["tcg", "ocg", "goat"]:
                try:
                    formats += f"{_format} ({card_info['banlist_info'][f'ban_{_format.lower()}']}), "
                except KeyError:
                    formats += f"{_format} (Unlimited), "
            else:
                formats += f'{_format}, '
        formats = formats[:-2]
        embed = Embeds.SearchEmbedBuilder(
            title=card_info["name"],
            description=card_parameters, color=color, file=file, response=card_info,
            formats=formats)
        return embed
    else:
        pages = []
        cards_left = len(response)
        page_count = 1
        page_max_results = constants.max_results
        max_pages = math.ceil(cards_left / page_max_results)
        while cards_left > 0:
            for i in range(0, len(response), page_max_results):
                title = ""
                if i == 0:
                    title = f'Found {len(response)} results.'
                embed = Embeds.SearchEmbedBuilder(
                    title=title, response=response, page_num=page_count, max_pages=max_pages,
                    cards_left=cards_left, single=False)
                page_count += 1
                pages.append(embed)
                cards_left -= page_max_results
    return pages


"""Other utility functions"""


def get_color_by_type(_type):
    """
    Return a color to use in a card's embed based on the card's type.
    Parameters:
    -----------
    :param _type: The type of the card.

    :return: The hex code for the dominant color.
    """
    match _type:
        case _type if _type.count("Spell") > 0:
            color = constants.spell_green
        case _type if _type.count("Trap") > 0:
            color = constants.trap_pink
        case _type if _type.count("Fusion") > 0:
            color = constants.fusion_purple
        case _type if _type.count("Synchro") > 0:
            color = constants.synchro_white
        case _type if _type.count("XYZ") > 0:
            color = constants.xyz_black
        case _type if _type.count("Link") > 0:
            color = constants.link_blue
        case _type if _type.count("Normal") > 0:
            color = constants.normal_yellow
        case _type if _type.count("Skill") > 0:
            color = constants.skill_blue
        case _:
            color = constants.effect_orange
    return color


def join_two_images(im1, im2):
    """
    Join two images side-by-side into a single file. Useful for embeds.
    Parameters:
    -----------
    :param im1: The image that will appear on the left.
    :param im2: The image that will appear on the right.
    """

    i1 = Image.open(f"card_images/{im1}.jpg")
    i1 = i1.resize((421, 614), Image.ANTIALIAS)
    i2 = Image.open(f"card_images/{im2}.jpg")
    i2 = i2.resize((421, 614), Image.ANTIALIAS)

    draw = Image.new("RGB", (i1.width + i2.width, max(i1.height, i2.height)))
    draw.paste(i1, (0, 0))
    draw.paste(i2, (i1.width, 0))
    draw.save(f"output/two_cards.jpg")
    return


def save_image(image, card_id):
    """
    Simply save an image locally given an url.
    :param image: The image url.
    :param card_id: The id used in the save image name (correspondent to the card id).
    """
    response_1 = requests.get(image)
    if response_1.status_code == 200:
        with open(f"artworks/artwork_{card_id}.jpg", 'wb') as f:
            f.write(response_1.content)
    return


def save_card(image, card_id):
    response = requests.get(image)
    if response.status_code == 200:
        with open(f"card_images/{card_id}.jpg", 'wb') as f:
            f.write(response.content)
    return
