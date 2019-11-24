import discord
from discord import Embed
from discord.ext import commands
from Util import logger
import database


class serveradministration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        @bot.command(name="addserver", aliases=["addbansync", "enablebansync", "removeserver", "togglebansync",
                                                "bansync", "addguild", "activesync", "toggleactivesync"])
        async def _addserver(ctx, arg1):
            """Enables/disables instant ban-sync on a guild"""
            if database.isModerator(ctx.author.id):
                if not database.isGuildInDB(arg1):
                    guild_id = int(arg1)
                    guild = bot.get_guild(guild_id)
                    name = None
                    ownerid = None
                    ownername = None
                    if guild is not None:
                        name = guild.name
                        ownerid = guild.owner.id
                        ownername = guild.owner.name
                    database.addBanSyncGuild(guild_id, name, ownerid, ownername)
                else:
                    database.toggleActiveSync(arg1)
                await ctx.send("Toggled ActiveSync for the guild with the ID: " + arg1)
            else:
                await ctx.send(
                    embed=Embed(color=discord.Color.red(), description="You are not a Global Moderator! Shame!"))

def setup(bot):
    bot.add_cog(serveradministration(bot))
