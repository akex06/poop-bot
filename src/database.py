import random

import discord
import mysql.connector
from discord.ext import commands

from collections import namedtuple

LeaderboardEntry = namedtuple("LeaderboardEntry", "member_id balance toilet poops")

class Database:
    def __init__(
            self,
            bot: commands.Bot,
            host: str,
            port: int,
            user: str,
            password: str,
            database: str
    ) -> None:
        self.conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        self.c = self.conn.cursor()
        self.bot = bot

        self.create_tables()

    def create_tables(self) -> None:
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS poops (
               member BIGINT,
               guild BIGINT,
               balance INT DEFAULT 0,
               toilet INT DEFAULT 1,
               poop1 INT DEFAULT 0,
               poop2 INT DEFAULT 0,
               poop3 INT DEFAULT 0,
               poop4 INT DEFAULT 0,
               poop5 INT DEFAULT 0,
               PRIMARY KEY (member, guild)
            )
            """)
        self.conn.commit()

        self.c.execute("""
            CREATE TABLE IF NOT EXISTS prefixes (
                guild BIGINT PRIMARY KEY,
                prefix VARCHAR(15)
            )
        """)
        self.conn.commit()

    def get_prefix(self, guild: discord.Guild) -> str:
        self.c.execute("SELECT prefix FROM prefixes WHERE guild = %s", (guild.id,))
        prefix = self.c.fetchone()

        if prefix is None:
            self.set_prefix(guild, "p!")
            return "p!"

        return prefix[0]

    def set_prefix(self, guild: discord.Guild, prefix: str) -> None:
        self.c.execute("UPDATE prefixes SET prefix = %s WHERE guild = %s", (prefix, guild.id))
        self.conn.commit()

    def user_exists(self, member: discord.Member) -> bool:
        self.c.execute(
            "SELECT 1 FROM poops WHERE member = %s AND guild = %s",
            (member.id, member.guild.id)
        )
        return bool(self.c.fetchone())

    def create_user_if_not_exists(self, member: discord.Member) -> None:
        if not self.user_exists(member):
            self.c.execute(
                "INSERT INTO poops (member, guild) VALUES (%s,%s)",
                (member.id, member.guild.id)
            )
            self.conn.commit()

    def get_balance(self, member: discord.Member) -> int:
        self.c.execute(
            "SELECT balance FROM poops WHERE member = %s AND guild = %s",
            (member.id, member.guild.id)
        )
        return self.c.fetchone()[0]

    def get_poops(self, member: discord.Member) -> tuple[int]:
        self.c.execute(
            "SELECT balance, toilet, poop1, poop2, poop3, poop4, poop5 FROM poops WHERE member = %s AND guild = %s",
            (member.id, member.guild.id)
        )
        # noinspection PyTypeChecker
        return self.c.fetchone()

    def get_toilet(self, member: discord.Member) -> int:
        self.c.execute("SELECT toilet FROM poops WHERE member = %s AND guild = %s", (member.id, member.guild.id))
        return self.c.fetchone()[0]

    def get_poop_value(self, poops: list[int]) -> int:
        return sum([
            poop_value * poop_amount for poop_value, poop_amount
            in zip(self.bot.config.poop_values.values(), poops)
        ])

    def add_poops(self, member: discord.Member) -> list[int]:
        toilet = self.get_toilet(member)

        rewards = [random.randrange(min_reward, max_reward + 1) for min_reward, max_reward in self.bot.config.get_toilet_ranges(toilet)]
        poop_value = self.get_poop_value(rewards)

        self.c.execute(
            """
            UPDATE poops
            SET
                poop1 = poop1 + %s,
                poop2 = poop2 + %s,
                poop3 = poop3 + %s,
                poop4 = poop4 + %s,
                poop5 = poop5 + %s,
                balance = balance + %s
            WHERE
                member = %s AND guild = %s
            """,
            (*rewards, poop_value, member.id, member.guild.id)
        )
        self.conn.commit()

        return rewards

    def rankup(self, member: discord.Member) -> None:
        poops_to_remove = self.bot.config.get_toilet_ranges()
        self.c.execute(
            """
            UPDATE poops
            SET
                poop1 = poop1 - %s,
                poop2 = poop2 - %s,
                poop3 = poop3 - %s,
                poop4 = poop4 - %s,
                poop5 = poop5 - %s,
                toilet = toilet + 1
            WHERE
                member = %s AND guild = %s
            """,
            (*poops_to_remove, member.id, member.guild.id)
        )
        self.conn.commit()

    def get_leaderboard(self, guild: discord.Guild, amount: int) -> list[LeaderboardEntry]:
        self.c.execute(
            """
                SELECT
                    member,
                    balance,
                    toilet,
                    poop1,
                    poop2,
                    poop3,
                    poop4,
                    poop5
                FROM poops
                WHERE guild = %s
                ORDER BY balance DESC
                LIMIT %s
            """,
            (guild.id, amount)
        )
        leaderboard = list()
        leaderboard_entries = self.c.fetchall()
        for entry in leaderboard_entries:
            leaderboard.append(LeaderboardEntry(*entry[:3], entry[3:]))

        return leaderboard
