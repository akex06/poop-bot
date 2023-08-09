import datetime

import discord
from PIL import Image, ImageFont, ImageDraw
from discord.ext import commands

from utils.config import Config
from utils.db import DB


def get_cooldown(ctx: commands.Context):
    return ctx.bot.config.get_cooldown(ctx.author)


class General(commands.Cog):
    def __init__(self, bot: commands.bot) -> None:
        self.bot: commands.Bot = bot
        self.config: Config = self.bot.config
        self.db: DB = self.bot.db

    @commands.command(aliases = ["bal", "balance"], description = "Show how many poops you have!")
    async def poopbal(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author

        poops = list(self.bot.db.get_poops(member).values())
        toilet_level = self.bot.db.get_toilet(member)

        background: Image = Image.open("./files/images/background.png")
        toilet = Image.open(f"./files/images/toilet{toilet_level}.png").resize((90, 90))
        background.paste(toilet, (485, 360), toilet)

        font = ImageFont.truetype("./files/font.otf", size = 50)
        draw = ImageDraw.Draw(background)

        draw.text((150, 124), str(poops[0]), font = font, fill = (255, 255, 255))
        draw.text((150, 250), str(poops[1]), font = font, fill = (255, 255, 255))
        draw.text((150, 376), str(poops[2]), font = font, fill = (255, 255, 255))
        draw.text((590, 124), str(poops[3]), font = font, fill = (255, 255, 255))
        draw.text((590, 250), str(poops[4]), font = font, fill = (255, 255, 255))
        draw.text((590, 376), f"Level {toilet_level}", font = font, fill = (255, 255, 255))

        background.save("./files/images/temporary.png")

        await ctx.send(file = discord.File("./files/images/temporary.png"))

    @commands.command(description = "Gain some poops!")
    @commands.dynamic_cooldown(get_cooldown, commands.BucketType.member)
    async def poop(self, ctx: commands.Context):

        obtained_poops: dict = self.bot.db.add_poops(ctx.author)
        poops: str = "\n".join([
            f"{self.config.get_emoji(poop)} {self.config.get_poop_info(poop)['name']}: {amount}"
            for poop, amount in obtained_poops.items()
        ])
        embed = discord.Embed(description = f"Poops Obtained:\n{poops}", color = discord.Color.green())
        embed.set_author(icon_url = self.bot.user.avatar.url, name = "Satisfying Poop")

        await ctx.send(embed = embed)

    @commands.command(aliases = ["rankup"], description = "Level up your toilet!")
    async def levelup(self, ctx: commands.Context):
        embed = discord.Embed(title = "Level Up", description = f"Use p!help for a list of all the commands",
                              color = discord.Colour.green())
        toilet = self.db.get_toilet(ctx.author)
        if toilet == 5:
            embed.add_field(name = "Level up :white_check_mark:",
                            value = f"You already have the max toilet level {self.config.get_emoji('toilet5')}")
            await ctx.send(embed = embed)
            return
        poops: dict = self.db.get_poops(ctx.author)
        needed_poops: dict = self.config.get_levelup(str(toilet))
        missing_poops: dict = {
            poop: max(amount - poops[poop], 0)
            for poop, amount in needed_poops.items()
        }
        if all(missing_poops.values()):
            embed.add_field(
                name = "**Missing poops**",
                value = "\n".join([
                    f"{self.config.get_emoji(poop)} **{poops[poop]}/{amount}**"
                    for poop, amount in needed_poops.items()
                ])
            )

            await ctx.send(embed = embed)
            return

        self.bot.db.c.execute(
            "UPDATE poop "
            "SET poop1 = poop1 - ?, "
            "poop2 = poop2 - ?, "
            "poop3 = poop3 - ?, "
            "poop4 = poop4 - ?, "
            "poop5 = poop5 - ?, "
            "toilet = toilet + 1 "
            "WHERE member = ? AND guild = ?",
            (
                needed_poops.get("poop1", 0),
                needed_poops.get("poop2", 0),
                needed_poops.get("poop3", 0),
                needed_poops.get("poop4", 0),
                needed_poops.get("poop5", 0),
                ctx.author.id,
                ctx.guild.id
            )
        )
        self.bot.db.conn.commit()

        await ctx.send("leveled up")

    @commands.command(aliases = ["leaderboard", "top"], description = "Shows a leaderboard with the most poops")
    async def lb(self, ctx: commands.Context):
        msg = await ctx.send("Loading leaderboard...")
        poops: list = self.bot.db.get_all_poops(ctx.guild)
        embed = discord.Embed(
            description = "Top 25 users with the most poop value",
            color = 0xed9b1f
        )

        embed.set_author(icon_url = self.bot.user.avatar.url, name = "PoopBot Leaderboard")

        for poop in poops:
            user: discord.User = await self.bot.fetch_user(poop[1])
            player_poops: str = "\n".join(
                [f"{self.config.get_emoji(f'poop{i + 1}')} `{amount}`"
                 for i, amount in enumerate(poop[2]) if amount]
            )

            embed.add_field(
                name = f"{user.name}#{user.discriminator}",
                value = f"Poop value: `{poop[0]}`\n{player_poops}"
            )

        await msg.edit(content = None, embed = embed)

    @commands.command(description = "Shows this message")
    async def help(self, ctx: commands.Context):
        embed = discord.Embed(title = "Poop Bot Help!", color = 0xed9b1f)
        for command in self.bot.commands:
            embed.add_field(name = f"p!{command.name}", value = command.description, inline = False)

        await ctx.send(embed = embed)


async def setup(bot: commands.bot):
    await bot.add_cog(
        General(bot)
    )
