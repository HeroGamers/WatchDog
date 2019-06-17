import discord
from discord import Embed
from discord.ext import commands
from Util import logging
import os

class Test(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

        @bot.command(name="testban")
        async def _testban(ctx, user_id: int, *, reason = "No reason given"):
            """TestBans a user globally."""
            mods = list(map(int, os.getenv("mods").split()))
            if ctx.author.id in mods:
                user = await ctx.bot.get_user_info(user_id)
                if user == ctx.bot.user:
                    await ctx.send(embed=Embed(color=discord.Color.red(), description="What are you trying to do? Shame!"))
                elif user.id in mods:
                    await ctx.send(embed=Embed(color=discord.Color.red(), description="You cannot ban a Global Moderator, sorry!"))
                else:
                    guild = []
                    for guild in bot.guilds:
                        try:
                            print("yeet - works in %s" % guild.name)
                        except:
                            channel = bot.get_channel(int(os.getenv('botlogfail')))
                            await channel.send("**[Info]** Could not ban the user `%s` (%s) in the guild `%s` (%s)" % (user.name, user.id, guild.name, guild.id))
                    embed = discord.Embed(title="Account banned", color=discord.Color.green(),
                        description="`%s` has been globally banned 👌" % user)
                    embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                    embed.set_image(url="https://cdn.discordapp.com/attachments/456229881064325131/475498849696219141/ban.gif")
                    await ctx.send(embed=embed)
                    channel = bot.get_channel(int(os.getenv('botlog')))
                    await channel.send(embed=Embed(color=discord.Color.red(), description="Moderator `%s` banned `%s` - (%s)" % (ctx.author.name, user.name, user.id)))
                    logging.logDebug("Moderator `%s` banned `%s` - (%s)" % (ctx.author.name, user.name, user.id))
                    #Send public ban notif in public ban list
                    pblchannel = bot.get_channel(int(os.getenv('pbanlist')))
                    pblembed = discord.Embed(title="Account banned", color=discord.Color.red(),
                        description="`%s` has been globally banned" % user.id)
                    pblembed.set_footer(text="%s has been globally banned" % user, icon_url="https://cdn.discordapp.com/attachments/456229881064325131/489102109363666954/366902409508814848.png")
                    pblembed.set_thumbnail(url=user.avatar_url)
                    await pblchannel.send(embed=pblembed)
                    #Send private ban notif in private moderator ban list
                    prvchannel = bot.get_channel(int(os.getenv('prvbanlist')))
                    prvembed = discord.Embed(title="Account banned", color=discord.Color.red(),
                        description="`%s` has been globally banned" % user.id)
                    prvembed.add_field(name="Moderator", value="%s (`%s`)" % (ctx.author.name, ctx.author.id), inline=True)
                    prvembed.add_field(name="Name when banned", value="%s" % user, inline=True)
                    prvembed.add_field(name="In server", value="%s (`%s`)" % (ctx.guild.name, ctx.guild.id), inline=True)
                    prvembed.add_field(name="In channel", value="%s (`%s`)" % (ctx.channel.name, ctx.channel.id), inline=True)
                    prvembed.set_footer(text="%s has been globally banned" % user, icon_url="https://cdn.discordapp.com/attachments/456229881064325131/489102109363666954/366902409508814848.png")
                    prvembed.set_thumbnail(url=user.avatar_url)
                    await prvchannel.send(embed=prvembed)
            else:
                await ctx.send(embed=Embed(color=discord.Color.red(), description="You are not a Global Moderator! Shame!"))

        @bot.command(name="testunban")
        async def _testunban(ctx, user_id: int, *, reason = "No reason given"):
            """TestUnbans a user globally."""
            mods = list(map(int, os.getenv("mods").split()))
            if ctx.author.id in mods:
                user = await ctx.bot.get_user_info(user_id)
                embed = discord.Embed(title="Account unbanned", color=discord.Color.green(),
                                    description="`%s` has been globally unbanned 👌" % user)
                embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                embed.set_image(url="https://cdn.discordapp.com/attachments/456229881064325131/475498943178866689/unban.gif")
                await ctx.send(embed=embed)
                channel = bot.get_channel(int(os.getenv('botlog')))
                await channel.send(embed=Embed(color=discord.Color.green(), description="Moderator `%s` unbanned `%s` - (%s)" % (ctx.author.name, user.name, user.id)))
                logging.logDebug("Moderator `%s` unbanned `%s` - (%s)" % (ctx.author.name, user.name, user.id))
                #Send public unban notif in public ban list
                pblchannel = bot.get_channel(int(os.getenv('pbanlist')))
                pblembed = discord.Embed(title="Account unbanned", color=discord.Color.green(),
                    description="`%s` has been globally unbanned" % user.id)
                pblembed.set_footer(text="%s has been globally unbanned" % user, icon_url="https://cdn.discordapp.com/attachments/456229881064325131/489102109363666954/366902409508814848.png")
                pblembed.set_thumbnail(url=user.avatar_url)
                await pblchannel.send(embed=pblembed)
            else:
                await ctx.send(embed=Embed(color=discord.Color.red(), description="You are not a Global Moderator! Shame!"))

        @bot.command(name="pblbansync")
        async def _pblbansync(ctx):
            """Onetime command to sync all bans to the Public Ban List"""
            mods = list(map(int, os.getenv("mods").split()))
            if ctx.author.id in mods:
                banguild = bot.get_guild(int(os.getenv('banlistguild')))
                ban_list = await banguild.bans()
                for BanEntry in ban_list:
                    try:
                        #Send public ban notif in public ban list
                        pblchannel = bot.get_channel(int(os.getenv('pbanlist')))
                        pblembed = discord.Embed(title="Account banned", color=discord.Color.red(),
                            description="`%s` has been globally banned" % BanEntry.user.id)
                        pblembed.set_footer(text="%s has been globally banned" % BanEntry.user, icon_url="https://cdn.discordapp.com/attachments/456229881064325131/489102109363666954/366902409508814848.png")
                        pblembed.set_thumbnail(url=BanEntry.user.avatar_url)
                        await pblchannel.send(embed=pblembed)
                    except:
                        channel = bot.get_channel(int(os.getenv('botlogfail')))
                        await channel.send("**[Info]** Could not show the user `%s` (%s) in the Public Ban List" % (BanEntry.user.name, BanEntry.user.id))
                await ctx.send("Public Ban list has been synced!")
            else:
                await ctx.send(embed=Embed(color=discord.Color.red(), description="You are not a Global Moderator! Shame!"))

        @bot.command(name="testmban")
        async def _testmban(ctx, *args, reason = "No reason given"):
            """Bans multiple users globally."""
            mods = list(map(int, os.getenv("mods").split()))
            if ctx.author.id in mods:
                argCountAllWithText = len(args)
                if argCountAllWithText == 0:
                    return
                else:
                    argCountAll = 0
                    #Sends main embed
                    guild = []
                    argCount = 0
                    embed = discord.Embed(title="Accounts are being banned...", color=discord.Color.green(),
                        description="0% complete! 👌")
                    embed.set_footer(text="%s - Global WatchDog Moderator" % ctx.author.name, icon_url=ctx.author.avatar_url)
                    embed_message = await ctx.send(embed=embed)
                    #ban on own guild
                    for arg in args:
                        try:
                            user = await ctx.bot.get_user_info(arg)
                        except:
                            argslist = list(args)
                            argslist.remove(arg)
                            args = tuple(argslist)
                            continue
                        if user == ctx.bot.user:
                            await ctx.send(embed=Embed(color=discord.Color.red(), description="ID of bot was found in list!"))
                            argslist = list(args)
                            argslist.remove(arg)
                            args = tuple(argslist)
                            continue
                        elif user.id in mods:
                            await ctx.send(embed=Embed(color=discord.Color.red(), description="ID of Global Moderator was found in list!"))
                            argslist = list(args)
                            argslist.remove(arg)
                            args = tuple(argslist)
                            continue
                        else:
                            #Priorize banning all accounts on own guild
                            #tries to ban
                            try:
                                await ctx.send("wowie, %s just got testbanned in %s" % (user.name, ctx.guild.name))
                                #await ctx.guild.ban(user, reason=f"WatchDog - Global Ban")
                            except:
                                channel = bot.get_channel(int(os.getenv('botlogfail')))
                                await channel.send("**[Info]** Could not ban the user `%s` (%s) in the guild `%s` (%s)" % (user.name, user.id, ctx.guild.name, ctx.guild.id))
                            #Sends a message in the botlog
                            channel = bot.get_channel(int(os.getenv('botlog')))
                            await channel.send(embed=Embed(color=discord.Color.red(), description="Moderator `%s` banned `%s` - (%s)" % (ctx.author.name, user.name, user.id)))
                            logging.logDebug("Moderator `%s` banned `%s` - (%s)" % (ctx.author.name, user.name, user.id))
                    #ban on all other guilds
                    for arg in args:
                        try:
                            user = await ctx.bot.get_user_info(arg)
                        except:
                            argslist = list(args)
                            argslist.remove(arg)
                            args = tuple(argslist)
                            continue
                        if user == ctx.bot.user:
                            argslist = list(args)
                            argslist.remove(arg)
                            args = tuple(argslist)
                            continue
                        elif user.id in mods:
                            argslist = list(args)
                            argslist.remove(arg)
                            args = tuple(argslist)
                            continue
                        else:
                            #checks other guilds
                            for guild in bot.guilds:
                                #checks if own guild, if it is, skip
                                if guild != ctx.guild:
                                    #tries to ban
                                    try:
                                        await ctx.send("wowie, %s just got testbanned in %s" % (user.name, guild.name))
                                        #await guild.ban(user, reason=f"WatchDog - Global Ban")
                                    except:
                                        channel = bot.get_channel(int(os.getenv('botlogfail')))
                                        await channel.send("**[Info]** Could not ban the user `%s` (%s) in the guild `%s` (%s)" % (user.name, user.id, guild.name, guild.id))
                        #Does the embed change
                        argCount += 1
                        percentRaw = (argCount/argCountAll)*100
                        percent = round(percentRaw, 1)
                        embed = discord.Embed(title="Accounts are being banned...", color=discord.Color.green(),
                            description="%s%% complete! 👌" % percent)
                        embed.set_footer(text="%s - Global WatchDog Moderator" % ctx.author.name, icon_url=ctx.author.avatar_url)
                        await embed_message.edit(embed=embed)
                        #Do this when done
                        #Send public ban notif in public ban list
                        pblchannel = bot.get_channel(int(os.getenv('pbanlist')))
                        pblembed = discord.Embed(title="Account banned", color=discord.Color.red(),
                            description="`%s` has been globally banned" % user.id)
                        pblembed.set_footer(text="%s has been globally banned" % user, icon_url="https://cdn.discordapp.com/attachments/456229881064325131/489102109363666954/366902409508814848.png")
                        pblembed.set_thumbnail(url=user.avatar_url)
                        await pblchannel.send(embed=pblembed)
                        #Send private ban notif in private moderator ban list
                        prvchannel = bot.get_channel(int(os.getenv('prvbanlist')))
                        prvembed = discord.Embed(title="Account banned", color=discord.Color.red(),
                            description="`%s` has been globally banned" % user.id)
                        prvembed.add_field(name="Moderator", value="%s (`%s`)" % (ctx.author.name, ctx.author.id), inline=True)
                        prvembed.add_field(name="Name when banned", value="%s" % user, inline=True)
                        prvembed.add_field(name="In server", value="%s (`%s`)" % (ctx.guild.name, ctx.guild.id), inline=True)
                        prvembed.add_field(name="In channel", value="%s (`%s`)" % (ctx.channel.name, ctx.channel.id), inline=True)
                        prvembed.set_footer(text="%s has been globally banned" % user, icon_url="https://cdn.discordapp.com/attachments/456229881064325131/489102109363666954/366902409508814848.png")
                        prvembed.set_thumbnail(url=user.avatar_url)
                        await prvchannel.send(embed=prvembed)
                    #send final embed, telling the ban was sucessful
                    embed = discord.Embed(title="Accounts banned", color=discord.Color.green(),
                        description="%s accounts have been globally banned 👌" % argCountAll)
                    embed.set_footer(text="%s - Global WatchDog Moderator" % ctx.author.name, icon_url=ctx.author.avatar_url)
                    embed.set_image(url="https://cdn.discordapp.com/attachments/456229881064325131/475498849696219141/ban.gif")
                    await embed_message.edit(embed=embed)
            else:
                await ctx.send(embed=Embed(color=discord.Color.red(), description="You are not a Global Moderator! Shame!"))

def setup(bot):
    bot.add_cog(Test(bot))
