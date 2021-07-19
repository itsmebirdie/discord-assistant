import discord, json, asyncio
from discord.ext import commands
from random import randint
from disrank.generator import Generator


class Leveling(commands.Cog):
    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
        with open("Configuration/Leveling.json") as f: self.CONFIG = json.load(f)

    def increment(self, message: discord.Message) -> None:
        randNo = randint(5, 15)
        if str(message.author.id) in self.CONFIG[str(message.author.guild.id)]["Levels"].keys():
            if self.CONFIG[str(message.author.guild.id)]["Levels"][str(message.author.id)][0] + randNo < 100:
                self.CONFIG[str(message.author.guild.id)]["Levels"][str(message.author.id)][0] += randNo
                self.CONFIG[str(message.author.guild.id)]["Levels"][str(message.author.id)][2] += randNo
                print('test1')
            elif self.CONFIG[str(message.author.guild.id)]["Levels"][str(message.author.id)][0] + randNo >= 100:
                print('test2')
                self.CONFIG[str(message.author.guild.id)]["Levels"][str(message.author.id)][0] = self.CONFIG[str(message.author.guild.id)]["Levels"][str(message.author.id)][0] + randNo - 100
                self.CONFIG[str(message.author.guild.id)]["Levels"][str(message.author.id)][1] += 1
                self.CONFIG[str(message.author.guild.id)]["Levels"][str(message.author.id)][2] += randNo
        else:
            self.CONFIG[str(message.author.guild.id)]["Levels"][message.author.id] = [randNo, 0, randNo]
        self.rewrite()
    
    def position(self, dct: dict, _obj: str) -> int:
        f = dct.copy()
        for index in range(len(list(f.items()))):
            f[index] = f[index][1]
        f.items().sort()
        print(f"{f} - POSITION FUNC")
        return 1
        
        
    def rewrite(self) -> None:
        with open("Configuration/Leveling.json", 'w') as f: json.dump(self.CONFIG, f, indent=4)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot: return
        if str(message.author.guild.id) in self.CONFIG.keys():
            if self.CONFIG[str(message.author.guild.id)]["Enabled"]:
                self.increment(message)
    
    @commands.command()
    async def toggleLeveling(self, ctx: commands.Context) -> None:
        if str(ctx.guild.id) in self.CONFIG.keys():
            self.CONFIG[str(ctx.guild.id)]["Enabled"] = True if not self.CONFIG[str(ctx.guild.id)]["Enabled"] else False
        else:
            self.CONFIG[str(ctx.guild.id)] = {"Enabled": True, "Levels":{}}
        self.rewrite()
        
        enabledordisabled = 'Enabled' if self.CONFIG[str(ctx.guild.id)]["Enabled"] else 'Disabled'
        await ctx.send(embed=discord.Embed(title="LEVELING", description=f"Leveling has been {enabledordisabled}", color=discord.Color.green() if self.CONFIG[str(ctx.guild.id)]["Enabled"] else discord.Color.red()))

    @commands.command()
    async def rank(self, ctx: commands.Context,*, user: commands.MemberConverter = None) -> None:
        print(user)
        if user is None: user = ctx.author
        if user.bot: return
        rank = self.position(self.CONFIG[str(ctx.author.guild.id)]["Levels"], str(ctx.author.id))
        args = {
            'profile_image': user.avatar_url,
            'level': int(self.CONFIG[str(user.guild.id)]["Levels"][str(user.id)][1]),
            'user_xp': int(self.CONFIG[str(user.guild.id)]["Levels"][str(user.id)][0]),
            'next_xp': 100,
            'user_position': rank,
            'user_name': str(user),
            'user_status': 'dnd'
        }
        print(args)
        image = Generator().generate_profile(**args)
        
        file = discord.File(fp=image, filename=f'image.png')
        await ctx.send(file=file)
        del args, image, file, rank


def setup(bot):
    bot.add_cog(Leveling(bot))