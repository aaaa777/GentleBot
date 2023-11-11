from .playlist import Playlist

class Player():
    
    def __init__(self) -> None:
        pass

    def set_playlist(self, playlist: Playlist=None):
        self.playlist = playlist

    def start(self):
        pass

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