import os
import database
from bot import bot
from Util import logger


async def ban(user, moderator=None, reason=None, guildid=None, channel=None):
    guilds = []

    if guildid is not None:
        try:
            guild = bot.get_guild(int(guildid))
            guilds.append(guild)
        except Exception as e:
            await logger.log("Could not fetch guild " + str(guildid), bot, "ERROR")

    for banSyncGuild in database.getBanSyncGuilds():
        try:
            guild = bot.get_guild(int(banSyncGuild.GuildID))
            guilds.append(guild)
        except Exception as e:
            await logger.log("Could not fetch guild " + str(banSyncGuild.GuildID), bot, "ERROR")
            continue

    for guild in guilds:
        # Check for testMode
        if os.getenv('testModeEnabled') != "True":
            # tries to ban
            try:
                await guild.ban(user, reason="WatchDog - Global Ban")
            except:
                await logger.log("Could not ban the user `%s` (%s) in the guild `%s` (%s)" % (
                    user.name, user.id, guild.name, guild.id), bot, "INFO")
        else:
            logger.logDebug("TestBanned (ban) " + user.name + " (" + str(
                user.id) + "), in the guild " + guild.name + "(" + str(guild.id) + ")", "DEBUG")
    if os.getenv('testModeEnabled') != "True":
        database.newBan(userid=user.id, discordtag=user.name + user.discriminator, moderator=moderator,
                        reason=reason, guild=guildid, avatarurl=user.avatar_url)


async def unban(user):
    for banSyncGuild in database.getBanSyncGuilds():
        try:
            guild = bot.get_guild(banSyncGuild.GuildID)
        except Exception as e:
            await logger.log("Could not fetch guild " + banSyncGuild.GuildID, bot, "ERROR")
            continue

        # Check for testMode
        if os.getenv('testModeEnabled') != "True":
            try:
                await guild.unban(user, reason="WatchDog - Global Unban")
            except:
                await logger.log("Could not unban the user `%s` (%s) in the guild `%s` (%s)" % (
                    user.name, user.id, guild.name, guild.id), bot, "INFO")
        else:
            logger.logDebug("TestUnBanned (unban) " + user.name + " (" + str(
                user.id) + "), in the guild " + guild.name + "(" + str(guild.id) + ")", "DEBUG")
    if os.getenv('testModeEnabled') != "True":
        database.invalidateBan(user.id)
