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
        print('Message from {0.author}: {0.content}'.format(message))

        if not message.channel.id in self.music_channel_list:
            return
        
        url_list = re.findall(self.__url_pattern, message.content)
        if len(url_list) == 0:
            return
        
        for url in url_list:
            self.save_like_song(message.author.id, url)
        
        await message.add_reaction('♥️')

    def save_like_song(self, user_id, song):
        LikeList.load(user_id).add_song(song)

    @commands.Cog.listener('on_raw_reaction_add')
    async def on_reaction_add(self, event):
        emoji = event.emoji
        message_id = event.message_id
        channel_id = event.channel_id
        user_id = event.user_id

        print('reaction add: {0}'.format(emoji))
        if channel_id in self.music_channel_list:
            return
        
        message = await self.bot.get_channel(channel_id).fetch_message(message_id)
        print(message.content)

        if str(emoji) == '❤️':
            for url in re.findall(self.__url_pattern, message.content):
                self.save_like_song(user_id, url)
        
        if str(emoji) == '💛':
            for url in re.findall(self.__url_pattern, message.content):
                self.save_like_song(message.author.id, url)