import os
import time
import discord
import asyncio
from discord.ext import commands

from Bot.bot import GentleBot
from Bot.command import Command


# Load .env file
from dotenv import load_dotenv

load_dotenv()

# load token from env
TOKEN = os.getenv("TOKEN")


def main():
    # intent = discord.Intents.default()
    # intent.message_content = True
    # bot = commands.Bot(command_prefix='$', intents=intent)
    # bot.add_cog(Command(bot))

    bot = GentleBot()

    bot.run(TOKEN)


main()