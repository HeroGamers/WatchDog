import asyncio
import discord
from discord import Embed
from discord.ext import commands
from Util import logger
from database import isModerator
import database
import os


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Helping Functions #

        # Function to have the moderator confirm their action, on stuff like revsync
        async def confirmAction(ctx, action):
            await ctx.send("Are you sure you want to do a revsync, and sync all the bans from this guild too all other "
                           "guilds? Confirm with a `Revsync the " + ctx.guild.name + "guild`...\nSleeping for 30 "
                                                                                     "seconds!")
            await asyncio.sleep(30)
            history = await ctx.channel.history(limit=100).flatten()
            for message in history:
                if (message.author.id == ctx.author.id) & (
                        message.content == ("Revsync the " + ctx.guild.name + " guild")):
                    return True
            return False

        # Function to send message about the ban
        async def logBan(ctx, user, unban=False, reason=None):
            # Sends a message in the botlog
            if unban:
                color = discord.Color.green()
                text = "unbanned"
            else:
                color = discord.Color.red()
                text = "banned"
            await logger.logEmbed(color,
                                  "Moderator `%s` %s `%s` - (%s)" % (ctx.author.name, text, user.name, user.id),
                                  bot)
            # Send private ban notif in private moderator ban list
            prvchannel = bot.get_channel(int(os.getenv('prvbanlist')))
            prvembed = discord.Embed(title="Account " + text, color=color,
                                     description="`%s` has been globally %s" % (user.id, text))
            prvembed.add_field(name="Moderator", value="%s (`%s`)" % (ctx.author.name + "#" + ctx.author.discriminator, ctx.author.id),
                               inline=True)
            prvembed.add_field(name="Name when " + text, value="%s" % user, inline=True)
            prvembed.add_field(name="In server", value="%s (`%s`)" % (ctx.guild.name, ctx.guild.id),
                               inline=True)
            prvembed.add_field(name="In channel", value="%s (`%s`)" % (ctx.channel.name, ctx.channel.id),
                               inline=True)
            if reason is not None:
                prvembed.add_field(name="Reason", value="%s" % reason,
                                   inline=True)
            prvembed.set_footer(text="%s has been globally %s" % (user, text),
                                icon_url="https://cdn.discordapp.com/attachments/456229881064325131/489102109363666954/366902409508814848.png")
            prvembed.set_thumbnail(url=user.avatar_url)
            await prvchannel.send(embed=prvembed)
            # Update the database
            if unban:
                database.invalidateBan(user.id)
            else:
                database.newBan(userid=user.id, discordtag=user.name + user.discriminator, moderator=ctx.author.id,
                                reason=reason, guild=ctx.guild.id, avatarurl=user.avatar_url)

        # Function used to try and get users from arguments
        async def getUser(ctx, arg):
            if arg.startswith("<@") and arg.endswith(">"):
                userid = arg.replace("<@", "").replace(">", "").replace("!", "")  # fuck you nicknames
            else:
                userid = arg

            try:
                user = await ctx.bot.fetch_user(userid)
            except Exception as e:
                logger.logDebug("User not found! ID method - %s" % e)
                try:
                    user = discord.utils.get(ctx.message.guild.members, name=arg)
                except Exception as e:
                    logger.logDebug("User not found! Name method - %s" % e)
            if user is not None:
                logger.logDebug("User found! - %s" % user.name)
                return user
            else:
                raise Exception("User not found!")

        # Funtion to try and get a reason from multiple arguments
        async def sortArgs(ctx, args):
            userlist = []
            reasonlist = []
            logger.logDebug("Userlist: " + str(userlist))
            logger.logDebug("Reason: " + str(reasonlist))

            i = 0
            user_max = 0
            for arg in args:
                try:
                    founduser = await getUser(ctx, arg)
                    logger.logDebug("User found: " + str(founduser))
                    userlist.append(founduser)

                    user_max = i
                except Exception:
                    print("no user lol")
                i += 1
            logger.logDebug("Usermax: " + str(user_max))

            i = 0
            for arg in args:
                if i > user_max:
                    reasonlist.append(arg)
                i += 1

            logger.logDebug("Userlist 2: " + str(userlist))
            logger.logDebug("Reason 2: " + str(reasonlist))

            users = tuple(userlist)
            reason = ' '.join(reasonlist)
            return users, reason

        # Commands #

        @bot.command(name="sync")
        @commands.guild_only()
        @commands.bot_has_permissions(ban_members=True)
        @commands.has_permissions(ban_members=True)
        async def _sync(ctx):
            """Sync the bans."""
            if not database.isBanSyncGuild(ctx.guild.id):
                await ctx.send("Sorry, but this command is restricted to some guilds, and we doubt that you will need "
                               "it! If you do feel like you need to sync all the bans, then please do reach out to a "
                               "Global Moderator on the Support Guild (`" + str(os.getenv('prefix')) + "support`)!")
                return
            if os.getenv('testModeEnabled') == "True":
                await logger.log(
                    "TestMode seems enabled.. ignores ban functions. Check the console/script logs for the full debugging logs!",
                    bot, "DEBUG")
            banguild = bot.get_guild(int(os.getenv('banlistguild')))
            ban_list = await banguild.bans()
            currentguild_ban_list = await ctx.guild.bans()
            banCount = 0
            banCountAll = len(ban_list)
            percent1 = round((round((banCountAll / 5 * 1), 0) / (banCountAll) * 100), 1)
            percent2 = round((round((banCountAll / 5 * 2), 0) / (banCountAll) * 100), 1)
            percent3 = round((round((banCountAll / 5 * 3), 0) / (banCountAll) * 100), 1)
            percent4 = round((round((banCountAll / 5 * 4), 0) / (banCountAll) * 100), 1)
            logger.logDebug(
                "PercentageChecks: " + str(percent1) + ", " + str(percent2) + ", " + str(percent3) + ", " + str(
                    percent4))
            messagepercentage = 0
            embed = discord.Embed(title="Sync in progress...", color=discord.Color.green(),
                                  description="0% complete! 👌")
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            # Causes lag in embed - embed.set_image(url="https://cdn.discordapp.com/attachments/456229881064325131/485934104156569600/happysuccess.gif")
            embed_message = await ctx.send(embed=embed)
            for BanEntry in ban_list:
                banned = False

                for BanEntry2 in currentguild_ban_list:  # Checks if the account already is banned on the guild
                    if BanEntry2.user.id == BanEntry.user.id:
                        banCount += 1
                        logger.logDebug(str(banCount) + "/" + str(
                            banCountAll) + " User already banned, skipping - " + BanEntry.user.name, "DEBUG")
                        ban_list_list = list(ban_list)
                        ban_list_list.remove(BanEntry)
                        ban_list = tuple(ban_list_list)
                        # Does the embed change
                        percentRaw = (banCount / banCountAll) * 100
                        percent = round(percentRaw, 1)
                        logger.logDebug("Percent: " + str(percent), "DEBUG")
                        if ((percent == percent1) or (percent == percent2) or (percent == percent3) or (
                                percent == percent4)) and (percent != messagepercentage):
                            logger.logDebug("Embed update triggered, percent: " + str(percent), "DEBUG")
                            messagepercentage = percent
                            embed = discord.Embed(title="Sync in progress...", color=discord.Color.green(),
                                                  description="%s%% complete! 👌" % percent)
                            embed.set_footer(text="%s - Global WatchDog Moderator" % ctx.author.name,
                                             icon_url=ctx.author.avatar_url)
                            await embed_message.edit(embed=embed)
                        banned = True
                        break

                if banned == True:
                    continue
                # Check for testMode
                if os.getenv('testModeEnabled') != "True":
                    try:
                        await ctx.guild.ban(BanEntry.user, reason="WatchDog - Global Ban")
                    except:
                        await logger.log("Could not syncban the user `%s` (%s) in the guild `%s` (%s)" % (
                            BanEntry.user.name, BanEntry.user.id, ctx.guild.name, ctx.guild.id), bot, "INFO")
                else:
                    logger.logDebug("TestBanned (sync) " + BanEntry.user.name + " (" + str(
                        BanEntry.user.id) + "), in the guild " + ctx.guild.name + "(" + str(ctx.guild.id) + ")",
                                    "DEBUG")
                banCount += 1
                percentRaw = (banCount / banCountAll) * 100
                percent = round(percentRaw, 1)
                logger.logDebug("Percent: " + str(percent), "DEBUG")
                if ((percent == percent1) or (percent == percent2) or (percent == percent3) or (
                        percent == percent4)) and (percent != messagepercentage):
                    messagepercentage = percent
                    logger.logDebug("Embed update triggered, percent: " + str(percent), "DEBUG")
                    embed = discord.Embed(title="Sync in progress...", color=discord.Color.green(),
                                          description="%s%% complete! 👌" % percent)
                    embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                    # Causes lag in embed - embed.set_image(url="https://cdn.discordapp.com/attachments/456229881064325131/485934104156569600/happysuccess.gif")
                    await embed_message.edit(embed=embed)
            embed = discord.Embed(title="Sync complete", color=discord.Color.green(),
                                  description="Synchronisation complete! 👌")
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.set_image(
                url="https://cdn.discordapp.com/attachments/456229881064325131/485934104156569600/happysuccess.gif")
            await embed_message.edit(embed=embed)

        @bot.command(name="revsync", aliases=["reversesync"])
        @commands.guild_only()
        @commands.bot_has_permissions(ban_members=True)
        async def _revsync(ctx):
            """Sync bans from server to central, and other guilds."""
            ban_list = await ctx.guild.bans()
            banguild = bot.get_guild(int(os.getenv('banlistguild')))
            banguild_ban_list = await banguild.bans()
            if isModerator(ctx.author.id):
                if not await confirmAction(ctx, "revsync"):
                    return
                if os.getenv('testModeEnabled') == "True":
                    await logger.log(
                        "TestMode seems enabled.. ignores ban functions. Check the console/script logs for the full debugging logs!",
                        bot, "DEBUG")
                banCount = 0
                banCountAll = len(ban_list)
                if banCountAll == 0:
                    await ctx.send("Sorry, but the guild doesn't have any bans!")
                    return
                percent1 = round((round((banCountAll / 5 * 1), 0) / (banCountAll) * 100), 1)
                percent2 = round((round((banCountAll / 5 * 2), 0) / (banCountAll) * 100), 1)
                percent3 = round((round((banCountAll / 5 * 3), 0) / (banCountAll) * 100), 1)
                percent4 = round((round((banCountAll / 5 * 4), 0) / (banCountAll) * 100), 1)
                logger.logDebug(
                    "PercentageChecks: " + str(percent1) + ", " + str(percent2) + ", " + str(percent3) + ", " + str(
                        percent4))
                messagepercentage = 0
                embed = discord.Embed(title="Revsync in progress...", color=discord.Color.green(),
                                      description="0% complete! 👌")
                embed.set_footer(text="%s - Global WatchDog Moderator" % ctx.author.name,
                                 icon_url=ctx.author.avatar_url)
                # Causes lag in embed - embed.set_image(url="https://cdn.discordapp.com/attachments/485619099481800714/485917795679338496/1521567278_980x.gif")
                embed_message = await ctx.send(embed=embed)

                for BanEntry in ban_list:
                    banned = False

                    if database.isBanned(BanEntry.user.id):
                        banCount += 1
                        logger.logDebug(str(banCount) + "/" + str(
                            banCountAll) + " User already banned, skipping - " + BanEntry.user.name, "DEBUG")
                        ban_list_list = list(ban_list)
                        ban_list_list.remove(BanEntry)
                        ban_list = tuple(ban_list_list)
                        # Does the embed change
                        percentRaw = (banCount / banCountAll) * 100
                        percent = round(percentRaw, 1)
                        logger.logDebug("Percent: " + str(percent), "DEBUG")
                        if ((percent == percent1) or (percent == percent2) or (percent == percent3) or (
                                percent == percent4)) and (percent != messagepercentage):
                            messagepercentage = percent
                            logger.logDebug("Embed update triggered, percent: " + str(percent), "DEBUG")
                            embed = discord.Embed(title="Revsync in progress...", color=discord.Color.green(),
                                                  description="%s%% complete! 👌" % percent)
                            embed.set_footer(text="%s - Global WatchDog Moderator" % ctx.author.name,
                                             icon_url=ctx.author.avatar_url)
                            await embed_message.edit(embed=embed)
                        banned = True
                        break
                    if banned:
                        continue
                    elif BanEntry.user == ctx.bot.user:
                        await logger.log(
                            "Someone tried to ban the bot during a revsync. Moderator: `%s` (%s) in the guild `%s` (%s)" % (
                                ctx.author.name, ctx.author.id, ctx.guild.name, ctx.guild.id), bot, "WARNING")

                        ban_list_list = list(ban_list)
                        ban_list_list.remove(BanEntry)
                        ban_list = tuple(ban_list_list)
                        continue
                    elif isModerator(BanEntry.user.id):
                        await logger.log(
                            "Someone tried to ban a Global Moderator during a revsync. Moderator: `%s` (%s) in the guild `%s` (%s)" % (
                                ctx.author.name, ctx.author.id, ctx.guild.name, ctx.guild.id), bot, "WARNING")

                        ban_list_list = list(ban_list)
                        ban_list_list.remove(BanEntry)
                        ban_list = tuple(ban_list_list)
                        continue
                    else:
                        banCount += 1
                        logger.logDebug(str(banCount) + "/" + str(
                            banCountAll) + " User not banned, banning - " + BanEntry.user.name, "DEBUG")
                        # checks other guilds
                        for banSyncGuild in database.getBanSyncGuilds():
                            guild = bot.get_guild(int(banSyncGuild.GuildID))
                            if guild is None:  # Check if guild is none
                                await logger.log("Guild is none... GuildID: " + banSyncGuild.GuildID, bot, "ERROR")
                                continue
                            # checks if own guild, if it is, skip
                            if guild != ctx.guild:
                                # Check for testMode
                                if os.getenv('testModeEnabled') != "True":
                                    # tries to ban
                                    try:
                                        await guild.ban(BanEntry.user, reason="WatchDog - Global Ban")
                                    except:
                                        await logger.log(
                                            "Could not revsyncban the user `%s` (%s) in the guild `%s` (%s)" % (
                                                BanEntry.user.name, BanEntry.user.id, guild.name, guild.id), bot,
                                            "INFO")
                                else:
                                    logger.logDebug("TestBanned (revsync) " + BanEntry.user.name + " (" + str(
                                        BanEntry.user.id) + "), in the guild " + guild.name + "(" + str(guild.id) + ")",
                                                    "DEBUG")
                        # Does the embed change
                        percentRaw = (banCount / banCountAll) * 100
                        percent = round(percentRaw, 1)
                        logger.logDebug("Percent: " + str(percent), "DEBUG")
                        if ((percent == percent1) or (percent == percent2) or (percent == percent3) or (
                                percent == percent4)) and (percent != messagepercentage):
                            messagepercentage = percent
                            logger.logDebug("Embed update triggered, percent: " + str(percent), "DEBUG")
                            embed = discord.Embed(title="Revsync in progress...", color=discord.Color.green(),
                                                  description="%s%% complete! 👌" % percent)
                            embed.set_footer(text="%s - Global WatchDog Moderator" % ctx.author.name,
                                             icon_url=ctx.author.avatar_url)
                            await embed_message.edit(embed=embed)
                        # Do this when done
                        # Check for testMode
                        if os.getenv('testModeEnabled') != "True":
                            # Send private ban notif in private moderator ban list as well as message in botlog
                            await logBan(ctx, BanEntry.user)
                        else:
                            logger.logDebug(
                                "TestSent (unban) embeds and prvlist notif for " + BanEntry.user.name + " (" + str(
                                    BanEntry.user.id) + ")", "DEBUG")
                # send final embed, telling the ban was sucessful
                if len(ban_list) == 1:
                    desc_string = "Reverse synchronisation complete! %s account has been globally banned 👌" % len(
                        ban_list)
                else:
                    desc_string = "Reverse synchronisation complete! %s accounts have been globally banned 👌" % len(
                        ban_list)

                embed = discord.Embed(title="Revsync complete", color=discord.Color.green(),
                                      description=desc_string)
                embed.set_footer(text="%s - Global WatchDog Moderator" % ctx.author.name,
                                 icon_url=ctx.author.avatar_url)
                embed.set_image(
                    url="https://cdn.discordapp.com/attachments/485619099481800714/485917795679338496/1521567278_980x.gif")
                await embed_message.edit(embed=embed)
            else:
                await ctx.send(
                    embed=Embed(color=discord.Color.red(), description="You are not a Global Moderator! Shame!"))

        @bot.command(name="ban")
        async def _ban(ctx, arg1, *args, reason="WatchDog - Global Ban"):
            """Bans a user globally."""
            if isModerator(ctx.author.id):
                if os.getenv('testModeEnabled') == "True":
                    await logger.log(
                        "TestMode seems enabled.. ignores ban functions. Check the console/script logs for the full debugging logs!",
                        bot, "DEBUG")
                banguild = bot.get_guild(int(os.getenv('banlistguild')))
                banguild_ban_list = await banguild.bans()
                try:
                    user = await getUser(ctx, arg1)
                except Exception as e:
                    await ctx.send(embed=Embed(color=discord.Color.red(), description="Specified user not found!"))
                    await logger.log("Could not get a specified user - Specified arg: %s - Error: %s" % (arg1, e), bot,
                                     "ERROR")
                    return
                if user == ctx.bot.user:
                    await ctx.send(
                        embed=Embed(color=discord.Color.red(), description="What are you trying to do? Shame!"))
                elif isModerator(user.id):
                    await ctx.send(
                        embed=Embed(color=discord.Color.red(), description="You cannot ban a Global Moderator, sorry!"))
                else:
                    if database.isBanned(user.id):
                        await ctx.send(
                            embed=Embed(color=discord.Color.red(), description="That user has already been banned!"))
                    else:
                        # Bans on current used guild first
                        # Check for testMode
                        if os.getenv('testModeEnabled') != "True":
                            # Priorize banning all accounts on own guild
                            # tries to ban
                            try:
                                await ctx.guild.ban(user, reason="WatchDog - Global Ban")
                            except:
                                await logger.log("Could not ban the user `%s` (%s) in the guild `%s` (%s)" % (
                                    user.name, user.id, ctx.guild.name, ctx.guild.id), bot, "INFO")
                        else:
                            logger.logDebug("TestBanned (ban) " + user.name + " (" + str(
                                user.id) + "), in the guild " + ctx.guild.name + "(" + str(ctx.guild.id) + ")",
                                            "DEBUG")

                        # Sends main embed
                        guildCount = 0
                        guilds = database.getBanSyncGuilds()
                        if len(guilds) >= 1:
                            guildCountAll = len(guilds)
                            percent1 = round((round((guildCountAll / 5 * 1), 0) / (guildCountAll) * 100), 1)
                            percent2 = round((round((guildCountAll / 5 * 2), 0) / (guildCountAll) * 100), 1)
                            percent3 = round((round((guildCountAll / 5 * 3), 0) / (guildCountAll) * 100), 1)
                            percent4 = round((round((guildCountAll / 5 * 4), 0) / (guildCountAll) * 100), 1)
                            logger.logDebug("PercentageChecks: " + str(percent1) + ", " + str(percent2) + ", " + str(
                                percent3) + ", " + str(percent4))
                            messagepercentage = 0
                            embed = discord.Embed(title="Account is being banned...", color=discord.Color.green(),
                                                  description="0% complete! 👌")
                            embed.set_footer(text="%s - Global WatchDog Moderator" % ctx.author.name,
                                             icon_url=ctx.author.avatar_url)
                            # Causes lag in embed - embed.set_image(url="https://cdn.discordapp.com/attachments/456229881064325131/475498849696219141/ban.gif")
                            embed_message = await ctx.send(embed=embed)
                            # checks guilds
                            for banSyncGuild in guilds:
                                guild = bot.get_guild(int(banSyncGuild.GuildID))
                                if guild is None:  # Check if guild is none
                                    await logger.log("Guild is none... GuildID: " + banSyncGuild.GuildID, bot, "ERROR")
                                    continue
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
                                # Does the embed change
                                guildCount += 1
                                percentRaw = (guildCount / guildCountAll) * 100
                                percent = round(percentRaw, 1)
                                logger.logDebug("Percent: " + str(percent), "DEBUG")
                                if ((percent == percent1) or (percent == percent2) or (percent == percent3) or (
                                        percent == percent4)) and (percent != messagepercentage):
                                    messagepercentage = percent
                                    logger.logDebug("Embed update triggered, percent: " + str(percent), "DEBUG")
                                    embed = discord.Embed(title="Account is being banned...", color=discord.Color.green(),
                                                          description="%s%% complete! 👌" % percent)
                                    embed.set_footer(text="%s - Global WatchDog Moderator" % ctx.author.name,
                                                     icon_url=ctx.author.avatar_url)
                                    await embed_message.edit(embed=embed)
                        # Do this when done
                        # Check for testMode
                        if os.getenv('testModeEnabled') != "True":
                            # Get the ban reason, if there is any
                            banreason = None
                            if len(args) > 1:
                                banreason = ' '.join(args)
                            # Send private ban notif in private moderator ban list as well as message in botlog
                            await logBan(ctx, user, reason=banreason)
                        else:
                            logger.logDebug("TestSent (unban) embeds and prvlist notif for " + user.name + " (" + str(
                                user.id) + ")", "DEBUG")
                        # send final embed, telling the ban was sucessful
                        embed = discord.Embed(title="Account banned", color=discord.Color.green(),
                                              description="`%s` has been globally banned 👌" % user)
                        embed.set_footer(text="%s - Global WatchDog Moderator" % ctx.author.name,
                                         icon_url=ctx.author.avatar_url)
                        embed.set_image(
                            url="https://cdn.discordapp.com/attachments/456229881064325131/475498849696219141/ban.gif")
                        await embed_message.edit(embed=embed)
            else:
                await ctx.send(
                    embed=Embed(color=discord.Color.red(), description="You are not a Global Moderator! Shame!"))

        @bot.command(name="unban")
        async def _unban(ctx, arg1, *, reason="WatchDog - Global Unban"):
            """Unbans a user globally."""
            if isModerator(ctx.author.id):
                if os.getenv('testModeEnabled') == "True":
                    await logger.log(
                        "TestMode seems enabled.. ignores unban functions. Check the console/script logs for the full debugging logs!",
                        bot, "DEBUG")
                # Sends main embed
                guildCount = 0
                guilds = database.getBanSyncGuilds()
                if len(guilds) >= 1:
                    guildCountAll = len(guilds)
                    percent1 = round((round((guildCountAll / 5 * 1), 0) / (guildCountAll) * 100), 1)
                    percent2 = round((round((guildCountAll / 5 * 2), 0) / (guildCountAll) * 100), 1)
                    percent3 = round((round((guildCountAll / 5 * 3), 0) / (guildCountAll) * 100), 1)
                    percent4 = round((round((guildCountAll / 5 * 4), 0) / (guildCountAll) * 100), 1)
                    logger.logDebug(
                        "PercentageChecks: " + str(percent1) + ", " + str(percent2) + ", " + str(percent3) + ", " + str(
                            percent4))
                    messagepercentage = 0
                    try:
                        user = await getUser(ctx, arg1)
                    except Exception as e:
                        await ctx.send(embed=Embed(color=discord.Color.red(), description="Specified user not found!"))
                        await logger.log("Could not get a specified user - Specified arg: %s - Error: %s" % (arg1, e), bot,
                                         "ERROR")
                        return
                    embed = discord.Embed(title="Account is being unbanned...", color=discord.Color.green(),
                                          description="0% complete! 👌")
                    embed.set_footer(text="%s - Global WatchDog Moderator" % ctx.author.name,
                                     icon_url=ctx.author.avatar_url)
                    # Causes lag in embed - embed.set_image(url="https://cdn.discordapp.com/attachments/456229881064325131/475498943178866689/unban.gif")
                    embed_message = await ctx.send(embed=embed)
                    for banSyncGuild in guilds:
                        guild = bot.get_guild(int(banSyncGuild.GuildID))
                        if guild is None:  # Check if guild is none
                            await logger.log("Guild is none... GuildID: " + banSyncGuild.GuildID, bot, "ERROR")
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
                        guildCount += 1
                        percentRaw = (guildCount / guildCountAll) * 100
                        percent = round(percentRaw, 1)
                        logger.logDebug("Percent: " + str(percent), "DEBUG")
                        if ((percent == percent1) or (percent == percent2) or (percent == percent3) or (
                                percent == percent4)) and (percent != messagepercentage):
                            messagepercentage = percent
                            logger.logDebug("Embed update triggered, percent: " + str(percent), "DEBUG")
                            embed = discord.Embed(title="Account is being unbanned...", color=discord.Color.green(),
                                                  description="%s%% complete! 👌" % percent)
                            embed.set_footer(text="%s - Global WatchDog Moderator" % ctx.author.name,
                                             icon_url=ctx.author.avatar_url)
                            await embed_message.edit(embed=embed)
                # do this when done
                # Check for testMode
                if os.getenv('testModeEnabled') != "True":
                    # Send private ban notif in private moderator ban list as well as message in botlog
                    await logBan(ctx, user, unban=True)
                else:
                    logger.logDebug(
                        "TestSent (unban) embeds and prvlist notif for " + user.name + " (" + str(user.id) + ")",
                        "DEBUG")
                # edits final embed
                embed = discord.Embed(title="Account unbanned", color=discord.Color.green(),
                                      description="`%s` has been globally unbanned 👌" % user)
                embed.set_footer(text="%s - Global WatchDog Moderator" % ctx.author.name,
                                 icon_url=ctx.author.avatar_url)
                embed.set_image(
                    url="https://cdn.discordapp.com/attachments/456229881064325131/475498943178866689/unban.gif")
                await embed_message.edit(embed=embed)
            else:
                await ctx.send(
                    embed=Embed(color=discord.Color.red(), description="You are not a Global Moderator! Shame!"))

        @bot.command(name="mban", aliases=["multipleban"])
        async def _mban(ctx, *args, reason="WatchDog - Global Ban"):
            """Bans multiple users globally."""
            if isModerator(ctx.author.id):
                if os.getenv('testModeEnabled') == "True":
                    await logger.log(
                        "TestMode seems enabled.. ignores ban functions. Check the console/script logs for the full debugging logs!",
                        bot, "DEBUG")
                banguild = bot.get_guild(int(os.getenv('banlistguild')))
                banguild_ban_list = await banguild.bans()
                # remove dupes
                args = list(dict.fromkeys(args))
                # sort the args into users and reason
                sortedargs = await sortArgs(ctx, args)
                print(sortedargs)
                users = sortedargs[0]
                print(users)
                reason = sortedargs[1]
                print(reason)
                # count args
                argCountAll = len(users)
                percent1 = round((round((argCountAll / 5 * 1), 0) / (argCountAll) * 100), 1)
                percent2 = round((round((argCountAll / 5 * 2), 0) / (argCountAll) * 100), 1)
                percent3 = round((round((argCountAll / 5 * 3), 0) / (argCountAll) * 100), 1)
                percent4 = round((round((argCountAll / 5 * 4), 0) / (argCountAll) * 100), 1)
                logger.logDebug(
                    "PercentageChecks: " + str(percent1) + ", " + str(percent2) + ", " + str(percent3) + ", " + str(
                        percent4))
                messagepercentage = 0
                if argCountAll == 0:
                    return
                else:
                    # Sends main embed
                    argCount = 0
                    embed = discord.Embed(title="Accounts are being banned...", color=discord.Color.green(),
                                          description="0% complete! 👌")
                    embed.set_footer(text="%s - Global WatchDog Moderator" % ctx.author.name,
                                     icon_url=ctx.author.avatar_url)
                    embed_message = await ctx.send(embed=embed)
                    # ban on own guild
                    for user in users:
                        if user == ctx.bot.user:
                            await ctx.send(
                                embed=Embed(color=discord.Color.red(), description="ID of bot was found in list!"))
                            argslist = list(users)
                            argslist.remove(user)
                            users = tuple(argslist)
                            continue
                        elif isModerator(user.id):
                            await ctx.send(embed=Embed(color=discord.Color.red(),
                                                       description="ID of Global Moderator was found in list!"))
                            argslist = list(users)
                            argslist.remove(user)
                            users = tuple(argslist)
                            continue
                        else:
                            # Check for testMode
                            if os.getenv('testModeEnabled') != "True":
                                # Priorize banning all accounts on own guild
                                # tries to ban
                                try:
                                    await ctx.guild.ban(user, reason="WatchDog - Global Ban")
                                except:
                                    await logger.log("Could not ban the user `%s` (%s) in the guild `%s` (%s)" % (
                                        user.name, user.id, ctx.guild.name, ctx.guild.id), bot, "INFO")
                            else:
                                logger.logDebug("TestBanned (mban) " + user.name + " (" + str(
                                    user.id) + "), in the guild " + ctx.guild.name + "(" + str(ctx.guild.id) + ")",
                                                "DEBUG")
                    # ban on all other guilds
                    for user in users:
                        banned = False

                        if database.isBanned(user.id):
                            logger.logDebug("User already banned, skipping - " + user.name, "DEBUG")
                            argslist = list(users)
                            argslist.remove(user)
                            users = tuple(argslist)
                            # Does the embed change
                            percentRaw = (argCount / argCountAll) * 100
                            percent = round(percentRaw, 1)
                            logger.logDebug("Percent: " + str(percent), "DEBUG")
                            if ((percent == percent1) or (percent == percent2) or (percent == percent3) or (
                                    percent == percent4)) and (percent != messagepercentage):
                                messagepercentage = percent
                                logger.logDebug("Embed update triggered, percent: " + str(percent), "DEBUG")
                                embed = discord.Embed(title="Accounts are being banned...",
                                                      color=discord.Color.green(),
                                                      description="%s%% complete! 👌" % percent)
                                embed.set_footer(text="%s - Global WatchDog Moderator" % ctx.author.name,
                                                 icon_url=ctx.author.avatar_url)
                                await embed_message.edit(embed=embed)
                            banned = True
                            break

                        if banned:
                            argCount += 1
                            continue
                        elif user == ctx.bot.user:
                            argCount += 1
                            argslist = list(users)
                            argslist.remove(user)
                            users = tuple(argslist)
                            continue
                        elif isModerator(user.id):
                            argCount += 1
                            argslist = list(users)
                            argslist.remove(user)
                            users = tuple(argslist)
                            continue
                        else:
                            # checks other guilds
                            for banSyncGuild in database.getBanSyncGuilds():
                                guild = bot.get_guild(int(banSyncGuild.GuildID))
                                if guild is None:  # Check if guild is none
                                    await logger.log("Guild is none... GuildID: " + banSyncGuild.GuildID, bot, "ERROR")
                                    continue

                                # checks if own guild, if it is, skip
                                if guild != ctx.guild:
                                    # Check for testMode
                                    if os.getenv('testModeEnabled') != "True":
                                        # tries to ban
                                        try:
                                            await guild.ban(user, reason="WatchDog - Global Ban")
                                        except Exception as e:
                                            await logger.log(
                                                "Could not ban the user `%s` (%s) in the guild `%s` (%s) - %s" % (
                                                    user.name, user.id, guild.name, guild.id, e), bot, "INFO")
                                    else:
                                        logger.logDebug("TestBanned (mban) " + user.name + " (" + str(
                                            user.id) + "), in the guild " + guild.name + "(" + str(guild.id) + ")",
                                                        "DEBUG")
                            # Does the embed change
                            argCount += 1
                            percentRaw = (argCount / argCountAll) * 100
                            percent = round(percentRaw, 1)
                            logger.logDebug("Percent: " + str(percent), "DEBUG")
                            if ((percent == percent1) or (percent == percent2) or (percent == percent3) or (
                                    percent == percent4)) and (percent != messagepercentage):
                                messagepercentage = percent
                                logger.logDebug("Embed update triggered, percent: " + str(percent), "DEBUG")
                                embed = discord.Embed(title="Accounts are being banned...", color=discord.Color.green(),
                                                      description="%s%% complete! 👌" % percent)
                                embed.set_footer(text="%s - Global WatchDog Moderator" % ctx.author.name,
                                                 icon_url=ctx.author.avatar_url)
                                await embed_message.edit(embed=embed)
                            # Do this when done
                            # Check for testMode
                            if os.getenv('testModeEnabled') != "True":
                                # Send private ban notif in private moderator ban list as well as message in botlog
                                await logBan(ctx, user, reason=reason)
                            else:
                                logger.logDebug(
                                    "TestSent (mban) embeds and prvlist notif for " + user.name + " (" + str(
                                        user.id) + ")", "DEBUG")
                    # send final embed, telling the ban was sucessful
                    if len(users) == 1:
                        desc_string = "%s account has been globally banned 👌" % len(users)
                    else:
                        desc_string = "%s accounts have been globally banned 👌" % len(users)

                    embed = discord.Embed(title="Accounts banned", color=discord.Color.green(),
                                          description=desc_string)
                    embed.set_footer(text="%s - Global WatchDog Moderator" % ctx.author.name,
                                     icon_url=ctx.author.avatar_url)
                    embed.set_image(
                        url="https://cdn.discordapp.com/attachments/456229881064325131/475498849696219141/ban.gif")
                    await embed_message.edit(embed=embed)
            else:
                await ctx.send(
                    embed=Embed(color=discord.Color.red(), description="You are not a Global Moderator! Shame!"))


def setup(bot):
    bot.add_cog(Moderation(bot))
