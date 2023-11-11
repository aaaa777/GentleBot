from discord.ext import commands
import re

from ..api.music_channel import MusicChannelAPI
from ..music.likelist import LikeList

class ChannelObserver(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.music_channel_api = MusicChannelAPI()
        self.music_channel_list = self.music_channel_api.get_music_channel_list()
        self.__url_pattern = "https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"

    @commands.Cog.listener('on_message')
    async def on_message(self, message):
        if message.channel.id in self.music_channel_list:
            return
        print('Message from {0.author}: {0.content}'.format(message))
        
        url_list = re.findall(self.__url_pattern, message.content)
        if len(url_list) == 0:
            return
        
        for url in url_list:
            self.save_like_song(message.author.id, url)

    def save_like_song(self, user_id, song):
        LikeList.load(user_id).add_song(song)