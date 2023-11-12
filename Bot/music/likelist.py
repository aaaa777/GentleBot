import random

from .playlist import PlayList
from ..api.likelist import LikeListAPI

class LikeList(PlayList):

    likelist_cache = {}

    def __init__(self, likelist_api: LikeListAPI):
        self.user_id = likelist_api.user_id
        if likelist_api is None:
            raise Exception('likelist_api is None')
        self.likelist_api = likelist_api
        # self.current_song_index = -1

        super().__init__()

        # self.all_songs初期化後に実行
        self.fetch_all_songs()
        print('likelist init: {0}'.format(self.all_songs))

    @classmethod
    def load(cls, user_id):
        if user_id in cls.likelist_cache:
            return cls.likelist_cache[user_id]
        
        likelist = cls(likelist_api=LikeListAPI(user_id))
        cls.likelist_cache[user_id] = likelist

        return likelist
    
    def add_song(self, song):
        self.likelist_api.add_song(song)
        self.all_songs.append(song)

    def fetch_all_songs(self):
        self.all_songs = self.likelist_api.get_all_songs()

    
    # def __iter__(self):
    #     return self
    
    # def __next__(self):
    #     self.current_song_index += 1

    #     if self.current_song_index >= len(self.songs):
    #         self.current_song_index -= 1
    #         raise StopIteration
        
    #     return self.songs[self.current_song_index]

    # def next(self):
    #     try:
    #         return self.__next__()
    #     except StopIteration:
    #         return None
    