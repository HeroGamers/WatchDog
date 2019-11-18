import discord, asyncio
from discord import File
from discord.ext import commands

import database
from Util import logger
import os


class listenerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        bot = self.bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        bot = self.bot
        userid = payload.user_id
        channel = bot.get_channel(payload.channel_id)
        user = channel.guild.get_member(userid)

        # we check whether the reaction added is from the appeal channel
        appealguild = bot.get_guild(int(os.getenv('appealguild')))
        appealchannel = None
        for channel in appealguild.channels:
            if channel.name == "appeal-here":
                appealchannel = channel
                break
        if appealchannel is None:
            await logger.log("No appealchannel found!", bot, "ERROR")
            return
        else:
            if payload.channel_id == appealchannel.id:
                await logger.log("A reaction has been added in the appeal channel! User ID: " + str(user.id), bot,
                                 "DEBUG")
                if user.bot:
                    return

                # Checking whether the user already is verified
                if database.isAppealing(userid):
                    await logger.log("Already appealing! User ID: " + str(user.id), bot, "DEBUG")
                    return

                # Add the user to the db
                await database.newBanAppeal(user.id)

                # if yes, send the user the verification message...
                dm_channel = user.dm_channel
                if dm_channel is None:
                    await user.create_dm()
                    dm_channel = user.dm_channel

                # Send message
                try:
                    await dm_channel.send(
                        "Thanks for your interest in appealing your WatchDog ban! To complete your ban "
                        "appeal, please write us a good reasoning on why YOU should get unbanned, "
                        "and why WE were wrong in banning you!")
                except Exception as e:
                    # if we can't send the DM, the user probably has DM's off, at which point we would uhhh, yeah. back to this later
                    await logger.log(
                        "Couldn't send DM to user that reacted. User ID: " + str(user.id) + " - Error: " + str(e), bot,
                        "INFO")
                    # send a headsup in the verification channel
                    channel = bot.get_channel(int(os.getenv('verificationChannel')))
                    await channel.send(
                        content=user.mention + " Sorry! It seems like your DM didn't go through, try to enable your DM's for this server!",
                        delete_after=float(30))
                    return
        # If the channel is the banappeal channel
        if payload.channel_id == int(os.getenv('banappealschannel')):
            await logger.log("A reaction has been added in the moderator appeal channel! User ID: " + str(user.id), bot,
                             "DEBUG")
            if user.bot:
                return

            message = await bot.fetch_message(payload.message_id)

            # Fetch new reason
            if payload.emoji.name == "arrows_counterclockwise":
                appeal = database.getAppealFromMessage(message.id)
                reason = str(appeal.Reason)
                user = bot.get_user(int(appeal.UserID))
                ban = database.getBan(user.id)
                if ban is None:
                    logger.log("Ban is none!", bot, "WARN")
                    return
                moderator = bot.get_user(int(ban.moderator))

                embed = discord.Embed(title="Ban Appeal", color=discord.Color.green(),
                                      description="Appeal Reason: " + reason)
                embed.add_field(name="UserID:", value=str(user.id),
                                inline=True)
                embed.add_field(name="DiscordTag:", value=str(user.name) + "#" + str(user.discriminator),
                                inline=True)
                embed.add_field(name="Banned for:", value=ban.Reason,
                                inline=True)
                embed.add_field(name="Banned by:",
                                value=moderator.name + "#" + moderator.discriminator + "(`" + ban.Moderator + "`)",
                                inline=True)
                embed.add_field(name="Time of ban:", value=str(ban.Time),
                                inline=True)
                embed.add_field(name="Time of appeal:", value=str(appeal.Time),
                                inline=True)
                embed.set_footer(text=user.name, icon_url=user.avatar_url)
                await message.edit(embed=embed)

            # Approve
            if payload.emoji.name == "white_check_mark":
                print("ok")

            # Deny
            if payload.emoji.name == "negative_squared_cross_mark":
                print("ok")

    @commands.Cog.listener()
    async def on_message(self, message):
        bot = self.bot

        # return if author is a bot (we're also a bot)
        if message.author.bot:
            return

        # check if it's a DM
        if isinstance(message.channel, discord.DMChannel):
            await logger.log("New message in the DM's", bot, "DEBUG")

            if message.content.startswith(os.getenv('prefix')):
                return

            user = message.author
            if database.isAppealing(user.id):
                isNew = False
                if database.hasNoAppealReason(user.id):
                    isNew = True
                database.addBanAppealReason(user.id, message.content)

                await message.channel.send("Thanks for your ban appeal reason! Our moderators will look into it!")

                if isNew:
                    os.getenv('banappealschannel')


def setup(bot):
    bot.add_cog(listenerCog(bot))
