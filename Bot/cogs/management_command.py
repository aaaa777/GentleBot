from discord.ext import commands
from discord import app_commands

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


    @commands.command(name='register', description="setup server")
    async def register(self, ctx):
        """setup server"""
        await self.setup()
        await ctx.send("setup server completed")

    async def setup(self):
        await self.bot.tree.sync()