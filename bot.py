import discord
import asyncio
import datetime
from discord.ext import commands
from discord import Embed
from pathlib import Path
import sys, traceback
import os
try:
    import config
except ImportError:
    print("Couldn't import config.py")

bot = commands.Bot(command_prefix=os.getenv('prefix'), description='I ban people who deserves so...')

startup_extensions = ["moderation",
                      "testcog"]

@bot.event
async def on_ready():
    print("[Info] Bot startup done.")
    channel = bot.get_channel(int(os.getenv('botlog')))
    await channel.send("**[Info]** Bot startup done.")
    print("\n")
    await bot.change_presence(game=discord.Game(name="with the banhammer"))

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
        channel = bot.get_channel(int(os.getenv('botlog')))
        await channel.send("**[ERROR]** %s" % error)

@bot.event
async def on_guild_join(guild):
    channel = bot.get_channel(int(os.getenv('botlog')))
    print("[Info] Joined a new guild (`%s` - `%s`)" % (guild.name, guild.id))
    await channel.send("**[Info]** Joined a new guild (`%s` - `%s`)" % (guild.name, guild.id))
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
            print("[Command] %s (%s) just used the %s command in the guild %s (%s)" % (ctx.author.name, ctx.author.id, ctx.invoked_with, ctx.guild.name, ctx.guild.id))
            channel = bot.get_channel(int(os.getenv('botlog')))
            await channel.send("**[Command]** `%s` (%s) used the `%s` command in the guild `%s` (%s), in the channel `%s` (%s)" % (ctx.author.name, ctx.author.id, ctx.invoked_with, ctx.guild.name, ctx.guild.id, ctx.channel.name, ctx.channel.id))
            await bot.invoke(ctx)
    else:
        return

if __name__ == '__main__':
    for extension in startup_extensions:
        try:
            bot.load_extension(f"cogs.{extension}")
        except Exception as e:
            print(f"[ERROR] Failed to load extention {extension}.", e)

bot.run(os.getenv('token'))
