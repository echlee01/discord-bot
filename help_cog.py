import discord
from discord.ext import commands

class help_cog(commands.Cog):
    def __init__(self, bot, prefix):
        self.bot = bot
        self.prefix = prefix
        self.help_message = """"""

    @commands.command(name="commands",aliases=["cmd"], help="Shows all commands")
    async def get_help(self, ctx):
        cmds = self.bot.walk_commands()

        if not self.help_message:
            for cmd in cmds:
                aliases = ", ".join(cmd.aliases)
                self.help_message += f'{cmd.name}, {aliases} - {cmd.help}\n'

        embed=discord.Embed(title=f"Commands prefix with ```{self.prefix}```", description=self.help_message, color=0x00ff00)
        await ctx.send(embed=embed)
        