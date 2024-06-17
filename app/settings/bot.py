from dataclasses import dataclass


@dataclass
class Bot:
    """Bot config"""

    token: str
    parse_mode: str


def get_parse_mode(bot_section) -> str:
    """
    Get & return parse mode. Provides to bot instance.
    :param bot_section: configparser section
    """

    try:
        if bot_section["parse_mode"] in ("HTML", "MarkdownV2"):
            return bot_section["parse_mode"]
        return "HTML"
    # Param parse_mode isn't set in app.ini. HTML will be set.
    except KeyError:
        return "HTML"
