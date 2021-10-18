import datetime
import discord
from discord.ext import commands
import database
from Util import logger
import os


def createEmbed(status, color, reason, appealUser, appeal, ban, moderator=None):
    if ban.Reason is None:
        ban.Reason = "N/A"
    moderatorID_text = ""
    if ban.Moderator is not None:
        moderatorID_text = " (`" + ban.Moderator + "`)"
    moderatorTag = "N/A"
    if moderator is not None:
        moderatorTag = moderator.name + "#" + moderator.discriminator

    banTime = datetime.datetime.strptime(str(ban.Time), '%Y-%m-%d %H:%M:%S.%f')
    appealTime = datetime.datetime.strptime(str(appeal.Time), '%Y-%m-%d %H:%M:%S.%f')

    embed = discord.Embed(title="Ban Appeal - Status: " + status, color=color,
                          description="Appeal Reason: " + reason)
    embed.add_field(name="UserID:", value=str(appealUser.id),
                    inline=True)
    embed.add_field(name="DiscordTag:", value=str(appealUser.name) + "#" + str(appealUser.discriminator),
                    inline=True)
    embed.add_field(name="Banned for:", value=ban.Reason,
                    inline=True)
    embed.add_field(name="Banned by:",
                    value=moderatorTag + moderatorID_text,
                    inline=True)
    embed.add_field(name="Time of ban:", value=banTime.strftime("%Y-%m-%d %H:%M:%S"),
                    inline=True)
    embed.add_field(name="Time of appeal:", value=appealTime.strftime("%Y-%m-%d %H:%M:%S"),
                    inline=True)
    embed.set_footer(text=appealUser.name + "#" + appealUser.discriminator, icon_url=appealUser.avatar_url)

    return embed


class listenerCog(commands.Cog, name="Listener Cog"):
    def __init__(self, bot):
        self.bot = bot

    async def unban(self, user):
        for guild in self.bot.guilds:
            if guild is None:
                await logger.log("Guild is none... GuildID: " + guild.id, self.bot, "ERROR")
                continue

            # Check for testMode
            if os.getenv('testModeEnabled') != "True":
                try:
                    await guild.unban(user, reason="WatchDog - Global Unban")
                except Exception as e:
                    await logger.log("Could not unban the user `%s` (%s) in the guild `%s` (%s)" % (
                        user.name, user.id, guild.name, guild.id), self.bot, "INFO")
                    logger.logDebug(e)
            else:
                logger.logDebug("TestUnBanned (unban) " + user.name + " (" + str(
                    user.id) + "), in the guild " + guild.name + "(" + str(guild.id) + ")", "DEBUG")
        if os.getenv('testModeEnabled') != "True":
            database.invalidateBan(user.id)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return

        joinguild = member.guild
        user = await self.bot.fetch_user(member.id)

        # If guild is appealguild
        if joinguild.id == int(os.getenv('appealguild')):
            await logger.log("User joined the appeal guild! UserID: " + str(member.id), self.bot, "DEBUG")
        # If user is globally banned in the database, ban
        elif database.isBanned(member.id):
            await logger.log("Banned User tried joining a guild! UserID: " + str(member.id), self.bot, "INFO")
            try:
                await joinguild.ban(user, reason="WatchDog - Global Ban")
            except Exception as e:
                await logger.log("Could not ban the user `%s` (%s) in the guild `%s` (%s) - %s" % (
                    user.name, user.id, joinguild.name, joinguild.id, e), self.bot, "INFO")
        else:
            # Ban users whose accounts are newer than x minutes, if the current joined guild has new account ban enabled
            if database.isNewAccountBanGuild(joinguild.id):
                minutes = 10
                user_creationdate = discord.utils.snowflake_time(member.id)
                timediff = (datetime.datetime.utcnow() - user_creationdate).total_seconds() / 60

                if timediff <= minutes:
                    # Send the user a message regarind their ban
                    dm_channel = user.dm_channel
                    if dm_channel is None:
                        await user.create_dm()
                        dm_channel = user.dm_channel

                    # Send message
                    try:
                        await dm_channel.send(
                            "Hello! I am WatchDog - a bot protecting the server, that you were just trying to join, "
                            "from baddies!\n\nYour account is very new, which is one of the key characteristics of "
                            "userbots, whose purposes include raiding and DM advertising. As such, you've been "
                            "globally banned from every server that is protected by WatchDog. If you think that this "
                            "is an error, and would like to appeal your ban, follow this link, and write us an "
                            "appeal! We are sorry for any inconvenience this may have caused "
                            "you!\nhttps://discord.gg/J9YVWgF")
                    except Exception as e:
                        # if we can't send the DM, the user probably has DM's off, at which point we would uhhh, yeah.
                        # back to this later
                        await logger.log(
                            "Couldn't send DM to banned user. User ID: " + str(user.id) + " - Error: " + str(e), self.bot,
                            "INFO")

                    # Ban on current guild
                    try:
                        await joinguild.ban(member, reason="WatchDog - Global Ban")
                    except Exception as e:
                        await logger.log("Could not ban the user `%s` (%s) in the guild `%s` (%s)" % (
                            member.name, member.id, joinguild.name, joinguild.id), self.bot, "INFO")
                        logger.logDebug(e)

                    # Ban on other guilds
                    guilds = [guild for guild in self.bot.guilds if guild.get_member(member.id)]
                    guilds.append(self.bot.get_guild(int(os.getenv('banlistguild'))))
                    for guild in guilds:
                        try:
                            await guild.ban(member, reason="WatchDog - Global Ban")
                        except Exception as e:
                            await logger.log("Could not ban the user `%s` (%s) in the guild `%s` (%s)" % (
                                member.name, member.id, guild.name, guild.id), self.bot, "INFO")
                            logger.logDebug(e)

                    # Send private ban notif in private moderator ban list as well as message in botlog
                    # Sends a message in the botlog
                    color = discord.Color.red()
                    text = "banned"

                    await logger.logEmbed(color,
                                          "`WatchDog` %s `%s` - (%s)" % (
                                          text, member.name, member.id),
                                          self.bot)
                    # Send private ban notif in private moderator ban list
                    prvchannel = self.bot.get_channel(int(os.getenv('prvbanlist')))
                    prvembed = discord.Embed(title="Account " + text, color=color,
                                             description="`%s` has been globally %s" % (member.id, text))
                    prvembed.add_field(name="Moderator", value="WatchDog",
                                       inline=True)
                    prvembed.add_field(name="Name when " + text, value="%s" % member, inline=True)
                    prvembed.add_field(name="In server", value="%s (`%s`)" % (joinguild.name, joinguild.id),
                                       inline=True)
                    prvembed.add_field(name="In channel", value="None",
                                       inline=True)
                    prvembed.add_field(name="Reason", value="New Account (%s minutes)" % timediff,
                                       inline=True)
                    prvembed.set_footer(text="%s has been globally %s" % (member, text),
                                        icon_url="https://cdn.discordapp.com/attachments/456229881064325131/489102109363666954/366902409508814848.png")
                    prvembed.set_thumbnail(url=member.avatar_url)
                    await prvchannel.send(embed=prvembed)
                    # Update the database
                    database.newBan(userid=member.id, discordtag=member.name + "#" + member.discriminator,
                                    moderator=self.bot.user.id, reason="New Account (%s minutes)" % timediff, guild=joinguild.id,
                                    avatarurl=member.avatar_url)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # logger.logDebug("New reaction! Payload emoji name: " + payload.emoji.name)
        userid = payload.user_id
        channel = self.bot.get_channel(payload.channel_id)
        user = channel.guild.get_member(userid)

        # we check whether the reaction added is from the appeal channel
        appealguild = self.bot.get_guild(int(os.getenv('appealguild')))
        appealchannel = None
        for appealguildchannel in appealguild.channels:
            if appealguildchannel.name == "appeal-here":
                appealchannel = appealguildchannel
                break
        if appealchannel is None:
            await logger.log("No appealchannel found! Returning!", self.bot, "ERROR")
            return

        # If the channel is the appeal channel
        if payload.channel_id == appealchannel.id:
            await logger.log("A reaction has been added in the appeal channel! User ID: " + str(user.id), self.bot,
                             "DEBUG")
            if user.bot:
                return

            # Checking whether the user is banned
            if not database.isBanned(userid):
                await logger.log("An user who is not banned tried adding the ban appeal reaction! User ID: " +
                                 str(user.id), self.bot, "DEBUG")
                return

            # Checking whether the user already is verified
            if database.isAppealing(userid):
                await logger.log("Already appealing! User ID: " + str(user.id), self.bot, "DEBUG")
                return

            # Add the user to the db
            database.newBanAppeal(user.id)

            dm_channel = user.dm_channel
            if dm_channel is None:
                await user.create_dm()
                dm_channel = user.dm_channel

            # Send message
            try:
                await dm_channel.send(
                    "Thanks for your interest in appealing your WatchDog Ban!\n\nTo complete your ban "
                    "appeal, please write us a good reasoning on why YOU should get unbanned, "
                    "and why WE were wrong in banning you!")
            except Exception as e:
                # if we can't send the DM, the user probably has DM's off, at which point we would uhhh, yeah. back
                # to this later
                await logger.log(
                    "Couldn't send DM to user that reacted. User ID: " + str(user.id) + " - Error: " + str(e), self.bot,
                    "INFO")
                # send a headsup in the verification channel
                channel = self.bot.get_channel(int(os.getenv('verificationChannel')))
                await channel.send(
                    content=user.mention + " Sorry! It seems like your DM didn't go through, try to enable your DM's for this server!",
                    delete_after=float(30))
                return

        # If the channel is the banappeal channel
        if payload.channel_id == int(os.getenv('banappealschannel')):
            await logger.log("A reaction has been added in the moderator appeal channel! User ID: " + str(user.id), self.bot,
                             "DEBUG")
            if user.bot:
                return

            # Variables used
            guild = self.bot.get_guild(payload.guild_id)
            reactMember = guild.get_member(payload.user_id)
            message = await channel.fetch_message(payload.message_id)

            if payload.emoji.name == "✅" or payload.emoji.name == "❎":
                # Remove the reactions
                await message.remove_reaction(payload.emoji.name, reactMember)
                botMember = guild.get_member(self.bot.user.id)
                await message.remove_reaction("❎", botMember)
                await message.remove_reaction("✅", botMember)
            else:
                return

            appeal = database.getAppealFromMessage(message.id)
            if appeal is None:
                return
            appealUser = self.bot.get_user(int(appeal.UserID))
            ban = database.getBan(appealUser.id)
            if ban is None:
                await logger.log("Ban is none!", self.bot, "WARN")
                return
            reason = str(appeal.Reason)
            moderator = None
            if ban.Moderator is not None:
                moderator = self.bot.get_user(int(ban.Moderator))
            color = discord.Color.blurple()

            status = "None"

            # Approve
            if payload.emoji.name == "✅":
                # Basic approval stuff
                status = "Accepted"
                await self.unban(appealUser)
                database.updateBanAppealStatus(appealUser.id, True, user.id)
                color = discord.Color.green()

                # Send appeal accepted message
                await message.channel.send("Appeal accepted! " + appealUser.name + "#" + appealUser.discriminator
                                           + " has been unbanned!", delete_after=10)

                # Send unban notif in banlist
                if reactMember is not None:
                    await logger.logEmbed(color, "Moderator `%s` unbanned `%s` - (%s)" % (reactMember.name,
                                                                                          appealUser.name,
                                                                                          appealUser.id), self.bot)

                # Send private ban notif in private moderator ban list
                banlistchannel = self.bot.get_channel(int(os.getenv('prvbanlist')))
                banlistembed = discord.Embed(title="Account unbanned", color=discord.Color.green(),
                                             description="`%s` has been globally unbanned" % appealUser.id)
                if reactMember is not None:
                    banlistembed.add_field(name="Moderator", value="%s (`%s`)" % (reactMember.name + "#" +
                                                                                  reactMember.discriminator,
                                                                                  reactMember.id),
                                           inline=True)
                banlistembed.add_field(name="Name when unbanned", value="%s" % appealUser, inline=True)
                banlistembed.add_field(name="In server", value="%s (`%s`)" % (guild.name, guild.id),
                                       inline=True)
                banlistembed.add_field(name="In channel", value="%s (`%s`)" % (channel.name, channel.id),
                                       inline=True)
                banlistembed.set_footer(text="%s has been globally unbanned" % appealUser,
                                        icon_url="https://cdn.discordapp.com/attachments/456229881064325131/489102109363666954/366902409508814848.png")
                banlistembed.set_thumbnail(url=appealUser.avatar_url)
                await banlistchannel.send(embed=banlistembed)

                # Notify the user
                dm_channel = appealUser.dm_channel
                if dm_channel is None:
                    await appealUser.create_dm()
                    dm_channel = appealUser.dm_channel

                # Send message in DM's
                try:
                    await dm_channel.send(
                        "Thanks for your interest in appealing your WatchDog Ban!\n\nYour Ban Appeal has been accepted "
                        "by our Global Moderators, in other words, you are now unbanned! Don't go and get yourself "
                        "banned again!")
                except Exception as e:
                    # if we can't send the DM, the user probably has DM's off, at which point we would uhhh,
                    # yeah. back to this later
                    await logger.log(
                        "Couldn't send DM to banned user. User ID: " + str(appealUser.id) + " - Error: " + str(e), self.bot,
                        "INFO")

                # Kick the user from the appealguild
                try:
                    await appealguild.kick(appealUser)
                except Exception as e:
                    await logger.log("Could not kick user from the appeal guild after being accepted! - " + str(e), self.bot,
                                     "ERROR")
            # Deny
            elif payload.emoji.name == "❎":
                status = "Denied"
                database.updateBanAppealStatus(appealUser.id, False, user.id)
                color = discord.Color.red()

                await message.channel.send("Appeal denied! " + appealUser.name + "#" + appealUser.discriminator
                                           + " has NOT been unbanned!", delete_after=10)

                # Notify the user
                dm_channel = appealUser.dm_channel
                if dm_channel is None:
                    await appealUser.create_dm()
                    dm_channel = appealUser.dm_channel

                # Send message
                try:
                    await dm_channel.send(
                        "Thanks for your interest in appealing your WatchDog Ban!\n\nWe are sorry to inform you that "
                        "your Ban Appeal has been denied by our Global Moderators... If you believe that this is "
                        "unjustified, you can always try appealing again, by writing a new reason, "
                        "or you can try contacting the bot owner, HeroGamers#0001, directly!")
                except Exception as e:
                    # if we can't send the DM, the user probably has DM's off, at which point we would uhhh, yeah.
                    # back to this later
                    await logger.log(
                        "Couldn't send DM to banned user. User ID: " + str(appealUser.id) + " - Error: " + str(e), self.bot,
                        "INFO")

            # Update the embed
            embed = createEmbed(status + " by " + user.name + "#" + user.discriminator, color, reason, appealUser,
                                appeal, ban, moderator)
            await message.edit(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        # return if author is a bot (we're also a bot)
        if message.author.bot:
            return

        # check if it's a DM
        if isinstance(message.channel, discord.DMChannel):
            await logger.log(
                "New message in the DM's! UserID: " + str(message.author.id) + " - Content: " + str(message.content),
                self.bot, "DEBUG")

            if message.content.startswith(os.getenv('prefix')):
                return

            user = message.author
            if database.isAppealing(user.id):
                logger.logDebug("User is appealing")
                isNew = False
                if database.hasNoAppealReason(user.id):
                    logger.logDebug("A new appeal")
                    isNew = True
                database.addBanAppealReason(user.id, message.content)

                appealschannel = self.bot.get_channel(int(os.getenv('banappealschannel')))
                ban = database.getBan(user.id)
                if ban is None:
                    await logger.log("Ban is none!", self.bot, "WARN")
                    return

                # Update the embed
                appeal = database.getAppeal(user.id)
                reason = str(appeal.Reason)
                moderator = None
                if ban.Moderator is not None:
                    moderator = self.bot.get_user(int(ban.Moderator))

                embed = createEmbed("Pending", discord.Color.blurple(), reason, user, appeal, ban, moderator)

                if isNew:
                    appealMessage = await appealschannel.send(embed=embed)
                    database.addAppealMessage(user.id, appealMessage.id)
                else:
                    appealMessage = await appealschannel.fetch_message(int(database.getAppealMessage(user.id)))
                    await appealMessage.edit(embed=embed)
                await appealMessage.add_reaction("✅")
                await appealMessage.add_reaction("❎")

                # Let the user know that we've updated their appeal
                try:
                    await message.channel.send("Thanks for your interest in appealing your WatchDog Ban!\n\nYour "
                                               "appeal reason has been updated, and our moderators will look into it! "
                                               "If you wish to update your appeal reason, then just write a new "
                                               "appeal reason in this DM!")
                except Exception as e:
                    # if we can't send the DM, the user probably has DM's off, at which point we would uhhh, yeah.
                    # back to this later
                    await logger.log(
                        "Couldn't send DM to banned user. User ID: " + str(user.id) + " - Error: " + str(e), self.bot,
                        "INFO")
            else:
                logger.logDebug("User is not appealing")


def setup(bot):
    bot.add_cog(listenerCog(bot))
