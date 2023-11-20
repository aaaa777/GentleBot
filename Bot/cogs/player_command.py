import os
import sys

import asyncio
import discord
from discord import Interaction
from discord import app_commands
from discord.ext import commands


from ..music.player import Player
from ..music.playlist import PlayList
from ..music.likelist import LikeList
from ..music.mixlist import MixList
from ..music.song import Song

class Command(commands.Cog):


    def __init__(self, bot):
        self.bot = bot
        self.players = {}
        # self.mix_mode = False
        # self.updating_dashboard = False

        # self.music_dashboard_message = None

    @commands.Cog.listener('on_ready')
    async def on_ready(self):
        print('music on_ready')

    @app_commands.command(name='hello', description="Says hello")
    async def hello(self, ctx: Interaction):
        """Says hello"""
        # await ctx.send("hello")
        await ctx.response.send_message("hello")


    @app_commands.command(name='join', description="join voice channel")
    async def join(self, ctx: Interaction):
        """join voice channel"""
        try:
            # player = self.get_player(ctx.guild.id)

            # コマンドを実行したメンバーがボイスチャンネルに接続しているか確認する
            author = ctx.user
            # if author.voice is None:
            # ボイスチャンネルに接続する
            if self.join_voice_chat(author) is False:
                await ctx.response.send_message("あなたはボイスチャンネルに接続していません。")
                return
            

            # users = self.get_voice_user_ids(ctx.guild.id)
            # player.update_users(users)
            

            await ctx.response.send_message("接続しました。")
        except:
            await ctx.response.send_message("エラーが発生しました。")

    async def join_voice_chat(self, user: discord.Member):
        if user.voice is None:
            return False
        await user.voice.channel.connect()
        player = self.get_player(user.guild.id)
        player.voice_client = self.get_voice_client(user.guild.id)
        return True

    # VCから切断するコマンド

    @app_commands.command(name='leave', description="leave voice channel")
    async def leave(self, ctx):
        """leave voice channel"""
        
        guild = ctx.guild
        if guild.voice_client is None:
            await ctx.response.send_message("接続していません。")
            return

        # 切断する
        await guild.voice_client.disconnect()

        player = self.get_player(guild.id)

        if player:
            player.kill()
            
        # self.players.pop(ctx.guild.id)
        await ctx.response.send_message("切断しました。")


    # 再生コマンド

    @app_commands.command(name='play', description="play music")
    @app_commands.describe(url='url')
    async def play(self, ctx, url: str = None):
        """play music"""
        await ctx.response.send_message("評価した曲リストから再生します")
        try:
            player = self.get_player(ctx.guild.id)

            voice_client = self.get_voice_client(ctx.guild.id)
            if voice_client is None:
                await self.join_voice_chat(ctx.user)

            if url is None:
                # コマンド打った時のLLを読み込む
                playlist = MixList()
                users = self.get_voice_user_ids(ctx.guild.id)

                for user in users:
                    likelist = LikeList.load(user)
                    playlist.add_playlist(likelist)

            else:
                playlist = PlayList()
                playlist.add_song(Song(url=url, user_id=ctx.user.id))

            
            #likelist = LikeList.load(ctx.author.id)
            player.playlist = playlist

            asyncio.create_task(player.start())
            # player.music_dashboard_message = await player.voice_client.channel.send(self.build_dashboard_message(player))
            
        except Exception as e:
            await ctx.channel.send("エラーが発生しました。")
            print(e)
            return
            # .response.send_message("エラーが発生しました。")
        # await ctx.response.message.edit_message("再生準備完了！")

    @app_commands.command(name='insert', description="insert music into next queue")
    @app_commands.describe(url='url')
    async def insert(self, ctx, url: str):
        """insert music into next queue"""
        player = self.get_player(ctx.guild.id)
        player.insert_song_next(Song(url=url, user_id=ctx.user.id))
        await ctx.response.send_message(f"曲がqueue #1に追加されました")
        await player.refresh_dashboard(repost=True)

    @app_commands.command(name='pause', description="pause music")
    async def pause(self, ctx):
        """pause music"""
        player = self.get_player(ctx.guild.id)
        player.pause()
        await ctx.response.send_message("pause") 

    @app_commands.command(name='unpause', description="resume music")
    async def unpause(self, ctx):
        """resume music"""
        player = self.get_player(ctx.guild.id)
        player.unpause()
        await ctx.response.send_message("unpause")

    @app_commands.command(name='skip', description="skip music")
    async def skip(self, ctx):
        """skip music"""
        await ctx.response.send_message("skipping music")
        player = self.get_player(ctx.guild.id)
        player.skip()
        await player.refresh_dashboard(repost=True)

    @app_commands.command(name='repeat', description="repeat music")
    async def repeat(self, ctx):
        """repeat music"""
        await ctx.response.send_message("repeat")
        player = self.get_player(ctx.guild.id)
        player.toggle_repeat()
        await player.refresh_dashboard(repost=True)   

    @app_commands.command(name='shuffle', description="shuffle music")
    async def shuffle(self, ctx):
        """shuffle music"""
        await ctx.response.send_message("shuffle")
        player = self.get_player(ctx.guild.id)
        player.shuffle()
        await player.refresh_dashboard(repost=True)

    @app_commands.command(name='volume', description="volume music")
    async def volume(self, ctx):
        """volume music"""
        await ctx.response.send_message("volume")

    @app_commands.command(name='stop', description="stop music and clear queue")
    async def stop(self, ctx):
        """stop music and clear queue"""
        await ctx.response.send_message("終了します、さよなら・・・")
        player = self.get_player(ctx.guild.id)
        player.kill()
        self.delete_player_by_guild_id(ctx.guild.id)
        # await player.refresh_dashboard(repost=True)

    @app_commands.command(name='save', description="save playlist")
    async def save(self, ctx):
        """save playlist"""
        await ctx.response.send_message("save")

    @app_commands.command(name='load', description="load playlist")
    async def load(self, ctx):
        """load playlist"""
        await ctx.response.send_message("load")

    @load.command()
    async def likelist(self, ctx):
        """load likelist"""
        await ctx.response.send_message("likelist")

    @load.command()
    async def playlist(self, ctx, playlist_name: str):
        """load playlist"""
        await ctx.response.send_message("playlist {playlist_name}}")

    @app_commands.command(name='now', description="now playing")
    async def now(self, ctx):
        """now playing"""
        await ctx.response.send_message(self.get_player(ctx.guild.id).get_current_song())
        # await ctx.response.send_message("now")

    @app_commands.command(name='playlist', description="show playlist")
    async def playlist(self, ctx):
        """show playlist"""
        await ctx.response.send_message('\n'.join(self.get_player(ctx.guild.id).next_3_songs()))

    @app_commands.command(name='like', description="add likelist")
    async def like(self, ctx, arg: str):
        """add likelist"""
        LikeList.load(ctx.user.id).add_song(arg)

        await ctx.response.send_message("like")

    @app_commands.command(name='reboot', description="reboot")
    async def reboot(self, ctx):
        """reboot"""
        await ctx.response.send_message("reboot")
        if ctx.guild.voice_client is not None:
            await ctx.guild.voice_client.disconnect()
        os.execv(sys.executable, ['python'] + sys.argv)


    # update state

    # VCに新しいユーザが入った時に呼ばれる
    @commands.Cog.listener('on_voice_state_update')
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return
        
        player = self.get_player(member.guild.id)

        if not player or player.voice_client is None:
            return

        if not player.mix_mode:
            return
        
        print('mixmode: on_voice_state_update')
        print('member', member)
        print('before', before)
        print('after', after)


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

            # await member.guild.voice_client.channel.send("added")

        if before.channel is not None and after.channel is None:
            print('leave')
            # VCからユーザが抜けた時
            # VCにいるユーザのLLをMixListに追加する
            mixlist = player.playlist

            # 抜けたユーザー
            mixlist.remove_playlist_by_user_id(member.id)

            # await member.guild.voice_client.channel.send("removed")

    @commands.Cog.listener('on_message')
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return
        
        player = self.get_player(message.guild.id)
        vc = player.voice_client
        if not vc or message.channel.id != vc.channel.id:
            return
        
        await player.refresh_dashboard(repost=True)


    # reaction controller
    @commands.Cog.listener('on_reaction_add')
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        
        player = self.get_player(reaction.message.guild.id)
        vc = player.voice_client
        if not vc or reaction.message.channel.id != vc.channel.id:
            return
        
        if reaction.message.id != player.music_dashboard_message.id:
            return

        emoji = reaction.emoji
        await reaction.remove(user)
        message = ""
        if str(emoji) == '⏯️':
            player.pause()
            message = "paused/playing"
        if str(emoji) == '⏭️':
            player.skip()
            message = "skipped"
        if str(emoji) == '🔁':
            player.toggle_repeat()
            message = "repeated" if player.repeat_mode else "not repeated"
        if str(emoji) == '🔀':
            player.shuffle()
            message = "shuffled"
        # if str(emoji) == '⏹':
        #     player.kill()
        #     return
        if str(emoji) == '📄':
            # プレイリストの管理画面に切り替え
            pass
        if str(emoji) == '❌':
            # ダッシュボードを閉じる
            pass

        await player.refresh_dashboard(message=message)

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
    
    def delete_player_by_guild_id(self, guild_id):
        del self.players[guild_id]

    def dispose_player_by_guild_id(self, guild_id):
        player = self.get_player(guild_id)
        player.kill()
        del self.players[guild_id]
        
