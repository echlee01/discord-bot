from ast import alias
import discord
from discord.ext import commands
import isodate
import google.auth
from googleapiclient.discovery import build
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

    async def music_template(self, ctx, query):
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

    @commands.command(name="play",aliases=["p"], help="Plays requested song `play <query>`")
    async def play(self, ctx, *args):
        query = " ".join(args)

        await self.music_template(ctx, query)
    
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
    
    @commands.command(name="bruh",aliases=["b"], help="Plays bruh")
    async def bruh(self, ctx):
        query = 'https://www.youtube.com/watch?v=TApmI8YtYhc'

        await self.music_template(ctx, query)

    @commands.command(name="omg",aliases=["o"], help="Plays omg")
    async def omg(self, ctx):
        query = 'https://www.youtube.com/watch?v=Xn4yAbA9cZw'

        await self.music_template(ctx, query)

    @commands.command(name="ninjasus", aliases=['ninja'], help="sussy ninja")
    async def ninjaSus(self, ctx):
        query = "UHcjhSjK0ws"

        await self.music_template(ctx, query)

    @commands.command(name="fnaf", aliases=['hor'], help="beatbox fnaf")
    async def fnaf(self, ctx):
        query = "https://www.youtube.com/watch?v=_CQ_ehoRfsE"
        
        await self.music_template(ctx, query)

    @commands.command(name="leave", aliases=["disconnect", "l", "dc"], help="Kick the bot from VC")
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
    
    @commands.command(name="search",aliases=["f"], help="list search `search <query>`")
    async def list(self, ctx, *args): 
        query = " ".join(args)

        vc = ctx.author.voice.channel
        if vc is None:
            await ctx.send("Connect to voice channel")
        else:
            # info = await self.search_list(query)
            info = await self.yt_search(query)
            options = []

            if type(info) == type(True):
                await ctx.send("Could not download song")
            
            for i in info:
                description = i['description']
                options.append(discord.SelectOption(label=i['title'], description=description))

            view=musicDropdownView(options=options)
            msg = await ctx.send("Pick a song", view=view)

            await view.wait()

            if view.index > (-1):
                await ctx.send(f"**{info[view.index]['title']}** added to the queue")
                await msg.delete()

                url = info[view.index]['source']
                song = self.search(url)
                self.music_queue.append([song, vc])

                if self.isplaying == False:
                    await self.play_music(ctx)

            else:
                await msg.delete()

    @commands.command(name="test", help="test button")
    async def test(self, ctx):
        view = testView()

        msg = await ctx.send("Hello, World!", view=view)

        await view.wait()
        await msg.delete()

    async def yt_search(self, query):
        api_key = ""
        with open("api_key.txt") as f:
            api_key = f.read() 
        youtube = build('youtube','v3',developerKey = api_key)
        request = youtube.search().list(q=query,part='id',type='video', maxResults=5) 
        response = request.execute()
        ids = []
        
        for id in response['items']:
            vidId = id['id']['videoId']
            ids.append(vidId) 

        id_str = ','.join(ids)
        
        req = youtube.videos().list(
                part="snippet,contentDetails",
                id=id_str
            )
        res = req.execute()
        vids = []
        index = 0

        for item in res['items']:
            duration = str(isodate.parse_duration(item['contentDetails']['duration']))
            title = str(index+1) + ". " + item['snippet']['title']
            vids += [{'source': item['id'], 'title': title, 'description': duration}]
            index += 1
        
        return vids

class testView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.container = 'full'

    @discord.ui.button(label='RELEASE')
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Down bad 💀')
        self.container = 'empty'
        self.stop()



    @discord.ui.button(label='ABSTAIN')
    async def abstain(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('GIGACHAD')
        self.container = 'full'
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
