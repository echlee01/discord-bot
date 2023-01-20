import asyncio
import discord
from discord.ext import commands


#import cog
from music_cog import music_cog
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)


async def setup(bot):
    await bot.add_cog(music_cog(bot))

token = ""
with open("token.txt") as f:
    token = f.read() 

asyncio.run(setup(bot))

bot.run(token)