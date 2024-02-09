from typing import Any, Mapping, Optional, List

import discord
from discord.ext import commands
from discord.ext.commands import Cog, Command

from src.constants import EMBED_COLOR


def get_cog_help_embed(cog: commands.Cog, prefix: str):
    description = list()
    for command in cog.get_commands():
        parameters = " ".join(
            f"<{name}>" if parameter.required else f"[{name}]"
            for name, parameter in command.params.items()
        )
        description.append(
            f"`{prefix}{command.name} {parameters}` - {command.description}"
        )

    embed = discord.Embed(description="\n".join(description), color=EMBED_COLOR)
    embed.set_author(name=f"{cog.qualified_name} cog")

    return embed


class HelpSelector(discord.ui.Select):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        options = [
            discord.SelectOption(label=name, description=cog.description, emoji=cog.emoji)
            for name, cog in bot.cogs.items()
        ]

        super().__init__(placeholder="Select a cog to get help", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction) -> Any:
        cog_name = self.values[0]
        cog = self.bot.get_cog(cog_name)

        for option in self.options:
            if option.value == cog_name:
                option.default = True
            else:
                option.default = False

        embed = get_cog_help_embed(cog, "p!")
        await interaction.message.edit(embed=embed, view=self.view)
        await interaction.response.defer()


class HelpView(discord.ui.View):
    def __init__(self, ctx: commands.Context, *, timeout=180) -> None:
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.message: discord.Message | None = None

        self.add_item(HelpSelector(self.ctx.bot))

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        if self.ctx.author != interaction.user:
            await interaction.response.send_message(
                "You can't use that, you need to generate a new help menu with p!help",
                ephemeral=True
            )
            return False

        return True

    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True

        await self.message.edit(view=self)


class HelpCommand(commands.HelpCommand):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.message = None

    async def send_bot_help(
            self,
            mapping: Mapping[Optional[Cog], List[Command[Any, ..., Any]]],
            /
    ) -> None:
        view = HelpView(self.context)
        await self.context.send(view=view)

    async def send_cog_help(self, cog: Cog, /) -> None:
        embed = get_cog_help_embed(cog, "p!")
        await self.get_destination().send(embed=embed)
