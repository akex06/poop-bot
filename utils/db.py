import mysql.connector
import discord
from discord.ext import commands

from utils.config import Config


class DB:
    conn = mysql.connector.connect(
        host = "host",
        port = 3306,
        user = "user",
        password = "password",
        database = "database"
    )
    c = conn.cursor()
    config: Config

    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        DB.config = bot.config


    def create_tables(self):
        self.c.execute("CREATE TABLE IF NOT EXISTS prefixes (guild VARCHAR(20) PRIMARY KEY, prefix VARCHAR(10))")
        self.c.execute(
            "CREATE TABLE IF NOT EXISTS poops("
            "   member VARCHAR(20),"
            "   guild VARCHAR(20),"
            "   poop1 int,"
            "   poop2 int,"
            "   poop3 int,"
            "   poop4 int,"
            "   poop5 int,"
            "   toilet int,"
            "   PRIMARY KEY (member, guild)"
            ");")
        self.conn.commit()

    def check_poops(self, member: discord.Member):
        self.c.execute("SELECT member FROM poops WHERE member = %s AND guild = %s",
                       (member.id, member.guild.id))
        result = self.c.fetchone()
        if not result:
            self.c.execute("SHOW TABLES")
            self.c.execute(
                "INSERT INTO poops (member, guild, poop1, poop2, poop3, poop4, poop5, toilet) VALUES (%s, %s, 0, 0, 0, 0, 0, 1)",
                (member.id, member.guild.id)
            )
            self.conn.commit()

    def get_poops(self, member: discord.Member):
        self.check_poops(member)

        self.c.execute("SELECT poop1, poop2, poop3, poop4, poop5 FROM poops WHERE member = %s AND guild = %s",
                       (member.id, member.guild.id))
        result = self.c.fetchone()
        return {
            f"poop{i + 1}": amount
            for i, amount in enumerate(result)
        }

    def get_toilet(self, member: discord.Member):
        self.c.execute("SELECT toilet FROM poops WHERE member = %s AND guild = %s",
                       (member.id, member.guild.id))
        result = self.c.fetchone()
        return result[0]

    def add_poops(self, member: discord.Member) -> dict:
        winnings: dict = self.config.generate_winnings(self.get_toilet(member))
        self.c.execute(
            "UPDATE poops "
            "SET poop1 = poop1 + %s, "
            "poop2 = poop2 + %s, "
            "poop3 = poop3 + %s, "
            "poop4 = poop4 + %s, "
            "poop5 = poop5 + %s "
            "WHERE member = %s AND guild = %s",
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
        self.conn.commit()

        return winnings

    def get_all_poops(self, guild: discord.Guild):
        self.c.execute(
            "SELECT member, toilet, poop1, poop2, poop3, poop4, poop5 FROM poops WHERE guild = %s",
            (guild.id,)
        )
        result = self.c.fetchall()
        formatted_poops = []
        for member in result:
            wealth: int = 0

            for i, amount in enumerate(member[2:]):
                wealth += amount * self.config.get_poop_info(f"poop{i + 1}")["price"]

            formatted_poops.append((wealth, member[0], member[2:]))

        formatted_poops.sort(reverse = True)
        return formatted_poops[:25]

    def remove_poops(self, member: discord.Member, poops: dict):
        self.c.execute(
            "UPDATE poop "
            "SET poop1 = poop1 - %s, "
            "poop2 = poop2 - %s, "
            "poop3 = poop3 - %s, "
            "poop4 = poop4 - %s, "
            "poop5 = poop5 - %s, "
            "toilet = toilet + 1 "
            "WHERE member = %s AND guild = %s",
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
        self.conn.commit()
