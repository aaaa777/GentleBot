import os
from .gasql import GASQL
from ..music.song import Song

class LikeListAPI():
    def __init__(self, user_id):
        self.user_id = user_id
        self.songs = []
        self.conn = GASQL(
            endpoint=os.getenv("GASQL_ENDPOINT"),
            access_token=os.getenv("GASQL_ACCESS_TOKEN")
        )
    
    def get_all_songs(self):
        # self.songs = ['https://www.youtube.com/watch?v=B_BRs_DTvqo', 'https://www.youtube.com/watch?v=9wh8FgsEtNQ', 'https://www.youtube.com/watch?v=0E1TQNrYVEg']
        res = self.conn.select(table='likelist', where={'w_col': 'user_id', 'w_op': '=', 'w_val': self.user_id})
        
        if res['status'] == 'ok':
            self.songs = [Song(url=row['url']) for row in res['records']]
            print('likelist loaded:', self.songs)

        return self.songs
    
    def add_song(self, song: Song):
        res = self.conn.insert(table='likelist', data={'user_id': self.user_id, 'url': song.url})
        if res['status'] == 'ok':
            self.songs.append(song)
            print('likelist added:', song)