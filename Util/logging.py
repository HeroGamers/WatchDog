import os
from discord import Embed

async def log(message, bot):
    channel = bot.get_channel(int(os.getenv('botlog')))
    logDebug(message)
    await channel.send(message)

def logDebug(message):
    print(message)

async def logEmbed(color, description, bot, debug=""):
    channel = bot.get_channel(int(os.getenv('botlog')))
    await channel.send(embed=Embed(color=color, description=description))
    if debug == "":
        logDebug(description)
        return
    logDebug(debug)