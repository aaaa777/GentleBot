import random

class PlayList():
    
    def __init__(self):
        if not hasattr(self, 'all_songs'):
            self.all_songs = []
        self.playing_song_index = -1
        self.iter = iter(self)

    def add_song(self, song):
        self.all_songs.append(song)

    def shuffle(self):
        random.shuffle(self.all_songs)

    def insert_after(self, index, song):
        if index < len(self.all_songs):
            self.all_songs.insert(index + 1, song)
        else:
            print("Index out of range. Song not inserted.")

    def reset_index(self):
        self.playing_song_index = -1

    def index_of(self, song):
        return self.all_songs.index(song)

    def now_playing(self):
        return self.all_songs[self.playing_song_index]
    
    def song_remains(self):
        return len(self.all_songs) - self.playing_song_index - 1

    def __iter__(self):
        return self

    def __next__(self):
        if self.playing_song_index + 1 >= len(self.all_songs):
            raise StopIteration

        self.playing_song_index += 1
        
        return self.all_songs[self.playing_song_index]
