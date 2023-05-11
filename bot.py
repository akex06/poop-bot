import discord

from discord.ext import commands
from utils.db import DB
from utils.config import Config


class Bot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix = "p!",
            intents = discord.Intents.all(),
            help_command = None
        )
        self.config: Config = Config()
        self.db: DB = DB(self)

    async def setup_hook(self) -> None:
        self.db.create_tables()

        await self.load_extension("cogs.general")

    async def on_ready(self):
        print(f"[   READY   ]: {self.user}")

    async def on_guild_join(self, guild: discord.Guild):
        print(f"[   GUILD+   ]: {guild.name}")

        self.db.get_prefix(guild)

    async def on_guild_leave(self, guild: discord.Guild):
        print(f"[   GUILD-   ]: {guild.name}")

    async def on_message(self, message: discord.Message):
        if f"<@{self.user.id}>" in message.content:
            prefix = self.db.get_prefix(message.guild)
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
