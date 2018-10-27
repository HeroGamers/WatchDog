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
                embed = discord.Embed(title="Bot Information", color=discord.Color.green(),
                    description="")
                embed.add_field(name="Creation Date", value="%s" % discord.utils.snowflake_time(ctx.bot.user.id).strftime("%Y-%m-%d %H:%M:%S"), inline=True)
                embed.add_field(name="Guilds", value="%s" % len(bot.guilds), inline=True)
                ban_list = await ctx.guild.bans()
                embed.add_field(name="Global Bans", value="%s" % len(ban_list), inline=True)
                embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
            else:
                await ctx.send(embed=Embed(color=discord.Color.red(), description="You are not a Global Moderator! Shame!"))
def setup(bot):
    bot.add_cog(Info(bot))
