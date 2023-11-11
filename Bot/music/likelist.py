import random

from ..api.likelist import LikeListAPI

class LikeList():
    likelist_cache = {}
    def __init__(self, likelist_api: LikeListAPI):
        self.user_id = likelist_api.user_id
        self.likelist_api = likelist_api
        self.current_song_index = -1

        self.fetch_all_songs()

    @classmethod
    def load(self, user_id):
        if user_id in self.likelist_cache:
            return self.likelist_cache[user_id]
        
        likelist_api = LikeListAPI(user_id)
        likelist = LikeList(likelist_api)
        self.likelist_cache[user_id] = likelist

        return likelist
    
    def add_song(self, song):
        self.likelist_api.add_song(song)
        self.songs.append(song)

    def fetch_all_songs(self):
        self.songs = self.likelist_api.get_all_songs()

    def shuffle(self):
        self.songs = random.shuffle(self.songs)

    def __iter__(self):
        return self
    
    def __next__(self):
        self.current_song_index += 1

        if self.current_song_index >= len(self.songs):
            self.current_song_index -= 1
            raise StopIteration
        
        return self.songs[self.current_song_index]

    def next(self):
        try:
            return self.__next__()
        except StopIteration:
            return None
    