from discord.ext import commands

class ChannelObserver(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener('on_message')
    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))