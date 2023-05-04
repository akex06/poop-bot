import discord
from discord.ext import commands

from utils import pooputils


class Bot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix = pooputils.bot_get_prefix,
            intents = discord.Intents.all(),
            help_command = None
        )

    async def setup_hook(self) -> None:
        pooputils.create_tables()

        await self.load_extension("cogs.general")

    async def on_ready(self):
        print(f"[   READY   ]: {self.user}")

    async def on_guild_join(self, guild: discord.Guild):
        print(f"[   GUILD+   ]: {guild.name}")

        pooputils.get_prefix(guild)

    async def on_guild_leave(self, guild: discord.Guild):
        print(f"[   GUILD-   ]: {guild.name}")

    async def on_message(self, message: discord.Message):
        if f"<@{self.user.id}>" in message.content:
            prefix = pooputils.get_prefix(message.guild)
            await message.reply(f"My prefix: `{prefix}`")

        await self.process_commands(message)

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Use p!help for a list of all commands")

        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                description = f"Wait {round(error.retry_after)} seconds before using this command",
                color = discord.Color.red()
            )
            embed.set_author(icon_url = self.user.avatar.url, name = "Satisfying Poop")

            await ctx.send(embed = embed)


bot = Bot()
bot.run("")
