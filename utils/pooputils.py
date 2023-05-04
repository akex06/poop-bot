import discord
import sqlite3
import json
import random

from discord.ext import commands

conn = sqlite3.connect("./files/poop.db")
c = conn.cursor()


def get_prefix(guild: discord.Guild):
    result = c.execute("SELECT prefix FROM prefixes WHERE guild = ?", (guild.id,)).fetchone()
    if not result:
        c.execute("INSERT INTO prefixes VALUES (?, ?)", (guild.id, "p!"))
        conn.commit()
        return "p!"

    return result[0]


def get_cooldown(message):
    check_poops(message.author)

    with open("./files/poop.json", "r") as f:
        data = json.load(f)

    toilet = c.execute("SELECT toilet FROM poop WHERE member = ? AND guild = ?",
                       (message.author.id, message.guild.id)).fetchone()[0]

    return commands.Cooldown(1, data["cooldowns"][f"toilet{toilet}"])


def create_tables():
    c.execute("CREATE TABLE IF NOT EXISTS prefixes (guild VARCHAR(20) PRIMARY KEY, prefix VARCHAR(10))")
    c.execute(
        "CREATE TABLE IF NOT EXISTS poop("
        "   member int,"
        "   guild int,"
        "   poop1 int,"
        "   poop2 int,"
        "   poop3 int,"
        "   poop4 int,"
        "   poop5 int,"
        "   toilet int,"
        "   PRIMARY KEY (member, guild)"
        ");")
    conn.commit()


def bot_get_prefix(bot: commands.Bot, message: discord.Message):
    return get_prefix(message.guild)


def check_poops(member):
    result = c.execute("SELECT member FROM poop WHERE member = ? AND guild = ?",
                       (member.id, member.guild.id)).fetchone()
    if not result:
        c.execute("INSERT INTO poop VALUES (?, ?, 0, 0, 0, 0, 0, 1)", (member.id, member.guild.id))
        conn.commit()


def get_poops(member):
    check_poops(member)

    result = c.execute("SELECT poop1, poop2, poop3, poop4, poop5 FROM poop WHERE member = ? AND guild = ?",
                       (member.id, member.guild.id)).fetchone()

    return {
        f"poop{i + 1}": amount
        for i, amount in enumerate(result)
    }


def get_toilet(member):
    result = c.execute("SELECT toilet FROM poop WHERE member = ? AND guild = ?",
                       (member.id, member.guild.id)).fetchone()
    return result[0]


def get_winnings(toilet: int) -> dict:
    return {
        poop: random.randint(*_range) for poop, _range in get_config()["winnings"][str(toilet)].items()
    }


def add_poops(member: discord.Member) -> dict:
    winnings: dict = get_winnings(get_toilet(member))
    print(winnings)
    c.execute(
        "UPDATE poop "
        "SET poop1 = poop1 + ?, "
        "poop2 = poop2 + ?, "
        "poop3 = poop3 + ?, "
        "poop4 = poop4 + ?, "
        "poop5 = poop5 + ? "
        "WHERE member = ? AND guild = ?",
        (
            winnings.get("poop1", 0),
            winnings.get("poop2", 0),
            winnings.get("poop3", 0),
            winnings.get("poop4", 0),
            winnings.get("poop5", 0),
            member.id,
            member.guild.id
        )
    )
    conn.commit()

    return winnings


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


def get_all_poops(guild: discord.Guild):
    result = c.execute(
        "SELECT member, toilet, poop1, poop2, poop3, poop4, poop5 FROM poop WHERE guild = ?",
        (guild.id,)
    ).fetchall()

    formatted_poops = []
    poop_values: dict = get_poop_values()
    for member in result:
        wealth: int = 0

        for i, poop in enumerate(member[2:]):
            wealth += poop * poop_values[f"poop{i + 1}"]["price"]

        formatted_poops.append((wealth, member[0], member[2:]))

    formatted_poops.sort(reverse = True)
    return formatted_poops[:25]


def set_prefix(guild: discord.Guild, prefix: str):
    c.execute("UPDATE prefixes SET prefix = ? WHERE guild = ?", (prefix, guild.id))
    conn.commit()
