import json
import re
from operator import methodcaller

import disnake

import constants
import database
import utils


class EmbedBuilder(disnake.Embed):
    """Generic embed builder class to be extended by more specific embed builder classes. Extension of the discord Embed
     class.

    Args:
        Embed (disnake.Embed): The discord Embed class that's being extended.
    """

    def __init__(
        self,
        title: str,
        description: str = "",
        color: int = constants.greed_green,
        file: disnake.File = None,
    ):
        """_summary_

        Args:
            title (str): _description_
            description (str, optional): A description for the embed. Defaults to "".
            color (str, optional): _description_. Defaults to constants.greed_green.
            file (disnake.File, optional): _description_. Defaults to None.
        """
        super().__init__()
        self.title = title
        self.description = description
        self.color = color
        self.file = file


class InfoEmbedBuilder(EmbedBuilder):
    """The embed builder related to information about the bot and its author.

    Args:
        EmbedBuilder (EmbedBuilder): The generic embed builder class being inherited.
    """

    def __init__(self, title: str, description: str, file: disnake.File, time: int):
        super().__init__(title=title, description=description, file=file)
        self.time = time
        super().set_thumbnail(url="attachment://profile.png")
        super().add_field(
            name=f"{constants.emojis['alarm_clock']} I've been awake since:",
            value=f"<t:{time}:R>",
            inline=False,
        )
        super().add_field(
            name=f"{constants.emojis['red_question_mark']} Having trouble with a command?",
            value="Use /guide and specify it in the command parameter.",
            inline=False,
        )


class DrawEmbedBuilder(EmbedBuilder):
    def __init__(self, title: str):
        no_artwork = True
        while no_artwork:
            card_a = database.random_card()
            card_b = database.random_card()
            try:
                utils.join_two_images(card_a["id"], card_b["id"])
                no_artwork = False
            except FileNotFoundError:
                pass

        file = disnake.File("output/two_cards.jpg", filename="two_cards.jpg")

        super().__init__(title=title, file=file)
        super().set_image(url="attachment://two_cards.jpg")
        super().set_footer(text=f"It's {card_a['name']} and {card_b['name']}!")


class GuessEmbedBuilder(EmbedBuilder):
    def __init__(
        self,
        title: str,
        color: str,
        file: disnake.File = None,
        description: str = "",
        mode: str = "",
    ):
        card = database.random_card()
        self.card = card
        match mode:
            case "Card Text":
                thumb = disnake.File("artworks/artwork_81210420.jpg", "thumbnail.jpg")
                description = card["desc"]
                description = (
                    description.replace(card["name"], "***Card Name***")
                    + "\n\nWhich card is this?"
                )

                super().__init__(
                    title=title, description=description, color=color, file=thumb
                )
                self.mode = mode
                super().set_thumbnail(url="attachment://thumbnail.jpg")
            case "Artwork":
                """
                In case the chosen card doesn't have an image in the database, choose another card
                """
                error = True
                while error:
                    images = dict(card).get("card_images")
                    for i in range(0, len(json.loads(images))):
                        card_id = json.loads(images)[i]["id"]
                        try:
                            file = disnake.File(
                                f"artworks/artwork_{card_id}.jpg",
                                filename="artwork.jpg",
                            )
                            error = False
                            break
                        except FileNotFoundError:
                            continue
                    if error:
                        card = database.random_card()
                        self.card = card
                super().__init__(
                    title=title, description=description, color=color, file=file
                )
                self.mode = mode
                super().set_image(url="attachment://artwork.jpg")


class SearchEmbedBuilder(EmbedBuilder):
    def __init__(
        self,
        title: str = "",
        description: str = "",
        color: str = constants.greed_green,
        file: disnake.File = None,
        response: dict = None,
        formats: str = "",
        page_num: int = 1,
        max_pages: int = 1,
        cards_left: int = 1,
        single: bool = True,
    ):
        if single:
            card_info = response
            super().__init__(
                title=title, description=description, color=color, file=file
            )
            super().set_thumbnail(url=f"attachment://thumb_card.jpg")
            self.__parse_card_text(card_info["desc"], card_info["type"])
            super().add_field(
                name="Card Prices:",
                value=f'Cardmarket: {card_info["card_prices"]["cardmarket_price"]}€'
                f"\n"
                f'TCGPlayer: ${card_info["card_prices"]["tcgplayer_price"]}',
                inline=False,
            )
            footer_text = f'ID: {card_info["id"]} | Views: {card_info["misc_info"]["views"]} | Formats: {formats}'
            if "TCG" in formats:
                footer_text += (
                    f' | Release Date (TCG): {card_info["misc_info"]["tcg_date"]}'
                )
            elif "OCG" in formats:
                footer_text += (
                    f' | Release Date (OCG): {card_info["misc_info"]["ocg_date"]}'
                )
            super().set_footer(text=footer_text)
        else:
            super().__init__(title=title)
            for j in range(min(constants.max_results, cards_left)):
                index = constants.max_results * (page_num - 1) + j
                curr_card_info = response[index]
                super().add_field(
                    name=curr_card_info["name"],
                    value=f'{curr_card_info["type"]} | {curr_card_info["subtype"]}',
                    inline=False,
                )
            super().set_footer(text=f"Page {page_num}/{max_pages}")

    def __parse_card_text(self, card_text, card_type):
        print(card_text)
        headers = re.findall(r"\[ (.*?) \]", card_text)
        bodies = re.findall(r"\][\r|\n|\s]*([^\[]*)", card_text)
        bodies = list(map(methodcaller("strip", "\r\n"), bodies))
        print(headers)
        print(bodies)
        if len(bodies) > len(headers):
            joined_body = "\n".join(bodies[len(headers) - 1 :])
            bodies = [bodies[0], joined_body]

        # Pendulum cards separate pendulum and monster effects/flavor text in the same string with the header
        # between square brackets followed by their respective text
        if headers and bodies:
            for i in range(len(headers)):
                if headers[i] == "Flavor Text":
                    bodies[i] = f"*{bodies[i]}*"
                super().add_field(name=f"{headers[i]}:", value=bodies[i], inline=False)

        elif "Normal" in card_type:
            card_text = f"*{card_text}*".replace("''", "")
            super().add_field(name="Flavor Text:", value=card_text, inline=False)
        else:
            super().add_field(name="Effect:", value=card_text, inline=False)


class ErrorEmbedBuilder(EmbedBuilder):
    def __init__(self, error_message: str):
        title = "ERROR"
        file = disnake.File("artworks/artwork_23002292.jpg", "error.jpg")
        super().__init__(
            title=title, description=error_message, color=constants.alarm_red, file=file
        )
        super().set_thumbnail(url="attachment://error.jpg")
        super().set_footer(
            text='Type "/guide" to access help regarding the bot\'s commands.'
        )


class HelpEmbedBuilder(EmbedBuilder):
    def __init__(
        self,
        title: str = "",
        description: str = "",
        color: str = constants.greed_green,
        file: disnake.File = None,
        page_num: int = 0,
        page_count: int = 0,
    ):
        super().__init__(title=title, description=description, color=color, file=file)
        super().set_thumbnail(url="attachment://help_image.jpg")
        if page_num != 0:
            super().set_footer(text=f"Page {page_num}/{page_count}")
