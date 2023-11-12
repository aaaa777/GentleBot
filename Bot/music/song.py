class Song:
    def __init__(self, title: str, url: str, duration: int, thumbnail: str):
        self.title = title
        self.url = url
        self.duration = duration
        self.thumbnail = thumbnail

    def __str__(self):
        return f'{self.title} - {self.duration // 60}:{self.duration % 60:02d}'