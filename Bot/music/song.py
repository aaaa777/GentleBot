class Song:
    music_type_list = [
        'bgm',
        'pop',
        'classic',
        'mad',
    ]
    def __init__(self, title: str, url: str, duration: int, thumbnail: str, start_time: int=None, end_time: int=None, music_type: str=None):
        self.title = title
        self.url = url
        self.duration = duration
        self.thumbnail = thumbnail

    def __str__(self):
        return f'{self.title} - {self.duration // 60}:{self.duration % 60:02d}'