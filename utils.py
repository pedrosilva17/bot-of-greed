import math
import re

import disnake
import requests
from PIL import Image
from disnake.utils import get

import Embeds
import constants


def count_whole_words(substring, string_list: list):
    pattern = re.compile(r"\b{}\b".format(substring), re.IGNORECASE)
    count = 0
    if " " in substring:
        string = " ".join(string_list)
        matches = pattern.findall(string.lower())
        count = len(matches)
    else:
        for string in string_list:
            matches = pattern.findall(string.lower())
            count += len(matches)
    return count

def search_wrapper(ctx, response):
    if (
        type(response) == str
    ):  # If card(s) not found, response is a simple error message
        embed = Embeds.ErrorEmbedBuilder(response)
        return embed
    elif len(response) == 1:
        card_info = response[0]
        emoji = None
        file = get_image(card_info)
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
                    marker_emojis = "".join(
                        [
                            constants.link_marker_emojis[marker]
                            for marker in value.split(", ")
                        ]
                    )
                    card_parameters += f"**{parameter}**: {marker_emojis}\n"
                case _:
                    if parameter in ["Level", "Rank", "Pendulum Scale"]:
                        emoji = get(
                            ctx.guild.emojis,
                            name=str(short_attr).replace(" ", "_").replace("-", "_"),
                        )
                    else:
                        emoji = get(
                            ctx.guild.emojis,
                            name=str(value).lower().replace(" ", "_").replace("-", "_"),
                        )
                    if parameter == "Archetype" and " (archetype)" in value:
                        value = value.replace(" (archetype)", "")

                    card_parameters += f"**{parameter}**: {value} "
                    if emoji is not None:
                        card_parameters += f"{emoji} "
                    if parameter in [
                        "Archetype",
                        "Attribute",
                        "Subtype",
                        "Pendulum Scale",
                    ]:
                        card_parameters += "\n"
        formats = ""
        for _format in card_info["misc_info"]["formats"]:
            if _format.lower() in ["tcg", "ocg", "goat"]:
                try:
                    formats += f"{_format} ({card_info['banlist_info'][f'ban_{_format.lower()}']}), "
                except KeyError:
                    formats += f"{_format} (Unlimited), "
            else:
                formats += f"{_format}, "
        formats = formats[:-2]
        embed = Embeds.SearchEmbedBuilder(
            title=card_info["name"],
            description=card_parameters,
            color=color,
            file=file,
            response=card_info,
            formats=formats,
        )
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
                    title = f"Found {len(response)} results."
                embed = Embeds.SearchEmbedBuilder(
                    title=title,
                    response=response,
                    page_num=page_count,
                    max_pages=max_pages,
                    cards_left=cards_left,
                    single=False,
                )
                page_count += 1
                pages.append(embed)
                cards_left -= page_max_results
    return pages


def get_image(card_info):
    card_image_list = card_info["card_images"]
    found_artwork = False
    for i in range(0, len(card_image_list)):
        card_id = card_image_list[i]["id"]
        try:
            file = disnake.File(
                f"artworks/artwork_{card_id}.jpg", filename=f"thumb_card.jpg"
            )
            found_artwork = True
            break
        except FileNotFoundError:
            continue
    if not found_artwork:
        for i in range(0, len(card_image_list)):
            card_id = card_image_list[i]["id"]
            try:
                file = disnake.File(
                    f"card_images/{card_id}.jpg", filename=f"thumb_card.jpg"
                )
                found_artwork = True
                break
            except FileNotFoundError:
                continue
    if not found_artwork:
        file = disnake.File("artworks/artwork_back.jpg", filename=f"thumb_card.jpg")
    return file


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
    response = requests.get(image)
    if response.status_code == 200:
        if "cropped" in image:
            with open(f"artworks/artwork_{card_id}.jpg", "wb") as f:
                f.write(response.content)
        else:
            with open(f"card_images/{card_id}.jpg", "wb") as f:
                f.write(response.content)
    return
