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
    return result


def get_toilet(member):
    result = c.execute("SELECT toilet FROM poop WHERE member = ? AND guild = ?",
                       (member.id, member.guild.id)).fetchone()
    return result[0]


def add_poops(member, toilet):
    with open("./files/poop.json", "r") as f:
        data = json.load(f)

    string = "UPDATE poop SET " + ", ".join([f"{x} = {x} + ?" for x in data["winnings"][str(toilet)]])
    val = tuple([random.randint(x[0], x[1]) for x in data["winnings"][str(toilet)].values()], )

    c.execute(string, val)
    conn.commit()

    return val


def get_config() -> dict:
    with open("files/poop.json", encoding = "utf-8") as f:
        return json.load(f)


def get_poop_values() -> dict:
    return get_config()["poops"]


def get_emojis() -> dict:
    return get_config()["emoji"]


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

    formatted_poops.sort()
    print(formatted_poops)
    return formatted_poops[:25]
