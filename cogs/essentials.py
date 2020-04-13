import discord
from discord import Embed
from discord.ext import commands

import database
from Util import logger
from database import isModerator


class essentials(commands.Cog, name="Essentials"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="loadcog", aliases=["loadextension"])
    async def _loadcog(self, ctx, arg1):
        """Loads a cog - GM only."""
        bot = self.bot
        if isModerator(ctx.author.id):
            try:
                bot.load_extension(f"cogs.{arg1}")
                await ctx.send(f"Successfully loaded the {arg1} extension")
                await logger.log("Moderator `%s` loaded the extension %s" % (ctx.author.name, arg1), bot, "INFO")
            except Exception as e:
                await ctx.send(f"Failed to load the extension {arg1}")
                await logger.log(f"Failed to load the extension {arg1} - {e}", bot, "ERROR")
        else:
            await ctx.send(
                embed=Embed(color=discord.Color.red(), description="You are not a Global Moderator! Shame!"))

    @commands.command(name="listcogs", aliases=["cogs"])
    async def _listcogs(self, ctx):
        """Lists all the cogs - GM only."""
        if isModerator(ctx.author.id):
            embed = discord.Embed(title="Cogs", color=discord.Color.green(),
                                  description="`essentials, info, moderation, listenerCog, botlists`")
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
        else:
            await ctx.send(
                embed=Embed(color=discord.Color.red(), description="You are not a Global Moderator! Shame!"))

    @commands.command(name="unloadcog", aliases=["unloadextension"])
    async def _unloadcog(self, ctx, arg1):
        """Unloads a cog - GM only."""
        bot = self.bot
        if isModerator(ctx.author.id):
            try:
                bot.unload_extension(f"cogs.{arg1}")
                await ctx.send(f"Successfully unloaded the {arg1} extension")
                await logger.log("Moderator `%s` unloaded the extension %s" % (ctx.author.name, arg1), bot, "INFO")
            except Exception as e:
                await ctx.send(f"Failed to unload the extension {arg1}")
                await logger.log(f"Failed to unload the extension {arg1} - {e}", bot, "ERROR")
        else:
            await ctx.send(
                embed=Embed(color=discord.Color.red(), description="You are not a Global Moderator! Shame!"))

    @commands.command(name="bannew", aliases=["newuserban", "enablenewuserbans", "bannewtoggle"])
    async def _bannew(self, ctx, *args):
        """Enables/disables the automatic global banning of accounts that are created less than 10 minutes ago.
        Disabled by default"""
        bot = self.bot
        if len(args) < 1:
            guild = ctx.guild
            guild_id = guild.id
        else:
            guild_id = int(args[0])
            guild = bot.get_guild(guild_id)

        if not database.isGuildInDB(guild_id):
            logger.logDebug("Guild is not in the database, adding it")
            name = None
            ownerid = None
            ownername = None
            if guild is not None:
                name = guild.name
                ownerid = guild.owner.id
                ownername = guild.owner.name
            database.addNewGuild(guild_id, name, ownerid, ownername)
        else:
            logger.logDebug("Guild is already in the database, doing toggle!")
            database.toggleNewAccountBan(guild_id)
        newAccountBanEnabled = database.isNewAccountBanGuild(guild_id)
        await ctx.send("Toggled bans for new accounts for the guild with the ID: " + str(guild_id) +
                       "\nBans for new accounts in this guild are now: " +
                       ("Enabled!" if newAccountBanEnabled else "Disabled!"))


def setup(bot):
    bot.add_cog(essentials(bot))
