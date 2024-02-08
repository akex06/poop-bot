from typing import Mapping, Optional, List, Any

import discord
from discord.ext import commands
from discord import ui
from src.constants import (
    EMBED_COLOR
)


class CogSelector(ui.Select):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        options = [
            discord.SelectOption(
                label=name,
                emoji=cog.emoji
            ) for name, cog
            in self.bot.cogs.items()
        ]

        super().__init__(placeholder="Select a cog", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction) -> Any:
        cog = self.bot.get_cog(self.values[0])
        prefix = self.bot.db.get_prefix(interaction.user)

        for option in self.options:
            if option.value == self.values[0]:
                option.default = True
            else:
                option.default = False

        description = list()
        description.append("<> Required parameters [] Optional parameters")
        for command in cog.get_commands():
            parameters = " ".join([
                f"<{parameter.name}>" if parameter.required else f"[{parameter.name}]" for parameter
                in command.params.values()
            ])
            description.append(f"{prefix}{command} {parameters}")

        embed = interaction.message.embeds[0]
        embed.description = "\n".join(description)

        await interaction.message.edit(embed=embed, view=self.view)
        await interaction.response.defer()


class CogSelectorView(ui.View):
    def __init__(self, ctx: commands.Context, *, timeout=10) -> None:
        super().__init__(timeout=timeout)
        self.message: discord.Message | None = None
        self.ctx = ctx
        self.add_item(CogSelector(self.ctx.bot))

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

    async def send_bot_help(
            self,
            mapping: Mapping[Optional[commands.Cog], List[commands.Command[Any, ..., Any]]]
    ) -> None:
        prefix = self.context.bot.db.get_prefix(self.context.guild)
        embed = discord.Embed(
            description=
            f"My prefix is `{prefix}`"
            f"Select the cog below for detailed help",
            color=EMBED_COLOR
        )
        cog_selector = CogSelectorView(self.context)
        cog_selector.message = await self.context.send(embed=embed, view=cog_selector)
