import os
from .gasql import GASQL

class MusicChannelAPI():
    def __init__(self):
        self.music_channel_id_list = None
        self.conn = GASQL(
            endpoint=os.getenv("GASQL_ENDPOINT"),
            access_token=os.getenv("GASQL_ACCESS_TOKEN")
        )
    
    def get_music_channel(self, guild_id: str):
        where = {'w_col': 'guild_id', 'w_op': '=', 'w_val': guild_id}
        res = self.conn.select(table='music channel', where=where)
        
        if res['status'] == 'ok':
            first_row = res['records'][0]
            if first_row is None:
                return None
            
            music_channel_id = first_row['music_channel_id']
            print('music ch loaded:', music_channel_id)

        return self.music_channel_id
    
    def get_music_channel_list(self):
        res = self.conn.select(table='music channel', where=None)
        
        if res['status'] == 'ok':
            self.music_channel_id_list = [row['music_channel_id'] for row in res['records']]
            print('music ch list loaded:', self.music_channel_id_list)

        return self.music_channel_id_list