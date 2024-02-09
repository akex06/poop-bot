import discord
from discord.ext import commands

from bot import PoopBot
from src.constants import (
    DEFAULT_GUILD_ICON,
    EMBED_COLOR
)


def get_cooldown(ctx: commands.Context):
    return ctx.bot.config.get_cooldown(ctx.author)


class Poop(commands.Cog):
    def __init__(self, bot: PoopBot) -> None:
        self.bot = bot
        self.emoji = "💩"

    @commands.dynamic_cooldown(get_cooldown, commands.BucketType.member)
    @commands.hybrid_command(
        "poop",
        description="You poop, what description did you expect",
        with_app_command=True
    )
    async def poop(self, ctx: commands.Context) -> None:
        self.bot.db.create_user_if_not_exists(ctx.author)
        added_poops = self.bot.db.add_poops(ctx.author)

        description = self.get_poop_description(added_poops)

        embed = discord.Embed(description="\n".join(description), color=EMBED_COLOR)
        embed.set_author(name="You pooped")

        await ctx.send(embed=embed)

    @commands.hybrid_command(
        "balance",
        description="Checks yours or others poop balance",
        aliases=["bal", "poops"],
        with_app_command=True
    )
    async def balance(self, ctx: commands.Context, member: discord.Member = None) -> None:
        if member is None:
            member = ctx.author

        self.bot.db.create_user_if_not_exists(member)

        balance, toilet, *poops = self.bot.db.get_poops(member)
        description = self.get_poop_description(poops)

        toilet = self.bot.db.get_toilet(member)
        toilet_emoji = self.bot.config.get_emoji(f"toilet{toilet}")
        description.append(f"{toilet_emoji}: `{toilet}`")

        embed = discord.Embed(description="\n".join(description), color=EMBED_COLOR)

        member_icon = DEFAULT_GUILD_ICON if member.avatar is None else member.avatar.url
        embed.set_author(name=f"{member.name}'s balance", icon_url=member_icon)

        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="upgrade",
        description="Upgrade your toilet to poop faster",
        aliases=["rankup"],
        with_app_command=True
    )
    async def upgrade(self, ctx: commands.Context) -> None:
        toilet = self.bot.db.get_toilet(ctx.author)
        required_poops = self.bot.config.get_upgrade(toilet)
        poops = self.bot.db.get_poops(ctx.author)

        can_rankup = True
        for poop_amount, required_poop_amount in zip(poops, required_poops):
            if poop_amount < required_poop_amount:
                can_rankup = False
                break

        if not can_rankup:
            await ctx.send(f"You can't upgrade, needed poops: {required_poops}")
            return

        self.bot.db.rankup(ctx.author)
        await ctx.send()

    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.hybrid_command(
        name="leaderboard",
        description="Checks the top 10 players of the server",
        aliases=["lb", "top"],
        with_app_command=True
    )
    async def leaderboard(self, ctx: commands.Context) -> None:
        embed = discord.Embed(description="Top 10 users with more poop value", color=EMBED_COLOR)
        leaderboard_entries = self.bot.db.get_leaderboard(ctx.guild, 10)

        for entry in leaderboard_entries:
            member = ctx.guild.get_member(entry.member_id)
            description = [f"Poop value `{entry.balance}`"]

            for poop, amount in enumerate(entry.poops, start=1):
                emoji = self.bot.config.get_emoji(f"poop{poop}")
                description.append(f"{emoji} `{amount}`")

            embed.add_field(
                name=f"{member}",
                value="\n".join(description)
            )

        await ctx.send(embed=embed)

    def get_poop_description(self, poops: list[int]) -> list:
        description = list()
        for poop, amount in enumerate(poops, 1):
            emoji = self.bot.config.get_emoji(f"poop{poop}")
            description.append(f"{emoji}: `{amount}`")

        return description


async def setup(bot: PoopBot) -> None:
    await bot.add_cog(Poop(bot))
