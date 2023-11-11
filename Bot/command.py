import discord
from discord import app_commands
from discord.ext import commands

class Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(name='hello', description="Says hello")
    async def hello(self, ctx):
        """Says hello"""
        await ctx.send("hello")