import asyncio
import discord
from discord import Embed
from discord.ext import commands
import os

class Info:
    def __init__(self,bot):
        self.bot = bot

        @bot.command()
        async def support(ctx):
            """Get help and support regarding the bot."""
            await ctx.send("Join this server for support and other talks: https://discord.gg/eH8xS75")

        @bot.command()
        async def invite(ctx):
            """How to invite the bot."""
            await ctx.send("Invite me to your server with this link: https://discordapp.com/oauth2/authorize?scope=bot&client_id=475447317072183306&permissions=0x00000004")

        @bot.command()
        async def botinfo(ctx):
            """Retrives information about the bot - GM only"""
            mods = list(map(int, os.getenv("mods").split()))
            if ctx.author.id in mods:
                guild = []
                for guild in bot.guilds:
                    try:
                        await guild.ban(user, reason=f"WatchDog - Global Ban")
                    except:
                        channel = bot.get_channel(int(os.getenv('botlogfail')))
                        await channel.send("**[Info]** Could not ban the user `%s` (%s) in the guild `%s` (%s)" % (user.name, user.id, guild.name, guild.id))
                embed = discord.Embed(title="Bot Information", color=discord.Color.green(),
                    description="`%s` has been globally banned 👌" % user)
                embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                embed.set_image(url="https://cdn.discordapp.com/attachments/456229881064325131/475498849696219141/ban.gif")
                await ctx.send(embed=embed)
                channel = bot.get_channel(int(os.getenv('botlog')))
                await channel.send(embed=Embed(color=discord.Color.red(), description="Moderator `%s` banned `%s` - (%s)" % (ctx.author.name, user.name, user.id)))
            else:
                await ctx.send(embed=Embed(color=discord.Color.red(), description="You are not a Global Moderator! Shame!"))
def setup(bot):
    bot.add_cog(Info(bot))
