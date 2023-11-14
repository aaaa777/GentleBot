import asyncio
import discord
from discord import app_commands
from discord.ext import commands

from ..music.player import Player
from ..music.likelist import LikeList
from ..music.mixlist import MixList
from ..music.song import Song

class Command(commands.Cog):


    def __init__(self, bot):
        self.bot = bot
        self.players = {}
        self.mix_mode = False

        self.music_dashboard_message = None


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
        player.voice_client = self.get_voice_client(ctx.guild.id)

        # users = self.get_voice_user_ids(ctx.guild.id)
        # player.update_users(users)

        await message.channel.send("接続しました。")


    # VCから切断するコマンド

    @commands.command(name='leave', description="leave voice channel", aliases=['l'])
    async def leave(self, ctx):
        """leave voice channel"""
        
        message = ctx.message
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。")
            return

        # 切断する
        await message.guild.voice_client.disconnect()
        # self.players.pop(ctx.guild.id)
        await message.channel.send("切断しました。")


    # 再生コマンド

    @commands.command(name='play', description="play music", aliases=['p'])
    async def play(self, ctx):
        """play music"""
        player = self.get_player(ctx.guild.id)

        voice_client = self.get_voice_client(ctx.guild.id)
        if voice_client is None:
            await self.join(ctx)

        # コマンド打った時のLLを読み込む
        mixlist = MixList()
        users = self.get_voice_user_ids(ctx.guild.id)

        for user in users:
            likelist = LikeList.load(user)
            mixlist.add_playlist(likelist)

        
        #likelist = LikeList.load(ctx.author.id)
        player.playlist = mixlist
        self.mix_mode = True

        # 初期3曲を読み込む
        # await player.fill_playlist_3()
        # print('player queue', player.queue)

        asyncio.create_task(player.start())
        self.music_dashboard_message = await player.voice_client.channel.send(self.build_dashboard_message(player))
        # await ctx.send("play")

    @commands.command(name='insert', description="insert music into next queue", aliases=['i'])
    async def insert(self, ctx, arg):
        """insert music into next queue"""
        player = self.get_player(ctx.guild.id)
        player.insert_song_next(Song(url=arg))
        await ctx.send(f"insert {arg}")

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
        player = self.get_player(ctx.guild.id)
        player.skip()
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
        await ctx.send(self.get_player(ctx.guild.id).get_current_song())
        await ctx.send("now")

    @commands.command(name='playlist', description="show playlist", aliases=['pl'])
    async def playlist(self, ctx):
        """show playlist"""
        await ctx.send('\n'.join(self.get_player(ctx.guild.id).next_3_songs()))

    @commands.command(name='like', description="add likelist")
    async def like(self, ctx, arg):
        """add likelist"""
        LikeList.load(ctx.author.id).add_song(arg)

        await ctx.send("like")

    # VCに新しいユーザが入った時に呼ばれる
    @commands.Cog.listener('on_voice_state_update')
    async def on_voice_state_update(self, member, before, after):
        if not self.mix_mode:
            return
        
        print('mixmode: on_voice_state_update')
        print('member', member)
        print('before', before)
        print('after', after)

        player = self.get_player(member.guild.id)

        if before.channel is None and after.channel is not None:
            print('join')
            # VCに新しいユーザが入った時
            # VCに入ったユーザのLLを読み込む
            likelist = LikeList.load(member.id)
            print('likelist', likelist.all_songs)
            print('likelist', likelist)
            # VCに入ったユーザのLLをMixListに追加する
            mixlist = player.playlist
            mixlist.add_playlist(likelist)
            print('mixlist', mixlist)

            await member.guild.voice_client.channel.send("added")

        if before.channel is not None and after.channel is None:
            print('leave')
            # VCからユーザが抜けた時
            # VCにいるユーザのLLをMixListに追加する
            mixlist = player.playlist

            # 抜けたユーザー
            mixlist.remove_playlist_by_user_id(member.id)

            await member.guild.voice_client.channel.send("removed")

    @commands.Cog.listener('on_message')
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return
        
        vc = self.get_voice_client(message.guild.id)
        if not vc or message.channel.id != vc.channel.id:
            return
        
        if self.music_dashboard_message:
            await self.music_dashboard_message.delete()

        self.music_dashboard_message = await message.channel.send(self.build_dashboard_message(self.get_player(message.guild.id)))


    # Utility

    def get_player(self, guild_id):
        if guild_id in self.players:
            return self.players[guild_id]
        else:
            player = Player(bot=self.bot, voice_client=None)
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
    
    def get_voice_user_ids(self, guild_id):
        vc = self.get_voice_client(guild_id)
        if vc is None:
            return None
        return [member.id for member in vc.channel.members if member.bot == False]
    
    def build_dashboard_message(self, player):
        return '<' + '>\n<'.join([str(s) for s in player.next_3_songs()]) + '>'