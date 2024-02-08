import os

import discord
from discord.ext import commands
from discord.ext.commands import errors

from src.database import Database
from src.env import (
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    DB_DATABASE,
    TOKEN
)
from src.poop_config import PoopConfig


class PoopBot(commands.Bot):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.db = Database(
            self,
            DB_HOST,
            DB_PORT,
            DB_USER,
            DB_PASSWORD,
            DB_DATABASE
        )
        self.config = PoopConfig(self, "config.json")

    async def on_ready(self) -> None:
        print(f"Bot ready: {self.user}")

    async def setup_hook(self) -> None:
        for cog in os.listdir("cogs"):
            if not cog.endswith(".py"):
                continue

            await self.load_extension(f"cogs.{cog[:-3]}")

    async def on_command_error(self, ctx: commands.Context, exception: errors.CommandError, /) -> None:
        if isinstance(exception, errors.CommandOnCooldown):
            await ctx.send(f"Please wait `{exception.retry_after:.2f}` seconds before pooping again")
        else:
            raise exception


def get_prefix(bot: PoopBot, message: discord.Message) -> str:
    return bot.db.get_prefix(message.guild)


if __name__ == "__main__":
    poop_bot = PoopBot(command_prefix=get_prefix, intents=discord.Intents.all())
    poop_bot.run(TOKEN)
