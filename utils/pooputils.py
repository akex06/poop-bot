import json
import random


def get_winnings(toilet: int) -> dict:
    return {
        poop: random.randint(*_range) for poop, _range in get_config()["winnings"][str(toilet)].items()
    }


def get_config() -> dict:
    with open("files/poop.json", encoding = "utf-8") as f:
        return json.load(f)


def get_poop_values() -> dict:
    return get_config()["poops"]


def get_emojis() -> dict:
    return get_config()["emoji"]


def get_emoji(name: str) -> str:
    return get_emojis()[name]


def get_levelup() -> dict:
    return get_config()["levelup"]


def get_poop_names() -> dict:
    return get_config()["poops"]
