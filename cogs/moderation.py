import asyncio
import discord
from discord import Embed
from discord.ext import commands
import os

class Moderation:
    def __init__(self,bot):
        self.bot = bot
        
        @bot.command()
        @commands.guild_only()
        @commands.bot_has_permissions(ban_members=True)
        @commands.has_permissions(ban_members=True) 
        async def sync(ctx):
            """Sync the bans."""
            banguild = bot.get_guild(int(os.getenv('banlistguild')))
            ban_list = await banguild.bans()
            for BanEntry in ban_list:
                try:
                    await ctx.guild.ban(BanEntry.user, reason=f"WatchDog - Global Ban")
                except:
                    channel = bot.get_channel(int(os.getenv('botlogfail')))
                    await channel.send("**[Info]** Could not syncban the user `%s` (%s) in the guild `%s` (%s)" % (BanEntry.user.name, BanEntry.user.id, ctx.guild.name, ctx.guild.id))
            embed = discord.Embed(title="Sync complete", color=discord.Color.green(),
                description="Synchronisation complete! 👌")
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.set_image(url="https://cdn.discordapp.com/attachments/456229881064325131/485934104156569600/happysuccess.gif")
            await ctx.send(embed=embed)

        @bot.command()
        @commands.guild_only()
        @commands.bot_has_permissions(ban_members=True)
        async def revsync(ctx):
            """Sync bans from server to central."""
            ban_list = await ctx.guild.bans()
            mods = list(map(int, os.getenv("mods").split()))
            if ctx.author.id in mods:
                for guild in bot.guilds:
                    for BanEntry in ban_list:
                        if BanEntry.user == ctx.bot.user:
                            channel = bot.get_channel(int(os.getenv('botlogfail')))
                            await channel.send("**[Alert]** Someone tried to ban the bot during a revsync. Moderator: `%s` (%s) in the guild `%s` (%s)" % (ctx.author.name, ctx.author.id, guild.name, guild.id))
                        elif BanEntry.user.id in mods:
                            channel = bot.get_channel(int(os.getenv('botlogfail')))
                            await channel.send("**[Alert]** Someone tried to ban a Global Moderator during a revsync. Moderator: `%s` (%s) in the guild `%s` (%s)" % (ctx.author.name, ctx.author.id, guild.name, guild.id))
                        else:
                            try:
                                await guild.ban(BanEntry.user, reason=f"WatchDog - Global Ban")
                            except:
                                channel = bot.get_channel(int(os.getenv('botlogfail')))
                                await channel.send("**[Info]** Could not revsyncban the user `%s` (%s) in the guild `%s` (%s)" % (BanEntry.user.name, BanEntry.user.id, guild.name, guild.id))
                            #Send public ban notif in public ban list
                            pblchannel = bot.get_channel(int(os.getenv('pbanlist')))
                            pblembed = discord.Embed(title="Account banned", color=discord.Color.red(),
                                description="`%s` has been globally banned" % BanEntry.user.id)
                            pblembed.set_footer(text="%s has been globally banned" % BanEntry.user, icon_url="https://cdn.discordapp.com/attachments/456229881064325131/489102109363666954/366902409508814848.png")
                            pblembed.set_thumbnail(url=BanEntry.user.avatar_url)
                            await pblchannel.send(embed=pblembed)
                            #Send private ban notif in private moderator ban list
                            prvchannel = bot.get_channel(int(os.getenv('prvbanlist')))
                            prvembed = discord.Embed(title="Account banned", color=discord.Color.red(),
                                description="`%s` has been globally banned" % BanEntry.user.id)
                            prvembed.add_field(name="Moderator", value="%s (`%s`)" % (ctx.author.name, ctx.author.id), inline=True)
                            prvembed.add_field(name="Name when banned", value="%s" % BanEntry.user, inline=True)
                            prvembed.add_field(name="In server", value="%s (`%s`)" % (guild.name, guild.id), inline=True)
                            prvembed.add_field(name="In channel", value="%s (`%s`)" % (ctx.channel.name, ctx.channel.id), inline=True)
                            prvembed.set_footer(text="%s has been globally banned" % BanEntry.user, icon_url="https://cdn.discordapp.com/attachments/456229881064325131/489102109363666954/366902409508814848.png")
                            prvembed.set_thumbnail(url=BanEntry.user.avatar_url)
                            await prvchannel.send(embed=prvembed)
                embed = discord.Embed(title="Revsync complete", color=discord.Color.green(),
                    description="Reverse synchronisation complete! 👌")
                embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                embed.set_image(url="https://cdn.discordapp.com/attachments/485619099481800714/485917795679338496/1521567278_980x.gif")
                await ctx.send(embed=embed)
            else:
                await ctx.send(embed=Embed(color=discord.Color.red(), description="You are not a Global Moderator! Shame!"))

#   Disabled because chat cannot handle that big a list anymore - was used for debugging
#        @bot.command()
#        async def listbans(ctx):
#            """Get all the bans in List form."""
#            mods = list(map(int, os.getenv("mods").split()))
#            if ctx.author.id in mods:
#                banguild = bot.get_guild(int(os.getenv('banlistguild')))
#                ban_list = await banguild.bans()
#                await ctx.send(embed=Embed(color=discord.Color.purple(), description="%s" % ban_list))
#            else:
#                await ctx.send(embed=Embed(color=discord.Color.red(), description="You are not a Global Moderator! Shame!"))

        @bot.command()
        async def ban(ctx, user_id: int, *, reason = "No reason given"):
            """Bans a user globally."""
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
                            await guild.ban(user, reason=f"WatchDog - Global Ban")
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

        @bot.command()
        async def unban(ctx, user_id: int, *, reason = "No reason given"):
            """Unbans a user globally."""
            mods = list(map(int, os.getenv("mods").split()))
            if ctx.author.id in mods:
                user = await ctx.bot.get_user_info(user_id)
                for guild in bot.guilds:   
                    try:
                        await guild.unban(user, reason=f"WatchDog - Global Unban")
                    except:
                        channel = bot.get_channel(int(os.getenv('botlogfail')))
                        await channel.send("**[Info]** Could not unban the user `%s` (%s) in the guild `%s` (%s)" % (user.name, user.id, guild.name, guild.id))
                embed = discord.Embed(title="Account unbanned", color=discord.Color.green(),
                                    description="`%s` has been globally unbanned 👌" % user)
                embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                embed.set_image(url="https://cdn.discordapp.com/attachments/456229881064325131/475498943178866689/unban.gif")
                await ctx.send(embed=embed)
                channel = bot.get_channel(int(os.getenv('botlog')))
                await channel.send(embed=Embed(color=discord.Color.green(), description="Moderator `%s` unbanned `%s` - (%s)" % (ctx.author.name, user.name, user.id)))
                #Send public unban notif in public ban list
                pblchannel = bot.get_channel(int(os.getenv('pbanlist')))
                pblembed = discord.Embed(title="Account unbanned", color=discord.Color.green(),
                    description="`%s` has been globally unbanned" % user.id)
                pblembed.set_footer(text="%s has been globally unbanned" % user, icon_url="https://cdn.discordapp.com/attachments/456229881064325131/489102109363666954/366902409508814848.png")
                pblembed.set_thumbnail(url=user.avatar_url)
                await pblchannel.send(embed=pblembed)
                #Send private ban notif in private moderator ban list
                prvchannel = bot.get_channel(int(os.getenv('prvbanlist')))
                prvembed = discord.Embed(title="Account unbanned", color=discord.Color.green(),
                    description="`%s` has been globally unbanned" % user.id)
                prvembed.add_field(name="Moderator", value="%s (`%s`)" % (ctx.author.name, ctx.author.id), inline=True)
                prvembed.add_field(name="Name when unbanned", value="%s" % user, inline=True)
                prvembed.add_field(name="In server", value="%s (`%s`)" % (ctx.guild.name, ctx.guild.id), inline=True)
                prvembed.add_field(name="In channel", value="%s (`%s`)" % (ctx.channel.name, ctx.channel.id), inline=True)
                prvembed.set_footer(text="%s has been globally unbanned" % user, icon_url="https://cdn.discordapp.com/attachments/456229881064325131/489102109363666954/366902409508814848.png")
                prvembed.set_thumbnail(url=user.avatar_url)
                await prvchannel.send(embed=prvembed)
            else:
                await ctx.send(embed=Embed(color=discord.Color.red(), description="You are not a Global Moderator! Shame!"))
            
def setup(bot):
    bot.add_cog(Moderation(bot))
