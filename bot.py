import discord
import asyncio
import datetime
from discord.ext import commands
from discord import Embed
from pathlib import Path
import config
import globalmods
import sys, traceback

bot = commands.Bot(command_prefix=config.prefix, description='I ban people who deserves so...')

startup_extensions = ["thecog"]

@bot.event
async def on_ready():
    print("Bot logged in sucessfully.")
    for s in bot.guilds:
        print(" - %s (%s)" % (s.name, s.id))
    await bot.change_presence(game=discord.Game(name="with the banhammer"))


@bot.event
async def on_message(message:discord.Message):
    if message.author.bot:
        return
    ctx:commands.Context = await bot.get_context(message)
    if message.content.startswith(config.prefix):
        if message.author.id in globalmods.mods:
            if ctx.command is not None:
                await bot.invoke(ctx)
        else:
            await ctx.send(embed=Embed(color=discord.Color.red(), description="You are not a Global Moderator! Shame!"))
    else:
        return

if __name__ == '__main__':
    for extension in startup_extensions:
        try:
            bot.load_extension(f"cogs.{extension}")
        except Exception as e:
            print(f"Failed to load extention {extension}.", e)

bot.run(config.token)
