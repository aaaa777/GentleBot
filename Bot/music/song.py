import asyncio
import json
from asyncio.subprocess import PIPE, DEVNULL, STDOUT
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

    metadata_filter = [
        # for display info
        'title',
        'duration',
        'thumbnail',
        'description',
        'view_count',
        'comment_count',
        'like_count',

        # for output template
        'extractor',
        'id',
        'ext',
    ]

    metadata_cache = {}

    def __init__(self, url: str, start_time: int=None, end_time: int=None, music_type: str=None):
        # loop = asyncio.get_event_loop()
        # loop.run_in_executor(None, lambda: self.download_metadata())
        # metadata_cor = self.download_metadata()
        # self.metadata_cor = metadata_cor
        self.proc = None
        self.metadata = None
        self.url = url
        # self.start_download_metadata(url)
        self.music_type = music_type

        self.title = 'Loading...'
        self.duration = 0
        self.thumbnail = None
        self.description = 'Loading...'
        self.view_count = None
        self.comment_count = None
        self.like_count = None

        loop = asyncio.get_event_loop()
        asyncio.create_task(self.async_init_metadata())

    async def async_init_metadata(self):
        self.proc = 'awaiting'
        loop = asyncio.get_running_loop()
        await self.start_download_metadata(self.url)
        # await self.start_download_metadata(self.url)
        await self.sync_metadata()


    async def start_download_metadata(self, url):
        if self.proc != 'awaiting' and self.proc is not None:
            return
        
        if url in self.metadata_cache:
            return self.metadata_cache[url]
        self.proc = await asyncio.create_subprocess_shell(' '.join(['yt-dlp', '--dump-json', '--format', 'bestaudio/best', url]), stdout=PIPE, stderr=STDOUT)

    async def get_metadata(self):
        if self.url in self.metadata_cache:
            return self.metadata_cache[self.url]
        
        if self.proc is None:
            return None
        
        if self.proc == 'awaiting':
            while self.proc == 'awaiting':
                await asyncio.sleep(1)

        try:
            # communicateメソッドでプロセスの終了を待ち、出力を取得します。
            stdout, _ = await self.proc.communicate()
            outs = stdout.decode()

        except Exception as e:
            print(e)
            self.proc.kill()
            self.proc = None
            outs = "{'proc_status': 'error'}"
        
        metadata = json.loads(outs)
        if 'proc_status' not in metadata:
            metadata['proc_status'] = 'ok'
        return metadata

    async def sync_metadata(self):
        
        # metadata = ytdl.extract_info(url, download=False)
        # metadata = self.get_download_metadata()
        # loop = asyncio.get_event_loop()
        # task = loop.create_task(self.get_metadata())
        metadata = await self.get_metadata()
        # print(metadata)

        metadata = {key: metadata[key] for key in self.metadata_filter if key in metadata}

        self.title = metadata['title']
        self.duration = metadata['duration']
        self.thumbnail = metadata['thumbnail']
        self.description = metadata['description']
        self.view_count = metadata['view_count']
        self.comment_count = metadata['comment_count']
        self.like_count = metadata['like_count'] if 'like_count' in metadata else None
        self.metadata = metadata

        self.metadata_cache[self.url] = metadata
        return metadata
    
    # async def await_data(self):
    #     await self.metadata_cor

    def __str__(self):
        # self.sync_metadata()
        return f'{self.title} - {self.duration // 60}:{(int)(self.duration % 60):02d}'