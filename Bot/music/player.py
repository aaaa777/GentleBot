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
        self.queue = []
        self.voice_client = voice_client
        # self.__user_likelists = {}
        # self.__playlist = None
        # self.__current_user_index = 0
        self.__current_song_index = -1
        self.playing_coroutine = None


    def set_playlist(self, playlist: PlayList=None):
        self.playlist = playlist


    def fill_playlist_10(self):

        remain = self.song_remains()
        print('remain: {0}'.format(remain))

        for _ in range(10 - remain):
            try:
                self.queue.append(next(self.playlist.iter))
            except StopIteration:
                break


    async def start(self):
        if self.playing_coroutine is not None:
            return
        self.playing_coroutine = asyncio.create_task(self.play_loop())
        # while True:
        #     await self.playing_coroutine
    
    async def play_loop(self):
        print('play_loop started')
        # vc = self.voice_client
        while True:
            # if vc.is_playing():
            #     await asyncio.sleep(1)
            #     continue

            self.fill_playlist_10()
            if False:
                print('cant add playlist no song remains')
                break
            
            song = self.get_next_song()
            # song = self.next_song()

            if song is None:
                print('no song remains, player stopped')
                break
            
            # self.__now_playing_coroutine = asyncio.create_task(vc.play(song))
            # vc.play(song)

            print('playing: {0}, queue: {1}, playlist: {2}'.format(song, str(self.queue), str(self.playlist.all_songs)))
            await asyncio.sleep(1)
            print('playing: {0}'.format(song))
            
            ytdl_player = await YTDLSource.from_url_via_file_stream(song, loop=self.bot.loop)
            # ytdl_player = await YTDLSource.from_url(song, loop=self.bot.loop, stream=True)
            if self.voice_client is None:
                raise ValueError('voice_client is None')
            
            self.voice_client.play(ytdl_player, after=lambda e: print(f'Player error: {e}') if e else None)
            # self.voice_client.play(ytdl_player, after=lambda e: print(f'Player error: {e}') if e else None)

            while self.voice_client.is_playing():
                await asyncio.sleep(1)
            print('song ended')

        print('play_loop ended')
        self.reset_cursor()
        self.playing_coroutine = None
        await self.send_playlist_ended()


    def get_next_song(self):
        try:
            self.__current_song_index += 1
            return self.queue[self.__current_song_index]
        except IndexError:
            return None

    def song_remains(self):
        return len(self.queue) - self.__current_song_index - 1
    
    def reset_cursor(self):
        self.__current_song_index = -1
    
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