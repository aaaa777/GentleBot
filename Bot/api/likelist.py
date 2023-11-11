class LikeListAPI():
    def __init__(self, user_id):
        self.user_id = user_id
        self.songs = []
    
    def get_all_songs(self):
        self.songs = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
        return self.songs