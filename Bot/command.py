import discord
from discord import app_commands
from discord.ext import commands

class Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(name='hello', description="Says hello", aliases=['hi', 'hey'])
    async def hello(self, ctx):
        """Says hello"""
        await ctx.send("hello")

    @commands.command(name='join', description="join voice channel", aliases=['j'])
    async def join(self, ctx):
        """join voice channel"""
        await ctx.send("join")

    @commands.command(name='leave', description="leave voice channel", aliases=['l'])
    async def leave(self, ctx):
        """leave voice channel"""
        await ctx.send("leave")

    @commands.command(name='play', description="play music", aliases=['p'])
    async def play(self, ctx):
        """play music"""
        await ctx.send("play")

    @commands.command(name='pause', description="pause music")
    async def pause(self, ctx):
        """pause music"""
        await ctx.send("pause") 

    @commands.command(name='unpause', description="resume music")
    async def unpause(self, ctx):
        """resume music"""
        await ctx.send("unpause")

    @commands.command(name='skip', description="skip music")
    async def skip(self, ctx):
        """skip music"""
        await ctx.send("skip")

    @commands.command(name='repeat', description="repeat music")
    async def repeat(self, ctx):
        """repeat music"""
        await ctx.send("repeat")    

    @commands.command(name='shuffle', description="shuffle music")
    async def shuffle(self, ctx):
        """shuffle music"""
        await ctx.send("shuffle")

    @commands.command(name='volume', description="volume music")
    async def volume(self, ctx):
        """volume music"""
        await ctx.send("volume")

    @commands.command(name='save', description="save playlist")
    async def save(self, ctx):
        """save playlist"""
        await ctx.send("save")

    @commands.command(name='load', description="load playlist")
    async def load(self, ctx):
        """load playlist"""
        await ctx.send("load")

    @commands.command(name='now', description="now playing", aliases=['np'])
    async def now(self, ctx):
        """now playing"""
        await ctx.send("now")

    @commands.command(name='playlist', description="show playlist", aliases=['pl'])
    async def playlist(self, ctx):
        """show playlist"""
        await ctx.send("playlist")

