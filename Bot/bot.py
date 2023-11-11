import discord
import asyncio

from discord import app_commands
from discord.ext import commands
from .command import Command

class GentleBot():

    def __init__(self):
        intent = discord.Intents.default()
        intent.message_content = True
        self.bot = commands.Bot(command_prefix="$", intents=intent)
        self.cog = Command(self.bot)

    async def on_ready(self):
        await self.add_cog(self.cog)
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))

    def run(self, token):

        asyncio.run(self.bot.add_cog(self.cog))
        self.bot.run(token)

