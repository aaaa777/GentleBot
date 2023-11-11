class PlayList():
    
    def __init__(self):
        self.all_songs = []
        self.__temp_song_index = -1

    def push(self, song):
        self.all_songs.append(song)

    def pop(self):
        pass

    def shuffle(self):
        pass

    def insert_after(self, index, song):
        pass

    def __iter__(self):
        return self

    def __next__(self):
        self.__temp_song_index += 1

        if self.__temp_song_index >= len(self.all_songs):
            self.__temp_song_index -= 1
            raise StopIteration
        
        return self.all_songs[self.__temp_song_index]
