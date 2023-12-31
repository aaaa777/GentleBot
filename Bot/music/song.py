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

        # for system
        'proc_status'
    ]

    metadata_cache = {}

    def __init__(self, url: str, user_id: str, start_time: int=None, end_time: int=None, music_type: str=None):
        if url is None:
            raise ValueError('Song constructor: url is None')

        self.proc = None
        self.__metadata = None
        self.url = url
        self.music_type = music_type
        self.user_id = user_id

        self.title = 'Loading...{0}'.format(url)
        self.duration = 0
        self.thumbnail = None
        self.description = None
        self.view_count = None
        self.comment_count = None
        self.like_count = None

        # メタデータのダウンロードを非同期で実行
        asyncio.create_task(self.async_init_metadata2())

    @property
    def metadata(self):
        return self.__metadata

    @metadata.setter
    def metadata(self, metadata):
        self.__metadata = metadata

    # メタデータを読み取る前に呼び出すと、メタデータのダウンロードを待ちます。
    async def await_metadata(self):
        while self.metadata is None:
            # TODO: ダウンロードに失敗した場合のタイムアウト処理
            await asyncio.sleep(1)
        return self.metadata

    async def async_init_metadata2(self):
        if self.proc is not None:
            return
        
        if self.url is None:
            raise Exception('song url is None')
        
        # メタデータを取得
        # メタデータのキャッシュがあればそれを使う
        if self.url in self.metadata_cache:
            metadata = self.metadata_cache[self.url]
            
        # キャッシュがなければyt-dlpを実行
        else:
            self.proc = await asyncio.create_subprocess_shell(' '.join(['yt-dlp', '--dump-json', '--format', 'bestaudio/best', self.url]), stdout=PIPE, stderr=STDOUT)

            try:
                # communicateメソッドでプロセスの終了を待ち、出力を取得
                stdout, _ = await self.proc.communicate()
                outs = stdout

                # なぜかJSONの後に謎の文字列が混入する場合があるため、一行目のJSONのみ取り出す
                outs = outs.splitlines()[0]
                metadata = json.loads(outs)

            except Exception as e:
                print(e)
                self.proc.kill()
                self.proc = None
                metadata = {
                    'proc_status': 'error',
                    'title': 'Unknown',
                }

            if 'proc_status' not in metadata:
                metadata['proc_status'] = 'ok'

            # キーでフィルタリング
            metadata = {key: metadata[key] for key in self.metadata_filter if key in metadata}
            
            # キャッシュにセット
            self.metadata_cache[self.url] = metadata

        # メタデータをプロパティにセット
        self.title = metadata['title'] if 'title' in metadata else None
        self.duration = metadata['duration'] if 'duration' in metadata else None
        self.thumbnail = metadata['thumbnail'] if 'thumbnail' in metadata else None
        self.description = metadata['description'] if 'description' in metadata else None
        self.view_count = metadata['view_count'] if 'view_count' in metadata else None
        self.comment_count = metadata['comment_count'] if 'comment_count' in metadata else None
        self.like_count = metadata['like_count'] if 'like_count' in metadata else None
        self.metadata = metadata

        return metadata


    def __str__(self):
        return f'{self.title} - {int(self.duration // 60)}:{(int)(self.duration % 60):02d}'