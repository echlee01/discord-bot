import asyncio
import discord
from discord.ext import commands


#import cog
from music_cog import music_cog
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)



# client = discord.Client(intents=discord.Intents.default())

# @client.event
# async def on_ready():
#     print(f'We have logged in as {client.user}')

# @client.event
# async def on_message(message):
#     print(f'Message from {message.author}: {message.content}')
    
#     if message.content.startswith('$hello'):
#         await message.channel.send('Hello!')


async def setup(bot):
    await bot.add_cog(music_cog(bot))

# async def main():
    
#     async with bot:
#         await setup(bot)
#         await bot.start("MTA2NTQ5MTA4MjM2NTkxNTI3Ng.G8hKzH.5L9yXNnBbJl6VEmn113ydNJOwZJciV2EC0APBA")


token = ""
with open("token.txt") as f:
    token = f.read() 

asyncio.run(setup(bot))

music = bot.get_cog('music_cog')
print(music)

bot.run(token)


# asyncio.run(main())

