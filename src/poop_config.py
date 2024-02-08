import json

import discord
from discord.ext import commands


class PoopConfig:
    def __init__(self, bot: commands.Bot, config_fp: str) -> None:
        self.bot = bot
        self.config_fp = config_fp
        self.config = self.get_config()

    def get_config(self) -> dict:
        with open(self.config_fp, encoding="utf-8") as f:
            return json.load(f)

    def reload(self):
        self.config = self.get_config()

    @property
    def poop_values(self) -> dict[str, int]:
        return self.config["values"]

    def get_toilet_ranges(self, toilet: int) -> list[int]:
        return self.config["rewards"][str(toilet)]

    def get_cooldown(self, member: discord.Member) -> commands.Cooldown:
        self.bot.db.create_user_if_not_exists(member)
        toilet = self.bot.db.get_toilet(member)

        return commands.Cooldown(1, self.config["cooldowns"][str(toilet)])

    def get_upgrade(self, toilet: int) -> list[int]:
        return self.config["upgrades"][str(toilet)]

    def get_emoji(self, emoji: str) -> str:
        return self.config["emojis"][emoji]