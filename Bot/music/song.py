import asyncio
from yt_dlp import YoutubeDL

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': False,
    'no_warnings': False,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ytdl = YoutubeDL(ytdl_format_options)

class Song:
    music_type_list = [
        'bgm',
        'pop',
        'classic',
        'mad',
    ]

    metadata_cache = {}

    def __init__(self, url: str, start_time: int=None, end_time: int=None, music_type: str=None):
        # metadata_cor = self.download_metadata()
        # self.metadata_cor = metadata_cor
        self.url = url
        self.music_type = music_type

        self.title = ''
        self.duration = 0
        self.thumbnail = None
        self.description = ''
        self.view_count = None
        self.comment_count = None
        self.like_count = None

    async def download_metadata(self):
        url = self.url
        if url in self.metadata_cache:
            return self.metadata_cache[url]
        
        metadata = ytdl.extract_info(url, download=False)
        self.title = metadata['title']
        self.duration = metadata['duration']
        self.thumbnail = metadata['thumbnail']
        self.description = metadata['description']
        self.view_count = metadata['view_count']
        self.comment_count = metadata['comment_count']
        self.like_count = metadata['like_count'] if 'like_count' in metadata else None
        self.metadata_cache[url] = ytdl.extract_info(url, download=False)
        return self.metadata_cache[url]

    def __str__(self):
        return f'{self.title} - {self.duration // 60}:{self.duration % 60:02d}'