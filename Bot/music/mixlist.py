from .playlist import PlayList

class MixList(PlayList):
    def __init__(self):
        self.playlists = []
        super().__init__()
        self.__playlist_cursol = 0

    def add_playlist(self, playlist):
        self.playlists.append(playlist)

    def remove_playlist(self, playlist):
        self.playlists.remove(playlist)

    def remove_playlist_by_index(self, index):
        del self.playlists[index]

    

    def next_song_roundrobin(self):

        for playlist_index in range(len(self.playlists)):

            # playlistのindexを取得する
            turn_index = (self.__playlist_cursol + playlist_index) % len(self.playlists)

            # playlistの中身を取り出す
            playlist_iter = self.playlists[turn_index].iter
            song = next(playlist_iter)

            if song is None:
                continue

            self.all_songs.append(song)
            
            self.__playlist_cursol += 1
            self.__playlist_cursol %= len(self.playlists)

            print('playlist stat:', self.all_songs)
            return song
            
        return None

    def __next__(self):
        # if self.playing_song_index + 1 >= len(self.all_songs):
        #     raise StopIteration

        song = self.next_song_roundrobin()
        if song is None:
            raise StopIteration
        
        self.playing_song_index += 1

        return song
    