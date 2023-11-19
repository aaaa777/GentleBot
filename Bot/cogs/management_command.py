from discord.ext import commands
from discord import app_commands
import discord

class ManagementCommand(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener('on_ready')
    async def on_ready(self):
        print('management on_ready')
        await self.setup()

    @commands.Cog.listener('on_guild_join')
    async def on_guild_join(self, guild):
        print('management on_guild_join')
        await self.setup()

    
    # @commands.command(name='register', description="setup server")
    @commands.hybrid_command(name='register', description="setup server")
    async def register(self, ctx):
        """setup server"""
        # await self.setup()
        await ctx.send("setting up commands for this server")
        await self.sync_guild_command(ctx.guild)
        await ctx.channel.send("done")

    async def setup(self):
        await self.bot.tree.sync()

    async def sync_guild_command(self, guild: discord.Guild) -> None:
        print('sync_guild_command')
        await self.bot.tree.sync(guild=guild)