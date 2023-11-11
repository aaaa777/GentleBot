
class PlayList():
    
    def __init__(self):
        self.all_songs = []
        self.current_song_index = 0

    def push(self, song):
        self.all_songs.append(song)

    def pop(self):
        pass

    def shuffle(self):
        pass

    def insert_after(self, index, song):
        pass

    def insert_next(self, song):
        self.insert_after(self.current_song_index, song)

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_song_index >= len(self.all_songs):
            raise StopIteration
        
        self.current_song_index += 1
        
        return self.all_songs[self.current_song_index - 1]