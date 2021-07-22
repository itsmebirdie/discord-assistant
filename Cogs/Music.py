import discord
from discord.ext import commands

from youtube_dl import YoutubeDL


class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # All the music related stuff
        # To check if the music is playing or not
        self.is_playing = False

        # Song currently playing right now
        self.playing = ""
        self.count1 = 0
        
        # 2d array containing [song, channel]
        # keeps track of any music that is in queue
        self.music_queue = []

        # Music options
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        # Current Voice Channel
        self.vc = ""

        # Global embeds
        self.embed_notplaying = discord.Embed(title="Music not playing",color=0x1ee0eb)
        self.embed_pause = discord.Embed(title="Music Paused",color=0x1ee0eb)
        self.embed_paused = discord.Embed(title="Music already paused",color=0x1ee0eb)
        self.embed_ispaused = discord.Embed(title="Music is paused, resume first")
        self.embed_resume = discord.Embed(title="Music Resumed",color=0x1ee0eb)
        self.embed_isresumed = discord.Embed(title="Music not paused")
        self.embed_disconnect= discord.Embed(title="Music Disconnected",color=0x1ee0eb)

    # Search Youtube 
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
                print("\n")
            except Exception:
                return False

            return {'source': info['formats'][0]['url'], 'title': info['title']}

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            # Get the first url
            music_url = self.music_queue[0][0]['source']
            self.playing =  self.music_queue[0][0]['title']

            # Start playing using the FFmpegPCMAudio with the given url and the options from above the dictionary
            # And when you are done playing that music, we want to go back into this play_next and check if there 
            # is something in the queue and if there is, repeat the whole process, if there isn't it can exit.
            try:
                self.vc.play(discord.FFmpegPCMAudio(music_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
                self.music_queue.pop(0)
            except discord.errors.ClientException as e:
                # Works even tho exception shows up
                if str(e) == "Already playing audio.":
                    print(e)
                    print("Exception handled\n")
                else:
                    print(e)       

        else:
            self.is_playing = False

    # Infinite loop checking
    async def play_music(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            music_url = self.music_queue[0][0]['source']
            
            # Try to connect to voice channel if you are not already connected
            if self.vc == "" or not self.vc.is_connected() or self.vc == None:
                self.vc = await self.music_queue[0][1].connect()
            else:
                await self.vc.move_to(self.music_queue[0][1])
            
            try:
                self.vc.play(discord.FFmpegPCMAudio(music_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())

            except discord.errors.ClientException as e:
                if str(e) == "Already playing audio.":
                    print(e)
                    if self.is_playing == True:
                        pass
                    else:
                        self.vc.play(discord.FFmpegPCMAudio(music_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())

                    print("Exception handled")
                else:
                    print(e)

            # To remove the first played song from the queue
            if self.count1 != 1:
                self.playing =  self.music_queue[0][0]['title']
                if str(self.music_queue[0][0]['title']) == str(self.playing):
                    self.music_queue.pop(0)
                    self.count1 = 1

        else:
            self.is_playing = False
    
    # Play - Adds to queue or Plays music
    @commands.command(aliases=["p"])
    async def play(self, ctx, *args):
        for word in args:
            if word.startswith("'") or word.startswith('"'):
                await ctx.reply("Invalid arguments")
                return False

        query = " ".join(args)

        if ctx.author.voice == None:
            await ctx.reply("Connect to a voice channel!")
        
        elif self.vc != "" and self.vc.is_paused():
            await ctx.reply(embed=self.embed_ispaused)
            pass

        else:
            voice_channel = ctx.author.voice.channel
            # search for the music with the query keyword in youtube
            song = self.search_yt(query)

            # To check if it is something other than a vid
            if type(song) == type(True):
                await ctx.reply("Incorrect format try another keyword.")
            
            else:
                songTitle=song['title']
                emb1=discord.Embed(title='Added a Song',description=f'Successfully added \n**{songTitle}** to the queue.',color=0x1ee0eb)
                await ctx.reply(embed=emb1)
                # appending the song and voice_channel to music_queue
                self.music_queue.append([song, voice_channel])

                # If not currently playing, start playing 
                if self.is_playing == False:
                    await self.play_music()
    
    # Queue - show the music queue
    @commands.command(aliases=["q"])
    async def queue(self, ctx):
        queue = []
        # go through a music_queue and add it to queue
        for i in range(0, len(self.music_queue)):
            queue.append(f"{i+1}. " + self.music_queue[i][0]['title'] + "\n")

        embed_queue = discord.Embed(title="Music Queue", description="\n".join([str(song) for song in queue]), color=discord.Colour.red())

        embed_queue.set_thumbnail(url=ctx.author.avatar_url)
        embed_queue.set_footer(icon_url=ctx.author.avatar_url)

        # If queue is not empty, send
        if queue != []:
            await ctx.reply(embed=embed_queue)

        # send there is no music in queue
        else:
            await ctx.reply("No music in queue")

    # Check
    async def check(self, ctx):
        if self.vc != "" or self.vc != None and self.vc:
            if ctx.author.voice == None:
                await ctx.reply("Connect to a voice channel!")
            elif ctx.author.voice.channel.id != self.vc.channel.id:
                await ctx.reply("Connect to the same voice channel as the bot!")
            else:
                return True
        else:
            await ctx.reply(embed=self.embed_notplaying)

    # Skip - Plays the next song in the queue
    @commands.command(aliases=["s"])
    async def skip(self, ctx):
        if await self.check(ctx) == True:
            # Stop playing the current music
            self.vc.stop()

            if self.music_queue == []:
                await ctx.reply("There is no music in Queue.\nPlease add more music to the Queue.")
            else:
                embed_skip = discord.Embed(color=discord.Colour.red())
                embed_skip.add_field(name="Skipped", value=self.playing)
                embed_skip.add_field(name="Now Playing", value=self.music_queue[0][0]['title'])
                await ctx.reply(embed=embed_skip)
                
                await self.play_music()

    # Pause
    @commands.command(aliases=['pa'])
    async def pause(self, ctx):
        if await self.check(ctx) == True:
            if self.vc.is_playing():
                self.vc.pause()
                await ctx.reply(embed=self.embed_pause)
            else:
                await ctx.reply(embed=self.embed_paused)

    # Resume
    @commands.command(aliases=["re"])
    async def resume(self, ctx):
        if await self.check(ctx) == True:
            if self.vc.is_paused():
                self.vc.resume()
                await ctx.reply(embed=self.embed_resume)
            else:
                await ctx.reply(embed=self.embed_isresumed)

    # Disconnect
    @commands.command(aliases=["stop", "dc"])
    async def disconnect(self, ctx):
        if await self.check(ctx) == True:
            await self.vc.disconnect()
            self.vc = ""
            self.is_playing = False

            self.playing = ""
            self.count1 = 0
        
            self.music_queue = []
            
            await ctx.reply(embed=self.embed_disconnect)

def setup(bot):
    bot.add_cog(music_cog(bot))