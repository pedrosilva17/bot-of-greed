"""
Stores constants used around the code.
"""

max_results = 10

emojis = {
    "fast_reverse": "\U000023EA",
    "reverse": "\U00002B05",
    "wastebasket": "\U0001F5D1",
    "play": "\U000027A1",
    "fast_forward": "\U000023E9",
    "red_question_mark": "\U00002753",
    "arrow_right": "\U000027A1",
    "alarm_clock": "\U000023F0",
    "left": "\U00002B05",
    "top-left": "\U00002196",
    "top": "\U00002B06",
    "top-right": "\U00002197",
    "right": "\U000027A1",
    "bottom-left": "\U00002199",
    "bottom": "\U00002B07",
    "bottom-right": "\U00002198",
}

attributes = [
    "Archetype",
    "Attribute",
    "Type",
    "Subtype",
    "Level",
    "Rank",
    "Pendulum Scale",
    "Link Value",
    "Link Markers",
    "Attack",
    "Defense",
]

link_markers = [
    "Left",
    "Top-Left",
    "Top",
    "Top-Right",
    "Right",
    "Bottom-Left",
    "Bottom",
    "Bottom-Right",
]

link_marker_emojis = {k: emojis[k.lower()] for k in link_markers}

card_types = [
    "Skill Card",
    "Spell Card",
    "Trap Card",
    "Normal Monster",
    "Normal Tuner Monster",
    "Effect Monster",
    "Tuner Monster",
    "Flip Monster",
    "Flip Effect Monster",
    "Pendulum Effect Monster",
    "Pendulum Normal Monster",
    "Pendulum Tuner Effect Monster",
    "Ritual Monster",
    "Ritual Effect Monster",
    "Fusion Monster",
    "Synchro Monster",
    "Synchro Tuner Monster",
    "Synchro Pendulum Effect Monster",
    "XYZ Monster",
    "XYZ Pendulum Effect Monster",
    "Link Monster",
    "Pendulum Flip Effect Monster",
    "Pendulum Effect Fusion Monster",
    "Token",
]

regex_comparable_patterns = {
    r"\b^gte[0-9]+$": ">=",
    r"\b^gt[0-9]+$": ">",
    r"\b^lte[0-9]+$": "<=",
    r"\b^lt[0-9]+$": "<",
    r"\b^[0-9]+$": "=",
}

short_terms = {
    "ID": "id",
    "Name": "name",
    "Archetype": "archetype",
    "Type": "type",
    "Subtype": "subtype",
    "Attribute": "attribute",
    "Attack": "atk",
    "Defense": "def",
    "Level": "level",
    "Rank": "rank",
    "Link Value": "linkval",
    "Link Markers": "linkmarkers",
    "Pendulum Scale": "scale",
    "Sort": "sort",
    "Order": "order",
}
long_terms = {v: k for k, v in short_terms.items()}

greed_green = 0x0B7520
hat_purple = 0x6A0DAD
fate_blue = 0x1E4CFA
alarm_red = 0xFF0000
normal_yellow = 0xC18F48
effect_orange = 0xB55120
ritual_blue = 0x4A72B7
fusion_purple = 0x89459A
synchro_white = 0xEFEEEC
xyz_black = 0x262827
link_blue = 0x17649A
spell_green = 0x078874
trap_pink = 0xA21C75
skill_blue = 0x008ACB
