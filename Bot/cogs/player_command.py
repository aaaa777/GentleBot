import asyncio
import discord
from discord import app_commands
from discord.ext import commands

from ..music.player import Player

class Command(commands.Cog):


    def __init__(self, bot):
        self.bot = bot
        self.players = {}


    @commands.command(name='hello', description="Says hello", aliases=['hi', 'hey'])
    async def hello(self, ctx):
        """Says hello"""
        await ctx.send("hello")


    @commands.command(name='join', description="join voice channel", aliases=['j'])
    async def join(self, ctx):
        """join voice channel"""

        # コマンドを実行したメンバーがボイスチャンネルに接続しているか確認する
        message = ctx.message
        if message.author.voice is None:
            await message.channel.send("あなたはボイスチャンネルに接続していません。")
            return
        
        # ボイスチャンネルに接続する
        await message.author.voice.channel.connect()
        player = self.get_player(ctx.guild.id)
        player.add_user(message.author.id)

        await message.channel.send("接続しました。")


    @commands.command(name='leave', description="leave voice channel", aliases=['l'])
    async def leave(self, ctx):
        """leave voice channel"""
        
        message = ctx.message
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。")
            return

        # 切断する
        await message.guild.voice_client.disconnect()

        await message.channel.send("切断しました。")


    @commands.command(name='play', description="play music", aliases=['p'])
    async def play(self, ctx):
        """play music"""
        player = self.get_player(ctx.guild.id)

        player.fill_playlist_10()
        print(player.playlist.all_songs)

        player.start()
        await ctx.send("play")

    @commands.command(name='pause', description="pause music")
    async def pause(self, ctx):
        """pause music"""
        player = self.get_player(ctx.guild.id)
        player.pause()
        await ctx.send("pause") 

    @commands.command(name='unpause', description="resume music")
    async def unpause(self, ctx):
        """resume music"""
        player = self.get_player(ctx.guild.id)
        player.unpause()
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


    def get_player(self, guild_id):
        if guild_id in self.players:
            return self.players[guild_id]
        else:
            player = Player(self.get_voice_client(guild_id))
            self.players[guild_id] = player
            return player
        
    def get_voice_client(self, guild_id):
        guilds = self.bot.guilds

        if len(guilds) == 0:
            return None
        
        for guild in guilds:
            if guild.id == guild_id:
                return guild.voice_client

        return None