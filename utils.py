import math
from PIL import Image
import colorthief
import urllib.request
import disnake
from disnake.utils import get
import constants
import ygoapi as ygo

"""
Functions that are generally useful or related to the construction of embeds.
"""


def embed_builder(ctx, embed_type, response=None, subtype=None, time=None):
    """
    Build a specific embed depending on the function where it is called.
    Parameters:
    -----------
    :param ctx: The invocation context of the command.
    :param embed_type: What the embed is used for (display information from /info, cards from /draw, the /guess game,
    etc.
    :param response: The JSON-encoded response obtained previously, defaults to None in case a request was not made
    before.
    :param subtype: Specifies the use of the embed further (for example, the type of game in /guess).
    :param time: The uptime of the bot (displayed in /info).

    :return: The new embed and optionally some information required for the command (for example, the name of the
    randomly chosen card).
    """
    match embed_type:
        case "Info":
            embed = disnake.Embed(title="My name is Bot of Greed!",
                                  description="I am a Discord bot created by [Pedro Silva]"
                                              "(https://github.com/pedrosilva17), "
                                              "that uses the [YGOPRODeck Database](https://db.ygoprodeck.com/) API.\n"
                                              "All of my commands are slash commands.",
                                  color=constants.greed_green)
            file = disnake.File("profile.png", "profile.png")
            embed.set_thumbnail(url="attachment://profile.png")
            embed.add_field(name=f"{constants.emojis['alarm_clock']} I've been awake since:",
                            value=f"<t:{time}:R>",
                            inline=False)
            embed.add_field(name=f"{constants.emojis['red_question_mark']} Having trouble with a command?",
                            value="Use /guide and specify it in the command parameter.",
                            inline=False)

            return embed, file
        case "Draw":
            """
            Creates and saves the image of the two cards combined. This is done because only 1 big image is allowed per 
            embed).
            """
            card_a = ygo.random_card()
            card_b = ygo.random_card()
            join_two_images(card_a["card"], card_b["card"])
            file = disnake.File("output/two_cards.jpg", "two_cards.jpg")

            embed = disnake.Embed(title="Pot of Greed activates!", color=constants.greed_green)
            embed.set_image(url="attachment://two_cards.jpg")
            embed.set_footer(text=f"It's {card_a['data']['name']} and {card_b['data']['name']}!")
            return embed, file
        case "Guess":
            file = None
            card = ygo.random_card()
            name = card["data"]["name"]
            match subtype:
                case "Card Text":
                    desc = card["data"]["desc"]
                    desc = desc.replace(name, "***Card Name***") + "\n\nWhich card is this?"
                    embed = disnake.Embed(
                        title="Guess the card!",
                        color=constants.hat_purple,
                        description=desc
                    )
                    thumbnail = disnake.File("artworks/artwork_81210420.jpg", "thumbnail.jpg")
                    embed.set_thumbnail(url="attachment://thumbnail.jpg")
                    return embed, thumbnail, name, card
                case "Artwork":
                    card_info = ygo.query({"name": name})
                    error = True
                    """
                    In case the chosen card doesn't have an image in the database, choose another card
                    """
                    while error:
                        try:
                            for i in range(0, len(card_info["data"][0]["card_images"])):
                                card_id = card_info["data"][0]["card_images"][i]["id"]
                                try:
                                    file = disnake.File(f"artworks/artwork_{card_id}.jpg", filename="artwork.jpg")
                                    error = False
                                    break
                                except FileNotFoundError:
                                    continue
                        except KeyError:
                            pass
                        if error:
                            card = ygo.random_card()
                            name = card["data"]["name"]
                            card_info = ygo.query({"name": name})
                    color = get_dominant_color(f"artworks/artwork_{card_id}.jpg")
                    embed = disnake.Embed(
                        title="Guess the card!",
                        color=disnake.Colour.from_rgb(color[0], color[1], color[2])
                    )
                    embed.set_image(url="attachment://artwork.jpg")
                    return embed, file, name, card
                case "Guide":
                    file = disnake.File("artworks/artwork_81210420.jpg", filename="magical_hats.jpg")
                    help_guide = open('help/guess_help.txt', 'r').read().rstrip('\n')
                    embed = disnake.Embed(
                        title="Minigame: Guess",
                        description=help_guide,
                        color=constants.hat_purple)
                    embed.set_thumbnail(
                        url="attachment://magical_hats.jpg")
                    return embed, file
        case "Search":
            match subtype:
                case "Card":
                    file = None
                    try:
                        right_bound = len(response["data"])
                        found_artwork = False
                        if len(response["data"]) == 1:
                            short_response = response["data"][0]
                            for i in range(0, len(short_response["card_images"])):
                                card_id = short_response["card_images"][i]["id"]
                                try:
                                    file = disnake.File(f"artworks/artwork_{card_id}.jpg",
                                                        filename=f"thumb_{card_id}.jpg")
                                    found_artwork = True
                                    break
                                except FileNotFoundError:
                                    continue
                            if not found_artwork:
                                card_id = "back"
                                file = disnake.File(f"artworks/artwork_{card_id}.jpg",
                                                    filename=f"thumb_{card_id}.jpg")
                            color = get_dominant_color(f"artworks/artwork_{card_id}.jpg")
                            description = ""
                            attributes = constants.attributes
                            for i in attributes:
                                try:
                                    match i:
                                        case "Level":
                                            if "XYZ" in short_response["type"]:
                                                description += f"**Rank**: {short_response[i.lower()]} "
                                            else:
                                                description += f"**{i}**: {short_response[i.lower()]} "
                                        case "Link Rating":
                                            description += f"**{i}**: {short_response['linkval']} "
                                        case "ATK":
                                            try:
                                                if short_response["misc_info"][0]["question_atk"] == 1:
                                                    description += f"**{i}**: ? "
                                            except KeyError:
                                                description += f"**{i}**: {short_response[i.lower()]} "
                                        case "DEF":
                                            try:
                                                if short_response["misc_info"][0]["question_atk"] == 1:
                                                    description += f"**{i}**: ? "
                                            except KeyError:
                                                description += f"**{i}**: {short_response[i.lower()]} "
                                        case "Link Markers":
                                            link_str = ", ".join(short_response["linkmarkers"])
                                            description += f"**{i}**: {link_str} "
                                        case "Archetype" | "Attribute":
                                            try:
                                                emoji = get(ctx.guild.emojis,
                                                            name=str(short_response[i.lower()]).lower()
                                                            .replace(" ", "_").replace("-", "_"))
                                                description += f"**{i}**: {short_response[i.lower()]}"
                                                if emoji is not None:
                                                    description += f" {emoji}\n"
                                                else:
                                                    description += "\n"
                                            except KeyError:
                                                pass
                                        case _:
                                            description += f"**{i}**: {short_response[i.lower()]} "
                                            emoji = get(ctx.guild.emojis, name=str(short_response[i.lower()]).lower()
                                                        .replace(" ", "_").replace("-", "_"))
                                            if emoji is not None:
                                                description += f"{emoji} "
                                except KeyError:
                                    pass
                            formats = ""
                            for i in short_response["misc_info"][0]["formats"]:
                                formats += f'{i}, '
                            formats = formats[:-2]
                            embed = disnake.Embed(title=short_response["name"],
                                                  description=description,
                                                  color=disnake.Colour.from_rgb
                                                  (color[0], color[1], color[2]))
                            embed.set_thumbnail(url=f"attachment://thumb_{card_id}.jpg")
                            embed.add_field(name="Card text:", value=short_response["desc"], inline=False)
                            embed.add_field(name="Card prices:",
                                            value=f'Cardmarket: {short_response["card_prices"][0]["cardmarket_price"]}€'
                                                  f'\n'
                                                  f'TCGPlayer: ${short_response["card_prices"][0]["tcgplayer_price"]}',
                                            inline=False)
                            footer_text = f'ID: {short_response["id"]} | Views: ' \
                                          f'{short_response["misc_info"][0]["views"]} | Formats: {formats} | '
                            if "OCG" not in formats:
                                footer_text += f'Release Date (TCG): {short_response["misc_info"][0]["tcg_date"]}'
                            else:
                                footer_text += f'Release Date (OCG): {short_response["misc_info"][0]["ocg_date"]}'
                            embed.set_footer(text=footer_text)
                            return embed, file
                        else:
                            pages = []
                            cards_left = right_bound
                            page_count = 1
                            page_max_results = 10
                            for i in range(0, right_bound, 10):
                                if cards_left < 0:
                                    break
                                if i == 0:
                                    embed = disnake.Embed(title=f'Found {len(response["data"])} results.',
                                                          color=constants.greed_green)
                                else:
                                    embed = disnake.Embed(color=constants.greed_green)
                                for j in range(min(10, cards_left)):
                                    long_response = response["data"][i]
                                    embed.add_field(name=long_response["name"],
                                                    value=f'{long_response["type"]} | {long_response["race"]}',
                                                    inline=False)
                                    i += 1
                                cards_left -= 10
                                embed.set_footer(text=f'Page {page_count}/{math.ceil(right_bound / page_max_results)}')
                                page_count += 1
                                pages.append(embed)
                            if found_artwork:
                                return pages, file
                            else:
                                return pages, False
                    except KeyError:
                        if response['error'].find("No card matching") != -1:
                            new_value = response['error'].replace("see https://db.ygoprodeck.com/api-guide/",
                                                                  "type '/guide search'")
                            response['error'] = new_value
                        return "err", file
                case "Guide":
                    file = disnake.File("artworks/artwork_74191528.jpg", filename="card_of_fate.jpg")
                    help_search_1 = open('help/search_help_1.txt', 'r').read().rstrip('\n')
                    help_search_2 = open('help/search_help_2.txt', 'r').read().rstrip('\n')
                    embed_1 = disnake.Embed(
                        title="Command: Search",
                        description=help_search_1,
                        color=constants.fate_blue)
                    embed_1.set_footer(text=f'Page 1/2')
                    embed_1.set_thumbnail(
                        url="attachment://card_of_fate.jpg")
                    embed_2 = disnake.Embed(
                        title="Command: Search",
                        description=help_search_2,
                        color=constants.fate_blue)
                    embed_2.set_footer(text=f'Page 2/2')
                    embed_2.set_thumbnail(
                        url="attachment://card_of_fate.jpg")
                    embeds = [embed_1, embed_2]
                    return embeds, file


"""Other utility functions"""


def get_dominant_color(card):
    """
    Get a card artwork's dominant color using the colorthief library.
    Parameters:
    -----------
    :param card: The card to extract the color from.

    :return: The hex code for the dominant color.
    """
    color_palette = colorthief.ColorThief(card)
    dominant_color = color_palette.get_color(quality=1)
    return dominant_color


def join_two_images(im1, im2):
    """
    Join two images side-by-side into a single file. Useful for embeds.
    Parameters:
    -----------
    :param im1: The image that will appear on the left.
    :param im2: The image that will appear on the right.
    """
    urllib.request.urlretrieve(im1, "output/card_1.jpg"), urllib.request.urlretrieve(im2, "output/card_2.jpg")

    i1 = Image.open("output/card_1.jpg")
    i1 = i1.resize((421, 614), Image.ANTIALIAS)
    i2 = Image.open("output/card_2.jpg")
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
    :param card_id: The id used in the save image name (correspondant to the card id).
    """
    urllib.request.urlretrieve(image, f"artworks/artwork_{card_id}.jpg")
    return
