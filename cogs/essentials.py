import discord
from discord import Embed
from discord.ext import commands
from Util import logging
import os

class essentials(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

        @bot.command(name="loadcog", aliases=["loadextension"])
        async def _loadcog(ctx, arg1):
            """Loads a cog"""
            mods = list(map(int, os.getenv("mods").split()))
            if ctx.author.id in mods:
                try:
                    bot.load_extension(f"cogs.{arg1}")
                    await ctx.send(f"Successfully loaded the {arg1} extension")
                    await logging.log("**[Info]** Moderator `%s` loaded the extension %s" % (ctx.author.name, arg1), bot)
                except Exception as e:
                    await ctx.send(f"Failed to load the extension {arg1}")
                    await logging.log(f"**[ERROR]** Failed to load the extension {arg1} - {e}", bot)
            else:
                await ctx.send(embed=Embed(color=discord.Color.red(), description="You are not a Global Moderator! Shame!"))

        @bot.command(name="listcogs", aliases=["cogs"])
        async def _listcogs(ctx):
            """Lists all the cogs"""
            mods = list(map(int, os.getenv("mods").split()))
            if ctx.author.id in mods:
                embed = discord.Embed(title="Cogs", color=discord.Color.green(),
                    description="`essentials, info, moderation, test`")
                embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
            else:
                await ctx.send(embed=Embed(color=discord.Color.red(), description="You are not a Global Moderator! Shame!"))

        @bot.command(name="unloadcog", aliases=["unloadextension"])
        async def _unloadcog(ctx, arg1):
            """Unloads a cog"""
            mods = list(map(int, os.getenv("mods").split()))
            if ctx.author.id in mods:
                try:
                    bot.unload_extension(f"cogs.{arg1}")
                    await ctx.send(f"Successfully unloaded the {arg1} extension")
                    await logging.log("**[Info]** Moderator `%s` unloaded the extension %s" % (ctx.author.name, arg1), bot)
                except Exception as e:
                    await ctx.send(f"Failed to unload the extension {arg1}")
                    await logging.log(f"**[ERROR]** Failed to unload the extension {arg1} - {e}", bot)
            else:
                await ctx.send(embed=Embed(color=discord.Color.red(), description="You are not a Global Moderator! Shame!"))

def setup(bot):
    bot.add_cog(essentials(bot))
