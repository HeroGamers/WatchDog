import discord
from discord.ext import commands
from discord import Embed
import cmd_unban
import cmd_ban
import config
import globalmods

client = discord.Client()


commands = {
    "ban": cmd_ban,
    "unban": cmd_unban,
}


@client.event
async def on_ready():
    print("Bot logged in sucessfully.")
    for s in client.guilds:
        print(" - %s (%s)" % (s.name, s.id))
    await client.change_presence(game=discord.Game(name="with the banhammer"))


@client.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content.startswith(config.prefix):
        if message.author.id in globalmods.mods:
            invoke = message.content[len(config.prefix):].split(" ")[0]
            args = message.content.split(" ")[1:]
            moderatorname = message.author.name
            modetatoravatar = message.author.avatar_url
            print("INVOKE: %s\nARGS: %s" % (invoke, args.__str__()[1:-1].replace("'", "")))
            if commands.__contains__(invoke):
                await commands.get(invoke).ex(args, message, client, invoke, moderatorname, modetatoravatar)
            else:
                await client.send_message(message.channel, embed=Embed(color=discord.Color.red(), description="The command `%s` is not a valid command!" % invoke))
        else:
            await client.send_message(message.channel, embed=Embed(color=discord.Color.red(), description="You are not a global moderator! Shame!"))
    else:
        return


client.run(config.token)
