import asyncio
import os
import re
import time

import disnake
from Levenshtein import ratio
from disnake import Intents
from disnake.ext import commands
from disnake.ui import Button, View
from dotenv import load_dotenv

import Embeds
import constants
import queries
import utils
import ygoapi as ygo
from other_functions import setup
from Paginate import CreatePaginator

"""
Rebuild card database with API call
"""
setup(get_card_images=True)

"""
Initializing bot permissions and global variables, loading token and startup confirmation message.
"""
in_game = False
uptime = int(time.time())
intents = Intents.default()
intents.message_content = True
bot = commands.InteractionBot(intents=intents)

load_dotenv()
token = os.getenv("DISCORD_TOKEN")


@bot.event
async def on_ready():
    print("Ready to draw.")


@bot.slash_command(name="draw", description="Draw 2 cards, just like Pot of Greed.")
async def draw(ctx):
    title = "Pot of Greed activates!"
    embed = Embeds.DrawEmbedBuilder(title=title)
    button = Button(label="Draw again", style=disnake.ButtonStyle.green,
                    emoji=disnake.utils.get(ctx.guild.emojis, name="cards"))

    async def redraw(interaction):
        new_embed = Embeds.DrawEmbedBuilder(title=title)
        await interaction.response.edit_message(embed=new_embed, file=new_embed.get_file(), view=view)

    view = View()
    view.add_item(button)
    button.callback = redraw
    await ctx.send(embed=embed, file=embed.get_file(), view=view)


@bot.slash_command(
    name="info",
    description="Some info about me."
)
async def info(ctx):
    """
    Sends a simple embed with information about the bot, such as the name of his creator (me) and his uptime, as well
    as some tips for the user.
    Parameters:
    ----------
    :param ctx: The invocation context of the command.
    """
    global uptime
    title = "My name is Bot of Greed!"
    description = """I am a Discord bot created by [Pedro Silva](https://github.com/pedrosilva17), \
    that uses the [YGOPRODeck Database](https://db.ygoprodeck.com/) API to populate its database.
    
    **Author's note**: if you have any issues with the bot or would like to contribute to the project, \
    click my name above to go to my Github page, where you can find my socials and the repository for \
    this bot. Consider leaving a star on the repo if you enjoy it!
    """
    file = disnake.File("profile.png", filename="profile.png")

    embed = Embeds.InfoEmbedBuilder(title=title, description=description, file=file, time=uptime)
    await ctx.send(embed=embed, file=file)


@bot.slash_command(
    name="guess",
    description="Given a card's text or artwork, guess its name. You have 90 seconds per game to guess.",
)
async def guess(ctx,
                mode: str = commands.Param(name="mode", description="The game mode to play.",
                                           choices=["Card Text", "Artwork"])
                ):
    """
    Guessing game that tests the user's ability to identify a card based on its description or artwork, depending on the
    value of the "mode" parameter.
    Parameters:
    ----------
    :param ctx: The invocation context of the command.
    :param mode: The game mode to play:
    - "Card Text": Guess the card through its description.
    - "Artwork": Guess the card through its artwork.
    """
    """
    global in_game
    if in_game:
        await ctx.send("Hey, there's still a game in progress! Type 'quit' if you want to end it and then "
                       "start another.", ephemeral=True)
        return
    """
    await ctx.response.defer()
    loading_emoji = disnake.utils.get(ctx.guild.emojis, name="level_spin")
    await ctx.send(f"Preparing the game... {loading_emoji}")

    title = "Guess the card!"
    if mode == "Card Text":
        thumb = disnake.File("artworks/artwork_81210420.jpg", "thumbnail.jpg")
        embed = Embeds.GuessEmbedBuilder(
            title=title, color=constants.hat_purple, file=thumb, mode=mode)
    else:
        embed = Embeds.GuessEmbedBuilder(title=title, color=constants.hat_purple, mode=mode)
    card = embed.get_card()
    file = embed.get_file()

    try:
        button = Button(label="Hint", style=disnake.ButtonStyle.green,
                        emoji=constants.emojis["red_question_mark"])
        view = View()
        view.add_item(button)

        async def show_hint(inter):
            """
            Upon clicking the "Hint" button, show the first letter of each word that composes the card name, as
            well as the number of letters, on the footer of the embed displaying the game.
            Parameters:
            ----------
            :param inter: The interaction invoking this function (the click on the button).
            """
            hint = ""
            hint_list = card["name"].split()
            for word in hint_list:
                hint += word[0] + re.sub('[A-z]', '_ ', word[1:]) + ' '
            embed.set_footer(text=f"Hint: {hint} | Type: {card['type']}")
            await inter.response.edit_message(embed=embed, view=view)
            return

        async def game_loop():
            """
            Loop that controls the flow of the game. There are 5 lives shared by every member that decides to guess,
            and if they are all spent, the game ends. Guessing the card name or typing "quit" produces the same result.
            """
            global in_game
            in_game = True
            tries = 5
            while in_game:
                answer = await bot.wait_for('message')
                if not answer.author.bot and answer.channel == ctx.channel and answer.author.id == ctx.author.id:
                    if card["name"].lower() == answer.content.lower():
                        await answer.reply(f"{answer.author.mention} got it right! Well done.")
                        in_game = False
                        break
                    match answer.content.lower():
                        case "quit":
                            await answer.reply(f"{answer.author.mention} ended the game. The answer is {card['name']}.")
                            in_game = False
                        case _:
                            tries -= 1
                            match tries:
                                case 1:
                                    await ctx.send(f"{answer.author.mention}, wrong! Last chance...")
                                case 0:
                                    await ctx.send(f"Game over! The answer is {card['name']}.")
                                    in_game = False
                                case _:
                                    await ctx.send(f"{answer.author.mention}, wrong! {tries} tries left.")
                            await asyncio.sleep(0.3)

        button.callback = show_hint
        await ctx.edit_original_message(content="", embed=embed, view=view, file=file)
        await asyncio.sleep(0.3)
        await asyncio.wait_for(game_loop(), timeout=90)

    except asyncio.TimeoutError:
        await ctx.send(f"Time's up! The answer is {card['name']}.")
        in_game = False
    return


NAMES = queries.card_attribute_list("name")
BETA_NAMES = queries.card_attribute_list("beta_name")
TYPES = queries.card_attribute_list("type")
SUBTYPES = queries.card_attribute_list("subtype")
ARCHETYPES = queries.card_attribute_list("archetype")


async def autocomp_names(inter: disnake.ApplicationCommandInteraction, _input: str):
    _input = re.escape(_input)
    if _input.strip() == "":
        return []
    result = sorted([name for name in NAMES], key=lambda s: ratio(
        s, _input) + utils.count_whole_words(_input, s.split(" ")), reverse=True)
    return result[:25]


async def autocomp_beta_names(inter: disnake.ApplicationCommandInteraction, _input: str):
    _input = re.escape(_input)
    if _input.strip() == "":
        return []
    result = sorted([name for name in BETA_NAMES], key=lambda s: ratio(
        s, _input) + utils.count_whole_words(_input, s.split(" ")), reverse=True)
    return result[:25]


async def autocomp_types(inter: disnake.ApplicationCommandInteraction, _input: str):
    _input = re.escape(_input)
    if _input.strip() == "":
        return []
    result = [card_type for card_type in TYPES if _input.lower() in card_type.lower()]
    return result[:25]


async def autocomp_subtypes(inter: disnake.ApplicationCommandInteraction, _input: str):
    _input = re.escape(_input)
    if _input.strip() == "":
        return []
    result = [subtype for subtype in SUBTYPES if _input.lower() in subtype.lower()]
    return result[:25]


async def autocomp_archetypes(inter: disnake.ApplicationCommandInteraction, _input: str):
    _input = re.escape(_input)
    if _input.strip() == "":
        return []
    arch_list = set()
    for archetype in ARCHETYPES:
        arch_list.update(archetype.split(", "))
    result = sorted([archetype for archetype in arch_list], key=lambda s: ratio(
        s, _input) + utils.count_whole_words(_input, s.split(" ")), reverse=True)
    return result[:25]


@bot.slash_command(
    name="search",
    description="Search for cards using multiple filters.",
)
async def search(ctx,
                 name: str = commands.Param(default=None, name="name", description="Filter by name (one card).",
                                            autocomplete=autocomp_names),
                 beta_name: str = commands.Param(default=None, name="beta_name",
                                                 description="Filter by beta (old) name (one card).",
                                                 autocomplete=autocomp_beta_names),
                 name_multi: str = commands.Param(default=None, name="name_multi",
                                                  description="Filter by name (one or more cards)."),
                 archetype: str = commands.Param(default=None, name="archetype",
                                                 description="Filter by card archetype.",
                                                 autocomplete=autocomp_archetypes),
                 card_type: str = commands.Param(default=None, name="type", description="Filter by card type.",
                                                 autocomplete=autocomp_types),
                 subtype: str = commands.Param(default=None, name="subtype", description="Filter by card subtype.",
                                               autocomplete=autocomp_subtypes),
                 attribute: str = commands.Param(default=None, name="attribute",
                                                 description="Filter by card attribute.",
                                                 choices=queries.card_attribute_list("attribute")),
                 attack: str = commands.Param(default=None, name="attack", description="Filter by attack points."),
                 defense: str = commands.Param(default=None, name="defense", description="Filter by defense points."),
                 level: str = commands.Param(default=None, name="level", description="Filter by level."),
                 rank: str = commands.Param(default=None, name="rank", description="Filter by rank."),
                 scale: str = commands.Param(default=None, name="scale", description="Filter by Pendulum Scale value."),
                 link: str = commands.Param(default=None, name="link", description="Filter by link value."),
                 link_marker: str = commands.Param(default=None, name="link_markers",
                                                   description="Filter by link markers."),
                 sort: str = commands.Param(default="Name", name="sort_by",
                                            description="Sort the results in case more than one card is found. "
                                                        "Defaults to name.",
                                            choices=list(constants.short_terms.keys())[:-2]),
                 order: str = commands.Param(default="Ascending", name="order",
                                             description="Choose sorting order. Defaults to ascending order.",
                                             choices=["Ascending", "Descending"]),
                 ):
    """
    Searches the database for cards, using a variety of filters and sorting options, and displays the results
    in a user-friendly and appealing manner, using an embed.
    Parameters:
    ----------
    :param ctx: The invocation context of the command.
    :param name: Name to filter with.
    :param beta_name: Old/Beta name to filter with.
    :param name_multi: Name to filter with, that can show one or more cards (assuming there are no errors).
    :param archetype: Card archetype to filter with (not always accurate, some cards are missing their archetypes).
    :param card_type: Card type to filter with.
    :param subtype: Card "sybtype" to filter with.
    :param attribute: Card attribute to filter with.
    :param attack: Attack value to filter with.
    :param defense: Defense value to filter with.
    :param level: Level value to filter with.
    :param rank: Rank value to filter with.
    :param link: Link value to filter with.
    :param link_marker: Link marker(s) to filter with.
    :param scale: Pendulum scale value to filter with.
    :param sort: Parameter to sort by. Defaults to name.
    :param order: Order to sort by (ascending/descending). Defaults to ascending order.
    """
    await ctx.response.defer()
    parameters = {
        "name": name, "beta_name": beta_name, "name_multi": name_multi, "archetype": archetype,
        "type": card_type, "subtype": subtype, "attribute": attribute, "atk": attack,
        "def": defense, "level": level, "rank": rank, "scale": scale, "linkval": link,
        "linkmarkers": link_marker, "sort": sort, "order": order}
    response = queries.query(parameters)
    # embed, file = utils.embed_builder(ctx=ctx, embed_type="Search", response=response, subtype="Card")
    embed = utils.search_wrapper(ctx, response)
    if type(embed) != list:
        file = embed.get_file()
        await ctx.send(embed=embed, file=file)
    else:
        author = ctx.author.id
        view = CreatePaginator(ctx=ctx, embeds=embed, author=author, size=len(embed))
        await ctx.send(embed=embed[0], view=view)
    return


@bot.slash_command(
    name="guide",
    description="Get help regarding less straightforward commands.",
)
async def guide(ctx,
                command: str = commands.Param(name="command", description="The command to be checked.",
                                              choices=["Guess", "Search"])
                ):
    """
    Sends embed(s) with more detailed explanations of the chosen command in the "command" parameter.
    Parameters:
    ----------
    :param ctx: The invocation context of the command.
    :param command: The command to display more information about.
    """
    match command:
        case "Guess":
            title = "Minigame: Guess"
            help_text = open('help/guess_help.txt', 'r').read().rstrip('\n')
            file = disnake.File("artworks/artwork_81210420.jpg", filename="help_image.jpg")
            embed = Embeds.HelpEmbedBuilder(
                title=title, description=help_text, color=constants.hat_purple, file=file)
            await ctx.send(embed=embed, file=file)
            return
        case "Search":
            title = "Command: Search"
            file = disnake.File("artworks/artwork_74191528.jpg", filename="help_image.jpg")
            embeds = []
            page_count = 2
            for page_num in range(1, 3):
                help_text = open(f'help/search_help_{page_num}.txt', 'r').read().rstrip('\n')
                embed = Embeds.HelpEmbedBuilder(
                    title=title, description=help_text, color=constants.fate_blue, file=file,
                    page_num=page_num, page_count=page_count)
                embeds.append(embed)
            author = ctx.author.id
            view = CreatePaginator(ctx=ctx, embeds=embeds, author=author,
                                   size=len(embeds), has_dropdown=False)
            await ctx.send(embed=embeds[0], file=file, view=view)
            return


@bot.slash_command(name="test", description="This is a test.")
async def test_embed(ctx):
    global uptime
    file = disnake.File("profile.png", filename="profile.png")
    embed = Embeds.InfoEmbedBuilder(
        title="Test", description="This is a test.", time=uptime, file=file)
    await ctx.send(embed=embed, file=file)


bot.run(token)
