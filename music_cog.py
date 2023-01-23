from ast import alias
import discord
from discord.ext import commands
import datetime
import json

from youtube_dl import YoutubeDL

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.isplaying = False
        self.ispaused = False
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.YDL_SEARCH_OPTIONS = {'format': 'bestaudio', 'simulate': 'True', 'skip_download': 'True'}
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
                await ctx.send(f"**{song['title']}** added to the queue")
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

    @commands.command(name="omg",alias=["o"], help="plays omg")
    async def omg(self, ctx, *args):
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

    # gives list from searches
    async def search_list(self, item):
        
        with YoutubeDL(self.YDL_SEARCH_OPTIONS) as ydl:
            try: 
                info = ydl.extract_info("ytsearch5:%s" % item, download=False)['entries']
                options = []
                index = 0
                
                for i in info:
                    title = str(index+1) + ". " + i['title']
                    description = i['duration']
                    option = {'title': title, 'description': description}
                    url = i['formats'][0]['url']
                    options += [{'source': url, 'option': option}]
                    index += 1

            except Exception: 
                return False

        return options
    
    
    
    @commands.command(name="search",aliases=["f"], help="list search")
    async def list(self, ctx, *args): 
        query = " ".join(args)

        vc = ctx.author.voice.channel
        if vc is None:
            await ctx.send("Connect to voice channel")
        else:
            info = await self.search_list(query)
            options = []

            if type(info) == type(True):
                await ctx.send("Could not download song")
            
            for i in info:
                duration = str(datetime.timedelta(seconds=i['option']['description']))
                options.append(discord.SelectOption(label=i['option']['title'], description=duration))

            view=musicDropdownView(options=options)
            msg = await ctx.send("Pick a song", view=view)

            await view.wait()

            if view.index > (-1):
                await ctx.send(f"**{info[view.index]['option']['title']}** added to the queue")

                self.music_queue.append([info[view.index], vc])
                await msg.delete()

                if self.isplaying == False:
                    
                    await self.play_music(ctx)
            else:
                await msg.delete()

    @commands.command(name="cum")
    async def test(self, ctx):
        view = cumView()

        msg = await ctx.send("Hello, World!", view=view)

        await view.wait()

        if view.balls == 'empty':
            print('Down bad 💀')
        elif view.balls == 'full':
            print('GIGACHAD')
        else:
            print('HUH')

class cumView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.balls = 'full'

    @discord.ui.button(label='CUM')
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Down bad 💀')
        self.balls = 'empty'
        self.stop()



    @discord.ui.button(label='ABSTAIN')
    async def abstain(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('GIGACHAD')
        self.balls = 'full'
        self.stop()



class musicDropdown(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder='Pick an audio file', min_values=1, max_values=1, options=options)
        
    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: musicDropdownView = self.view

        view.index = int(interaction.data['values'][0][:1]) - 1
        view.stop()

class buttonCancel(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Cancel", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: musicDropdownView = self.view

        view.stop()

class musicDropdownView(discord.ui.View):
    def __init__(self, options):
        self.index = -1
        super().__init__()

        self.add_item(musicDropdown(options))
        self.add_item(buttonCancel())
