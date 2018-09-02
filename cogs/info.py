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

def setup(bot):
    bot.add_cog(Info(bot))
