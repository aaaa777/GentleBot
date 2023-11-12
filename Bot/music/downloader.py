# This example requires the 'message_content' privileged intent to function.

import asyncio
import discord
import os
import re

from subprocess import run, PIPE, Popen, DEVNULL, STDOUT, CalledProcessError, TimeoutExpired
from yt_dlp import YoutubeDL
from discord.ext import commands

# Suppress noise about console usage from errors
#YoutubeDL.utils.bug_reports_message = lambda: ''
max_volume_re = re.compile(r"max_volume: (-?\d+\.\d+) dB")

outtmpl = '%(extractor)s-%(id)s.%(ext)s'

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': outtmpl,
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

ffmpeg_options = {
    'options': '-vn',
    'pipe': True,
}

ytdl = YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.2):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        await cls.download_metadata(url)

        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        print(data['url'])
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
    
    @classmethod
    async def from_url_via_file_stream(cls, url, *, loop=None):
        try:
            data = await cls.download_metadata(url)
        except:
            raise Exception('download metadata failed')

        # TODO: プレイリストやプロバイダ毎の処理をここに書く

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]


        # ダウンロード処理
        # メタデータから生成されるファイル名を推測
        #filename = f"{data['extractor']}-{data['id']}.{data['ext']}"
        filename = outtmpl % data
        filename_part = f"{filename}.part"
        file_ext = data['ext']

        # 一時ファイルがあれば削除
        if os.path.exists(f'tmp/{filename_part}'):
            os.remove(f'tmp/{filename_part}')

        # yt-dlpのダウンロード処理を実行
        res = cls.download_with_ytdl(url)

        print('downloading into', filename)


        # 一時ファイルのpipeを取得
        # 10秒間ダウンロードが進まなかったらタイムアウト
        f = None
        retry_count = 0
        while not f and retry_count < 20:
            try:
                print('try to open part')
                f = open(f'tmp/{filename_part}', 'rb')
            except:
                print('part not found')
            
            if f is None:
                try:
                    print('try to open cache')
                    f = open(f'tmp/{filename}', 'rb')
                except:
                    print(f'cache not found. retrying {retry_count}')
            retry_count += 1
            await asyncio.sleep(0.5)

        if f is None:
            return None
        
        # 音量を取得
        volume = await cls.get_volume(f)
        print(f'volume gain: {volume} -> {-volume} dB')

        f.seek(0)

        # ffmpegでエンコード
        print('encoding with ffmpeg')
        return cls(discord.FFmpegPCMAudio(f, **cls.ffmpeg_options(volume=-volume)), data=data)
    
    @classmethod
    async def download_metadata(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        return data
    

    @classmethod
    def download_with_ytdl(cls, url, *, dir='tmp', loop=None):
        command = 'yt-dlp'
        args = [
            '--format', 'bestaudio/best',
            # '--paths', dir,
            '--output', f'{dir}/{outtmpl}',
            '--restrict-filenames',
            '--no-playlist',
            '--no-check-certificate',
            # 'ignoreerrors',
            # 'logtostderr',
            # 'quiet':,
            # 'no_warnings':,
            '--default-search', 'auto',
            #'--source-address', '0.0.0.0',
        ]

        #ytdl_result = run([command, *args, url])
        loop = loop or asyncio.get_event_loop()
        ytdl_result = loop.run_in_executor(None, lambda: run([command, *args, url],))
        
        return ytdl_result

    # 前30秒の音量を取得する
    @classmethod
    async def get_volume(self, file):
        command = 'ffmpeg'
        args = [
            '-i', '-',
            '-vn',
            '-af', 'volumedetect',
            '-f', 'null', '-'
        ]

        # ffmpegの実行
        loop = asyncio.get_event_loop()
        ffmpeg_result = await loop.run_in_executor(None, lambda: run([command, *args], stdin=file, stdout=PIPE, stderr=STDOUT, timeout=10))
        out = ffmpeg_result.stdout.decode("utf8")
        
        # 音量を取得
        print(out)
        match = max_volume_re.search(out)
        a, b = match.group(1), float(match.group(1))
        return float(match.group(1)) if match else 0.0
    
    @classmethod
    def ffmpeg_options(cls, volume=0.0):
        return {
            'options': f'-af volume={volume}dB',
            'pipe': True,
        }

