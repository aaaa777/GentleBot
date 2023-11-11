import random

class LikeList():
    def __init__(self, user_id):
        self.user_id = user_id
        self.songs = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n']
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
    