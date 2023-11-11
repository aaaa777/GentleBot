import asyncio

from .playlist import PlayList
from .likelist import LikeList

class Player():
    
    def __init__(self, voice_client) -> None:
        self.playlist = PlayList()
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
        self.__user_likelists[user_id] = LikeList(user_id)

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
        
        print('playlist stat:', self.playlist.all_songs)

    def start(self):
        self.playing_coroutine = asyncio.create_task(self.play_loop())
    
    async def play_loop(self):
        print('play_loop started')
        vc = self.voice_client
        while True:
            # if vc.is_playing():
            #     await asyncio.sleep(1)
            #     continue

            self.fill_playlist_10()
            if self.song_remains() == 0:
                print('no song remains')
                break

            # song = self.playlist_iter.next()
            song = self.next_song()

            if song is None:
                print('no song')
                break
            
            # vc.play(song)
            await asyncio.sleep(1)
            print('playing: {0}'.format(song))
            print(song)

    def song_remains(self):
        return len(self.playlist.all_songs) - self.__current_song_index - 1

    def next_song(self):
        self.__current_song_index += 1

        if self.__current_song_index >= len(self.playlist.all_songs):
            return None
        
        return self.playlist.all_songs[self.__current_song_index]
    
    def next_like_song(self, user_id):
        return self.__user_likelists[user_id].next()

    def pause(self):
        pass

    def skip(self):
        pass

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