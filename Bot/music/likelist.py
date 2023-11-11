import random

from ..api.likelist import LikeListAPI

class LikeList():
    def __init__(self, likelist_api: LikeListAPI):
        self.user_id = likelist_api.user_id
        self.songs = ['https://www.youtube.com/watch?v=B_BRs_DTvqo', 'https://www.youtube.com/watch?v=9wh8FgsEtNQ', 'https://www.youtube.com/watch?v=0E1TQNrYVEg']
        self.current_song_index = -1

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
    