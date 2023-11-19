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
        self.__playlist = PlayList()
        self.bot = bot
        self.users = []
        self.queue = []
        self.repeat_mode = False
        self.voice_client = voice_client
        self.skip_flag = False
        self.voice_channel = voice_client.channel if voice_client else None
        self.mix_mode = False

        self.music_dashboard_message = None
        self.music_dashboard_message_text = ""
        self.dashboard_loop_running = False
        # self.__user_likelists = {}
        # self.__playlist = None
        # self.__current_user_index = 0
        self.__current_song_index = -1
        self.playing_coroutine = None

        # ダッシュボードの更新ループを開始
        asyncio.create_task(self.update_dashboard_loop())

    @property
    def voice_client(self):
        # TODO: vcが無くなった場合の処理
        return self.__voice_client
    
    @voice_client.setter
    def voice_client(self, voice_client: discord.voice_client):
        self.voice_channel = voice_client.channel if voice_client else None
        self.__voice_client = voice_client

    # def set_playlist(self, playlist: PlayList=None):
    #     self.playlist = playlist
    @property
    def playlist(self):
        return self.__playlist
    
    @playlist.setter
    def playlist(self, playlist: PlayList):
        self.__playlist = playlist
        self.reset_cursor()

    # 操作系

    # 再生を開始する
    async def start(self):
        if self.playing_coroutine is not None:
            return
        self.playing_coroutine = asyncio.create_task(self.play_loop())

    # 再生を停止する
    async def stop(self):
        if self.playing_coroutine is None:
            return
        self.playing_coroutine.cancel()
        self.playing_coroutine = None
    
    # 再生のループ
    # タスク化してstart()で呼び出す
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
                    
                    # print('playing: {0}, queue: {1}, playlist: {2}'.format(song, str(self.queue), str(self.playlist.all_songs)))
                    print('playing: {0}, queue: {1}'.format(song, str(self.queue[-3:])))

                    try:
                        music_source = await YTDLSource.from_song_object(song, loop=self.bot.loop)
                    except Exception as e:
                        print(e)
                        # 一つの動画ダウンロードに失敗した場合スキップする
                        break
                    
                    # vcが無くなった場合、直ちに再生を終了する
                    if self.voice_client is None:
                        raise ValueError('voice_client is None')
                
                    # 再生
                    self.voice_client.play(music_source, after=lambda e: print(f'Player error: {e}') if e else None)

                    # 再生が終わるまでの待ち判定
                    while self.voice_client.is_playing():
                        await asyncio.sleep(1)
                    print('song ended')
                    
                    # self.refresh_dashboard()

                    # リピートモードの場合はsongをそのままにして再生
                    if not self.repeat_mode:
                        break

                    print('repeat mode enabled, play again')
        except Exception as e:
            print(e)
            return
        finally:
            print('play_loop ended')
            self.reset_cursor()
            self.playing_coroutine = None

        await self.send_playlist_ended()
        await self.refresh_dashboard(repost=True)

    
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

    def toggle_repeat(self):
        self.repeat_mode = not self.repeat_mode

    def shuffle(self):
        pass

    def volume(self):
        pass

    def save_playlist(self):
        pass

    def load_playlist(self):
        pass

    def kill(self):
        pass

    
    # 内部操作系

    # 3曲分のキューをプレイリストから読んで埋める
    async def fill_playlist_3(self):
        remain = self.song_remains()

        # print('remain: {0}'.format(remain))
        for _ in range(3 - remain):
            try:
                song = next(self.playlist.iter)
                self.queue.append(song)
            except StopIteration:
                break


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
            return self.queue[self.__current_song_index:self.__current_song_index + 4]
        except IndexError:
            return self.queue[self.__current_song_index:]
        
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


    # dashboard message

    # 音楽の表示を更新するループ
    async def update_dashboard_loop(self):
        # アップデートループが実行されている場合はループを終了
        if self.dashboard_loop_running:
            return
        
        # アップデートループをロック
        self.dashboard_loop_running = True
        try:
            while True:
                await self.bot.change_presence(activity=discord.Game(name='music'))
                
                # 情報を更新
                await self.refresh_dashboard(repost=self.music_dashboard_message is None)
                await asyncio.sleep(10)
        except Exception as e:
            print(e)
            self.dashboard_loop_running = False

    # async def post_dashboard(self, player: Player):
    #     await player.voice_client.channel.send(self.build_dashboard_message(self.get_player(player.voice_client.guild.id)))

    async def refresh_dashboard(self, repost=False, message=None):
        if self.voice_channel is None:
            return

        old_message = self.music_dashboard_message
        # 再投稿オンの場合は投稿する
        # content = self.build_dashboard_message()
        if message:
            self.music_dashboard_message_text = message
        content = self.music_dashboard_message_text
            
        embed = await self.build_dashboard_embed_queue()
        if repost:
            self.music_dashboard_message = await self.voice_channel.send(content=content, embed=embed)
        
            # 古い投稿が残っている場合削除する
            if old_message:
                await old_message.delete()

        else:
            # 再投稿オフの場合は投稿がなければ投稿する
            if self.music_dashboard_message is None:
                self.music_dashboard_message = await self.voice_channel.send(content=content, embed=embed)

            # 投稿があれば更新する
            else:
                await self.music_dashboard_message.edit(content=content, embed=embed)
                return

        # await self.music_dashboard_message.add_reaction('⏯️')
        await self.music_dashboard_message.add_reaction('⏭️')
        await self.music_dashboard_message.add_reaction('🔁')
        await self.music_dashboard_message.add_reaction('🔀')
            
        # self.music_dashboard_message = None

    async def remove_dashboard(self):
        if self.music_dashboard_message:
            await self.music_dashboard_message.delete()
            self.music_dashboard_message = None

    # message responder

    async def send_playlist_ended(self):
        await self.voice_client.channel.send('playlist ended')

    def build_dashboard_message(self):
        return '<' + '>\n<'.join([s.await_metadata and str(s) for s in self.next_3_songs()]) + '>'
    
    async def build_dashboard_embed_queue(self):
        # 現在の曲を表示
        now_song = self.get_current_song()
        embed = discord.Embed(
            title="now {1}: {0}".format(now_song.title, "repeating" if self.repeat_mode else "playing"),
            # description=now_song.description,
            url=now_song.url,

            color=0xeee657,
        )
        embed.set_thumbnail(url=now_song.thumbnail)

        # 追加したユーザを表示
        user = await self.bot.fetch_user(now_song.user_id)
        if user:
            embed.set_author(name="added by: {0}".format(user.name), icon_url=user.avatar.url)

        # queueの残りを表示
        for i, song in enumerate(self.next_3_songs()):
            if i == 0:
                continue
            embed.add_field(
                name="queue #{0}".format(i),
                value="{0}".format(str(song)),
                inline=False
            )
        return embed
    