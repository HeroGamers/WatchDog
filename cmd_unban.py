import discord
from discord import Embed


async def ex(args, message, client, invoke, moderatorname, modetatoravatar):
    newargs = args.__str__()[1:-1].replace("'", "")
    banuserarg = newargs.split(" ")[0].replace(",", "")

    try:
        await client.guild.unban(discord.Object(id=banuserarg))
        embed = discord.Embed(title="Account unbanned", color=discord.Color.green(),
                              description="`%s` has been globally unbanned 👌" % banuserarg)
        embed.set_footer(text=moderatorname, icon_url=modetatoravatar)
        embed.set_image(url="https://cdn.discordapp.com/attachments/456229881064325131/475498943178866689/unban.gif")
        await client.send_message(message.channel, embed=embed)
    except discord.Forbidden:
        await client.send_message(message.channel, embed=Embed(color=discord.Color.red(), description="I need **Ban Members** to do this!"))


