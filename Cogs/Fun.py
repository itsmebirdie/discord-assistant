import discord, requests
from discord.ext import commands
from random import choice


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        
        self.EIGHT_BALL_ANSWERS = [
            "Yeah", "Yes", "Ofcourse", "Ofc", "Ah Yes", "I see in the Prophecy: TRUE!"
            "Nah", "No", 'Nope', 'Never', "I don't think so",
            "idk", "Maybe", "ig", "I'm bored", "You're annoying"
        ]
          
    ## ==> COIN FLIP
    #############################################################################################
    
    @commands.command()
    async def coin(self, ctx: commands.Context) -> None:
        await ctx.send(embed=discord.Embed(title="COIN FLIP", description=f"Coin has been Tossed: {choice(['Heads', 'Tails'])}", color=discord.Color.green()))

    #############################################################################################
    
    ## ==> press f to pay respect
    #############################################################################################
    
    @commands.command()
    async def f(self, ctx: commands.Context, *, reason: str = None) -> None:
        await ctx.send(f"{ctx.author.name} has pressed f to pay respect for reason: {reason}" if reason is not None else f"{ctx.author.name} has pressed f to pay respect")
    
    #############################################################################################
    
    ## ==> 8BALL
    #############################################################################################

    @commands.command(aliases=['8ball'])
    async def eightBall(self, ctx: commands.Context, *, question) -> None:
        embed = discord.Embed(color=ctx.author.color, title="8BALL", description=f"Question - {question}?\nAnswer - {choice(self.EIGHT_BALL_ANSWERS)}")
        embed.set_author(name=str(ctx.author)[:-5], icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    #############################################################################################

    ## ==> MEMES
    #############################################################################################

    @commands.command()
    async def meme(self,ctx: commands.Context) -> None:
        r = requests.get("https://memes.blademaker.tv/api?lang=en")
        res = r.json()
        embed_ = discord.Embed(title=res['title'],color=discord.Color.blue())
        embed_.set_image(url = res["image"])
        embed_.set_author(name = ctx.author,icon_url = ctx.author.avatar_url)
        await ctx.send(embed = embed_)

    @commands.command()
    async def memes(self, ctx: commands.Context, number: int = 3) -> None:
        if number <= 3:
            for i in range(number):
                r = requests.get("https://memes.blademaker.tv/api?lang=en")
                res = r.json()
                embed_ = discord.Embed(title=res['title'], color=discord.Color.blue())
                embed_.set_image(url = res["image"])
                embed_.set_author(name = ctx.author,icon_url = ctx.author.avatar_url)
                await ctx.send(embed = embed_)

    #############################################################################################

def setup(bot:commands.Bot):
    bot.add_cog(Fun(bot))