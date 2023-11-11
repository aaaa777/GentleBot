import asyncio
import discord
from discord import app_commands
from discord.ext import commands

from Bot.music.downloader import YTDLSource

from .playlist import PlayList
from .likelist import LikeList
from ..api.likelist import LikeListAPI

class Player():
    
    def __init__(self, bot: commands.Bot, voice_client: discord.voice_client) -> None:
        self.playlist = PlayList()
        self.bot = bot
        self.users = []
        self.voice_client = voice_client
        self.__user_likelists = {}
        # self.__playlist = None
        self.__current_user_index = 0
        self.__current_song_index = -1
        self.playing_coroutine = None


    def set_playlist(self, playlist: PlayList=None):
        self.playlist = playlist

    def add_user(self, user_id):
        self.users.append(user_id)
        self.__user_likelists[user_id] = LikeList(likelist_api=LikeListAPI(user_id))

    def update_users(self, user_ids):
        self.users = user_ids
        for user_id in user_ids:
            if user_id not in self.__user_likelists:
                self.__user_likelists[user_id] = LikeList(likelist_api=LikeListAPI(user_id))

    def fill_playlist_10(self):
        if(len(self.users) == 0):
            return

        remain = self.song_remains()
        print('remain: {0}'.format(remain))

        for _ in range(10 - remain):
            turn_user_id = self.users[self.__current_user_index]

            song = self.next_like_song(turn_user_id)

            if song is not None:
                self.playlist.push(song)
            
            self.__current_user_index += 1
            self.__current_user_index %= len(self.users)
        
        # print('playlist stat:', self.playlist.all_songs)

    async def start(self):
        if self.playing_coroutine is not None:
            return
        self.playing_coroutine = asyncio.create_task(self.play_loop())
        # while True:
        #     await self.playing_coroutine
    
    async def play_loop(self):
        print('play_loop started')
        vc = self.voice_client
        while True:
            # if vc.is_playing():
            #     await asyncio.sleep(1)
            #     continue

            self.fill_playlist_10()
            if False:
                print('cant add playlist no song remains')
                break

            # song = self.playlist_iter.next()
            song = self.next_song()

            if song is None:
                print('no song remains, player stopped')
                break
            
            # self.__now_playing_coroutine = asyncio.create_task(vc.play(song))
            # vc.play(song)
            await asyncio.sleep(1)
            print('playing: {0}'.format(song))
            
            ytdl_player = await YTDLSource.from_url(song, loop=self.bot.loop, stream=True)
            vc.play(ytdl_player, after=lambda e: print(f'Player error: {e}') if e else None)
            # vc.play(ytdl_player, after=lambda e: print(f'Player error: {e}') if e else None)

            while vc.is_playing():
                await asyncio.sleep(1)

        print('play_loop ended')
        self.reset_cursor()
        self.playing_coroutine = None
        await self.send_playlist_ended()

    # async def play_next(self, e=None):
    #     if e is not None:
    #         print('Player error: {0}'.format(e))

    #     vc = self.voice_client
    #     if vc is None:
    #         return
    #     self.fill_playlist_10()
    #     song = self.next_song()
    #     if song is None:
    #         print('no song remains, player stopped')
    #         return
    #     print('playing: {0}'.format(song))
        
    #     ytdl_player = await YTDLSource.from_url(song, loop=self.bot.loop, stream=False)
    #     vc.play(ytdl_player, after=self.play_next)
    #     # vc.play(ytdl_player, after=lambda e: print(f'Player error: {e}') if e else None)

    def song_remains(self):
        return len(self.playlist.all_songs) - self.__current_song_index - 1

    # 内部カウントを使うイテレータ
    def next_song(self):
        self.__current_song_index += 1

        if self.__current_song_index >= len(self.playlist.all_songs):
            return None
        
        return self.playlist.all_songs[self.__current_song_index]
    
    def reset_cursor(self):
        self.__current_song_index = -1
    
    def next_like_song(self, user_id):
        return self.__user_likelists[user_id].next()

    def pause(self):
        pass

    def skip(self):
        vc = self.voice_client
        if vc is None:
            return
        if vc.is_playing():
            vc.stop()
        else:
            # TODO fix
            self.next_song()

    def repeat(self):
        pass

    def shuffle(self):
        pass

    def volume(self):
        pass

    def save_playlist(self):
        pass

    def load_playlist(self):
        pass


    # message responder

    async def send_playlist_ended(self):
        await self.voice_client.channel.send('playlist ended')