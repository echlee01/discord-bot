from ast import alias
import discord
from discord.ext import commands

from youtube_dl import YoutubeDL

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.isplaying = False
        self.ispaused = False
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.vc = None

    def search(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try: 
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]

            except Exception: 
                return False

        return {'source': info['formats'][0]['url'], 'title': info['title']}
    
    def play_next(self):
        if len(self.music_queue) > 0:
            self.isplaying = True
            url = self.music_queue[0][0]['source']

            self.music_queue.pop(0)
            self.vc.play(discord.FFmpegPCMAudio(url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.isplaying = False

    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.isplaying = True
            url = self.music_queue[0][0]['source']

            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()
                 
                if self.vc == None:
                    await ctx.send("Could not connect to the voice channel")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])

            self.music_queue.pop(0)
            
            self.vc.play(discord.FFmpegPCMAudio(url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())

        else:
            self.isplaying = False

    @commands.command(name="play",aliases=["p"], help="plays songs")
    async def play(self, ctx, *args):
        query = " ".join(args)

        vc = ctx.author.voice.channel
        if vc is None:
            await ctx.send("Connect to voice channel")
        else:
            song = self.search(query)
            if song is True:
                await ctx.send("Could not download")
            else:
                await ctx.send("Song added to the queue")
                self.music_queue.append([song, vc])
                
                if self.isplaying == False:
                    await self.play_music(ctx)
    
    @commands.command(name="queue", aliases=["q"], help="Displays the current songs in queue")
    async def queue(self, ctx):
        retval = ""
        for i in range(0, len(self.music_queue)):
            retval += self.music_queue[i][0]['title'] +"\n"
        print(retval)
        if retval != "":
            await ctx.send(retval)
        else:
            await ctx.send("no music")
    
    @commands.command(name="skip", aliases=["s"], help="Skips the current song being played")
    async def skip(self, ctx):
        if self.vc != "":
            self.vc.stop()
            await self.play_music(ctx)
    
    @commands.command(name="bruh",aliases=["b"], help="plays bruh")
    async def bruh(self, ctx, *args):
        query = 'https://www.youtube.com/watch?v=TApmI8YtYhc'

        vc = ctx.author.voice.channel
        if vc is None:
            await ctx.send("Connect to voice channel")
        else:
            song = self.search(query)
            if song is True:
                await ctx.send("Could not download")
            else:
                await ctx.send("Song added to the queue")
                self.music_queue.append([song, vc])
                
                if self.isplaying == False:
                    await self.play_music(ctx)

    @commands.command(name="omg", help="plays omg")
    async def bruh(self, ctx, *args):
        query = 'https://www.youtube.com/watch?v=Xn4yAbA9cZw'

        vc = ctx.author.voice.channel
        if vc is None:
            await ctx.send("Connect to voice channel")
        else:
            song = self.search(query)
            if song is True:
                await ctx.send("Could not download")
            else:
                await ctx.send("Song added to the queue")
                self.music_queue.append([song, vc])
                
                if self.isplaying == False:
                    await self.play_music(ctx)

    @commands.command(name="leave", aliases=["disconnect", "l", "d"], help="Kick the bot from VC")
    async def dc(self, ctx):
        self.isplaying = False
        self.ispaused = False
        await self.vc.disconnect()

    @commands.command(name="clear", aliases=["c", "bin"], help="Stops the music and clears the queue")
    async def clear(self, ctx):
        if self.vc != None and self.isplaying:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("Music queue cleared")
    
    @commands.command(name="list",aliases=["l"], help="list search")
    async def list(self, ctx, *args): 
        