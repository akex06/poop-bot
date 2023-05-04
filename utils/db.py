import sqlite3

import discord
from discord.ext import commands

from utils import pooputils

conn = sqlite3.connect("./files/poop.db")
c = conn.cursor()


class DB:
    @staticmethod
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

    @staticmethod
    def get_prefix(guild: discord.Guild):
        result = c.execute("SELECT prefix FROM prefixes WHERE guild = ?", (guild.id,)).fetchone()
        if not result:
            c.execute("INSERT INTO prefixes VALUES (?, ?)", (guild.id, "p!"))
            conn.commit()
            return "p!"

        return result[0]

    @staticmethod
    def bot_get_prefix(bot: commands.Bot, message: discord.Message):
        return DB.get_prefix(message.guild)

    @staticmethod
    def check_poops(member: discord.Member):
        result = c.execute("SELECT member FROM poop WHERE member = ? AND guild = ?",
                           (member.id, member.guild.id)).fetchone()
        if not result:
            c.execute("INSERT INTO poop VALUES (?, ?, 0, 0, 0, 0, 0, 1)", (member.id, member.guild.id))
            conn.commit()

    @staticmethod
    def get_poops(member: discord.Member):
        DB.check_poops(member)

        result = c.execute("SELECT poop1, poop2, poop3, poop4, poop5 FROM poop WHERE member = ? AND guild = ?",
                           (member.id, member.guild.id)).fetchone()

        return {
            f"poop{i + 1}": amount
            for i, amount in enumerate(result)
        }

    @staticmethod
    def get_toilet(member: discord.Member):
        result = c.execute("SELECT toilet FROM poop WHERE member = ? AND guild = ?",
                           (member.id, member.guild.id)).fetchone()
        return result[0]

    @staticmethod
    def add_poops(member: discord.Member) -> dict:
        winnings: dict = pooputils.get_winnings(DB.get_toilet(member))
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

    @staticmethod
    def get_all_poops(guild: discord.Guild):
        result = c.execute(
            "SELECT member, toilet, poop1, poop2, poop3, poop4, poop5 FROM poop WHERE guild = ?",
            (guild.id,)
        ).fetchall()

        formatted_poops = []
        poop_values: dict = pooputils.get_poop_values()
        for member in result:
            wealth: int = 0

            for i, poop in enumerate(member[2:]):
                wealth += poop * poop_values[f"poop{i + 1}"]["price"]

            formatted_poops.append((wealth, member[0], member[2:]))

        formatted_poops.sort(reverse = True)
        return formatted_poops[:25]

    @staticmethod
    def remove_poops(member: discord.Member, poops: dict):
        c.execute(
            "UPDATE poop "
            "SET poop1 = poop1 - ?, "
            "poop2 = poop2 - ?, "
            "poop3 = poop3 - ?, "
            "poop4 = poop4 - ?, "
            "poop5 = poop5 - ?, "
            "toilet = toilet + 1 "
            "WHERE member = ? AND guild = ?",
            (
                poops.get("poop1", 0),
                poops.get("poop2", 0),
                poops.get("poop3", 0),
                poops.get("poop4", 0),
                poops.get("poop5", 0),
                member.id,
                member.guild.id
            )
        )
        conn.commit()