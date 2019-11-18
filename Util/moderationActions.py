import os
import database
from bot import bot
from Util import logger


async def ban(user, moderator=None, reason=None, guildid=None):
    for guild in bot.guilds:
        # Check for testMode
        if os.getenv('testModeEnabled') != "True":
            # tries to ban
            try:
                await guild.ban(user, reason=f"WatchDog - Global Ban")
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
    for guild in bot.guilds:
        # Check for testMode
        if os.getenv('testModeEnabled') != "True":
            try:
                await guild.unban(user, reason=f"WatchDog - Global Unban")
            except:
                await logger.log("Could not unban the user `%s` (%s) in the guild `%s` (%s)" % (
                    user.name, user.id, guild.name, guild.id), bot, "INFO")
        else:
            logger.logDebug("TestUnBanned (unban) " + user.name + " (" + str(
                user.id) + "), in the guild " + guild.name + "(" + str(guild.id) + ")", "DEBUG")
    if os.getenv('testModeEnabled') != "True":
        database.invalidateBan(user.id)
