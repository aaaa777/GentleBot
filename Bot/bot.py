import discord
import asyncio
from discord import app_commands
from discord.ext import commands

from .cogs.player_command import Command
from .cogs.player_channel_observer import ChannelObserver

class GentleBot():

    def __init__(self):
        intent = discord.Intents.default()
        intent.message_content = True
        self.bot = commands.Bot(command_prefix="$", intents=intent)
        self.command_cog = Command(self.bot)
        self.observer_cog = ChannelObserver(self.bot)

    def run(self, token):
        asyncio.run(self.bot.add_cog(self.command_cog))
        asyncio.run(self.bot.add_cog(self.observer_cog))
        self.bot.run(token)

