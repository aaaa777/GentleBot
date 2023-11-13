import asyncio
import discord
from discord import app_commands
from discord.ext import commands

from Bot.music.downloader import YTDLSource

from .playlist import PlayList
from .likelist import LikeList
from .song import Song

class Player():
    
    def __init__(self, bot: commands.Bot, voice_client: discord.voice_client) -> None:
        self.playlist = PlayList()
        self.bot = bot
        self.users = []
        self.queue = []
        self.repeat_mode = False
        self.voice_client = voice_client
        self.skip_flag = False
        # self.__user_likelists = {}
        # self.__playlist = None
        # self.__current_user_index = 0
        self.__current_song_index = -1
        self.playing_coroutine = None


    def set_playlist(self, playlist: PlayList=None):
        self.playlist = playlist


    async def fill_playlist_3(self):

        remain = self.song_remains()
        print('remain: {0}'.format(remain))

        for _ in range(3 - remain):
            try:
                song = next(self.playlist.iter)
                await song.download_metadata()
                self.queue.append(song)
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
        try:
            while True:

                await self.fill_playlist_3()

                song = self.get_next_song()

                if song is None:
                    print('no song remains, player stopped')
                    break
                
                # repeat loop
                while True:
                    
                    print('playing: {0}, queue: {1}, playlist: {2}'.format(song, str(self.queue), str(self.playlist.all_songs)))

                    try:
                        ytdl_player = await YTDLSource.from_url_via_file_stream(song, loop=self.bot.loop)
                    except Exception as e:
                        # 一つの動画ダウンロードに失敗した場合スキップする
                        break
                    
                    # vcが無くなった場合、直ちに再生を終了する
                    if self.voice_client is None:
                        raise ValueError('voice_client is None')
                
                    self.voice_client.play(ytdl_player, after=lambda e: print(f'Player error: {e}') if e else None)

                    # 再生が終わるまでの待ち判定
                    while self.voice_client.is_playing():
                        await asyncio.sleep(1)
                    print('song ended')

                    # リピートモードの場合はsongをそのままにして再生
                    if not self.repeat_mode:
                        print('repeat mode enabled, play again')
                        break
        except Exception as e:
            print(e)
            return
        finally:
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
        
    def get_current_song(self):
        if self.__current_song_index < 0:
            return None
        try:
            return self.queue[self.__current_song_index]
        except IndexError:
            return None
        
    # 次の3曲を返す
    def next_3_songs(self):
        try:
            return self.queue[self.__current_song_index + 1:self.__current_song_index + 4]
        except IndexError:
            return self.queue[self.__current_song_index + 1:]
        
    # 割り込みで次の曲に挿入する
    def insert_song_next(self, song):
        self.queue.insert(self.__current_song_index + 1, song)
        print('queue: {0}'.format(str(self.queue)))

    # queue内残り曲数を返す
    def song_remains(self):
        return len(self.queue) - self.__current_song_index - 1
    
    # queueのインデックスをリセットする
    def reset_cursor(self):
        self.__current_song_index = -1
    
    def pause(self):
        vc = self.voice_client
        if vc is None:
            return
        if vc.is_playing():
            vc.pause()

    def unpause(self):
        vc = self.voice_client
        if vc is None:
            return
        if vc.is_paused():
            vc.resume()

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
        self.repeat_mode = True

    def unrepeat(self):
        self.repeat_mode = False

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