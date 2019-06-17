import discord
from discord.ext import commands
from discord import Embed
from Util import logging
import os
try:
    import config
except ImportError:
    print("Couldn't import config.py")

bot = commands.Bot(command_prefix=os.getenv('prefix'), description='I ban people who deserves so...')

startup_extensions = ["essentials",
                      "moderation",
                      "info"]

@bot.event
async def on_ready():
    await logging.log("**[Info]** Bot startup done.", bot)
    print("\n")
    await bot.change_presence(activity=discord.Game(name="with the banhammer"))

@bot.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send("This command cannot be used in private messages")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send(embed=Embed(color=discord.Color.red(), description="I need the permission `Ban Members` to sync the bans!"))
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(embed=Embed(color=discord.Color.red(), description="You are missing the permission `Ban Members`!"))
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
        await logging.log("**[ERROR]** %s" % error, bot)

@bot.event
async def on_guild_join(guild):
    await logging.log("**[Info]** Joined a new guild (`%s` - `%s`)" % (guild.name, guild.id), bot)
    banguild = bot.get_guild(int(os.getenv('banlistguild')))
    ban_list = await banguild.bans()
    for BanEntry in ban_list:
        await guild.ban(BanEntry.user, reason=f"WatchDog - Global Ban")

@bot.event
async def on_message(message:discord.Message):
    if message.author.bot:
        return
    ctx:commands.Context = await bot.get_context(message)
    if message.content.startswith(os.getenv('prefix')):
        if ctx.command is not None:
            await logging.log("**[Command]** `%s` (%s) used the `%s` command in the guild `%s` (%s), in the channel `%s` (%s)" % (ctx.author.name, ctx.author.id, ctx.invoked_with, ctx.guild.name, ctx.guild.id, ctx.channel.name, ctx.channel.id), bot)
            await bot.invoke(ctx)
    else:
        return

if __name__ == '__main__':
    for extension in startup_extensions:
        try:
            bot.load_extension(f"cogs.{extension}")
        except Exception as e:
            logging.logDebug(f"[ERROR] Failed to load extension {extension}. - {e}")

bot.run(os.getenv('token'))
