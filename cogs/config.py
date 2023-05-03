import discord

from discord.ext import commands
from utils import pooputils


class Config(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def setprefix(self, ctx: commands.Context, prefix: str = None):
        if not prefix:
            await ctx.send("You need to specify a prefix")
            return

        pooputils.set_prefix(ctx.guild, prefix)
        await ctx.send(f"The prefix was changed to `{prefix}`")


async def setup(bot: commands.Bot):
    await bot.add_cog(
        Config(bot)
    )
