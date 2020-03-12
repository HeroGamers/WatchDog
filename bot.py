import discord
from discord.ext import commands
from discord import Embed, Permissions
from Util import logger
import os
import database

try:
    import config
except ImportError:
    print("Couldn't import config.py")
try:
    import monkeyPatch
except ImportError:
    print("DEBUG: No Monkey patch found!")

bot = commands.Bot(command_prefix=os.getenv('prefix'), description='Well boys, we did it. Baddies is no more.')

startup_extensions = ["essentials",
                      "moderation",
                      "info",
                      "listenerCog"]


# Function to update the database on startup
async def updateDatabase():
    # Fetch bans from the banlistguild, and smack them into the db
    banguild = bot.get_guild(int(os.getenv('banlistguild')))
    ban_list = await banguild.bans()
    for BanEntry in ban_list:
        if not database.isBanned(BanEntry.user.id):
            database.newBan(userid=BanEntry.user.id, discordtag=BanEntry.user.name + "#" + BanEntry.user.discriminator,
                            avatarurl=BanEntry.user.avatar_url)


# Make sure appeal guild is set up properly
async def checkAppealGuild():
    appealguild = bot.get_guild(int(os.getenv('appealguild')))
    appealchannel = None
    for channel in appealguild.channels:
        if channel.name == "appeal-here":
            appealchannel = channel
            break
    if appealchannel is None:
        await logger.log("No appealchannel found! Trying to create one!", bot, "INFO")
        try:
            overwrites = {
                appealguild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
                appealguild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True,
                                                            manage_messages=True, embed_links=True,
                                                            add_reactions=True)
            }
            appealchannel = await appealguild.create_text_channel("appeal-here", overwrites=overwrites)
        except Exception as e:
            await logger.log("Could not create an appeal channel! Returning! - " + str(e), bot, "ERROR")
            return

    history = await appealchannel.history(limit=5).flatten()
    # check if no messages
    if len(history) == 0:  # no messages
        # Sending the message
        await logger.log("Sending the appeal channel message", bot, "INFO")
        message = await appealchannel.send(content="Hello there! Welcome to the WatchDog Appeal Server!\n" +
                                             "\nTo begin your appeal process, please click this reaction!")

        # now we add a reaction to the message
        await message.add_reaction("✅")



@bot.event
async def on_ready():
    # Bot startup is now done...
    logger.logDebug("----------[LOGIN SUCESSFULL]----------", "INFO")
    logger.logDebug("     Username: " + bot.user.name, "INFO")
    logger.logDebug("     UserID:   " + str(bot.user.id), "INFO")
    logger.logDebug("--------------------------------------", "INFO")
    print("\n")


    logger.logDebug("Updating the database!", "INFO")
    await updateDatabase()
    logger.logDebug("Done updating the database!", "INFO")
    print("\n")

    # Ban appeal server setup
    await checkAppealGuild()

    # Bot done starting up
    await logger.log("Bot is ready!", bot, "INFO", "Bot startup done.\n")
    await bot.change_presence(activity=discord.Game(name="with the banhammer"))


@bot.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send("This command cannot be used in private messages")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send(
            embed=Embed(color=discord.Color.red(), description="I need the permission `Ban Members` to sync the bans!"))
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(
            embed=Embed(color=discord.Color.red(), description="You are missing the permission `Ban Members`!"))
    elif isinstance(error, commands.CheckFailure):
        return
    elif isinstance(error, commands.CommandOnCooldown):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        return
    elif isinstance(error, commands.BadArgument):
        return
    elif isinstance(error, commands.CommandNotFound):
        return
    else:
        await ctx.send("Something went wrong while executing that command... Sorry!")
        await logger.log("%s" % error, bot, "ERROR")


@bot.event
async def on_guild_join(guild):
    await logger.log("Joined a new guild (`%s` - `%s`)" % (guild.name, guild.id), bot, "INFO")
    # Check the bot's ban permission
    if Permissions.ban_members in guild.get_member(bot.user.id).guild_permissions:
        # Get bans from db
        bans = database.getBans()
        # make new list for userid in bans, if member is in guild
        ban_members = [userid for userid in bans if guild.get_member(userid)]
        logger.logDebug(str(ban_members))
        # Ban the found users
        for userid in ban_members:
            await guild.ban(bot.get_user(int(userid)), reason="WatchDog - Global Ban")
            logger.logDebug("Banned user in guild hahayes")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    ctx: commands.Context = await bot.get_context(message)
    if message.content.startswith(os.getenv('prefix')):
        if ctx.command is not None:
            if isinstance(message.channel, discord.DMChannel):
                await logger.log("`%s` (%s) used the `%s` command in their DM's" % (
                    ctx.author.name, ctx.author.id, ctx.invoked_with), bot, "INFO")
            else:
                await logger.log("`%s` (%s) used the `%s` command in the guild `%s` (%s), in the channel `%s` (%s)" % (
                    ctx.author.name, ctx.author.id, ctx.invoked_with, ctx.guild.name, ctx.guild.id, ctx.channel.name,
                    ctx.channel.id), bot, "INFO")
            await bot.invoke(ctx)
    else:
        return


if __name__ == '__main__':
    logger.setup_logger()

    # Load extensions
    for extension in startup_extensions:
        try:
            bot.load_extension(f"cogs.{extension}")
        except Exception as e:
            logger.logDebug(f"Failed to load extension {extension}. - {e}", "ERROR")

bot.run(os.getenv('token'))
