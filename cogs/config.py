from discord.ext import commands
from bot import PoopBot


class Config(commands.Cog):
    def __init__(self, bot: PoopBot) -> None:
        self.bot = bot
        self.emoji = "🔧"

    @commands.hybrid_command(
        name="setprefix",
        aliases=["set_prefix", "prefix"],
        with_app_command=True
    )
    @commands.has_permissions(administrator=True)
    async def set_prefix(self, ctx: commands.Context, prefix: str = None) -> None:
        current_prefix = self.bot.db.get_prefix(ctx.guild)
        if prefix is None:
            await ctx.send(f"Current prefix is `{current_prefix}`")
            return

        self.bot.db.set_prefix(ctx.guild, prefix)
        await ctx.send(f"Changed prefix from `{current_prefix}` to `{prefix}`")


async def setup(bot: PoopBot) -> None:
    await bot.add_cog(Config(bot))
