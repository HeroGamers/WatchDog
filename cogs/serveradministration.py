import discord
from discord import Embed
from discord.ext import commands
from Util import logger
import database


class serveradministration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        @bot.command(name="addserver", aliases=["addbansync", "enablebansync", "removeserver", "togglebansync", "bansync", "addguild", "activesync", "toggleactivesync"])
        async def _addserver(ctx, *args):
            """Enables/disables instant ban-sync on a guild"""
            if database.isModerator(ctx.author.id):
                logger.logDebug(str(len(args)))
                if len(args) < 1:
                    guild = ctx.guild
                    guild_id = guild.id
                else:
                    guild_id = int(args[0])
                    guild = bot.get_guild(guild_id)

                if not database.isGuildInDB(guild_id):
                    name = None
                    ownerid = None
                    ownername = None
                    if guild is not None:
                        name = guild.name
                        ownerid = guild.owner.id
                        ownername = guild.owner.name
                    database.addBanSyncGuild(guild_id, name, ownerid, ownername)
                else:
                    database.toggleActiveSync(guild_id)
                activeSyncEnabled = database.isBanSyncGuild(guild_id)
                await ctx.send("Toggled ActiveSync for the guild with the ID: " + str(guild_id) +
                               "\nActiveSync for the guild is now: " +
                               ("Enabled!" if activeSyncEnabled else "Disabled!"))
            else:
                await ctx.send(
                    embed=Embed(color=discord.Color.red(), description="You are not a Global Moderator! Shame!"))


def setup(bot):
    bot.add_cog(serveradministration(bot))
