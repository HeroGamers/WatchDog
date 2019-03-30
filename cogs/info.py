import asyncio
import discord
from discord import Embed
from discord.ext import commands
import os

class Info:
    def __init__(self,bot):
        self.bot = bot

        @bot.command()
        async def support(ctx):
            """Get help and support regarding the bot."""
            await ctx.send("Join this server for support and other talks: https://discord.gg/eH8xS75")

        @bot.command()
        async def invite(ctx):
            """How to invite the bot."""
            await ctx.send("Invite me to your server with this link: https://discordapp.com/oauth2/authorize?scope=bot&client_id=475447317072183306&permissions=0x00000004")

        @bot.command()
        async def botinfo(ctx):
            """Retrives information about the bot - GM only"""
            mods = list(map(int, os.getenv("mods").split()))
            if ctx.author.id in mods:
                embed = discord.Embed(title="Bot Information", color=discord.Color.green(),
                    description="")
                embed.add_field(name="Creation Date", value="%s" % discord.utils.snowflake_time(ctx.bot.user.id).strftime("%Y-%m-%d %H:%M:%S"), inline=True)
                embed.add_field(name="Guilds", value="%s" % len(bot.guilds), inline=True)
                ban_list = await ctx.guild.bans()
                embed.add_field(name="Global Bans", value="%s" % len(ban_list), inline=True)
                embed.add_field(name="Central Server", value=bot.get_guild(int(os.getenv('banlistguild'))).name, inline=True)
                #embed.add_field(name="Log channel", value="<#%s>" % bot.get_channel(int(os.getenv('botlog'))).id, inline=True)
                embed.set_footer(text="%s - Global WatchDog Moderator" % ctx.author.name, icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
            else:
                await ctx.send(embed=Embed(color=discord.Color.red(), description="You are not a Global Moderator! Shame!"))

        @bot.command()
        async def userinfo(ctx, arg1):
            """Gets info about a user"""
            try:
                user = await ctx.bot.get_user_info(arg1)
            except:
                try:
                    user = await ctx.bot.get_user_info(ctx.message.mentions[0].id)
                except:
                    try:
                        user = await ctx.bot.get_user_info(ctx.message.mentions[0].id)
                    except:
                        try:
                            user = discord.utils.get(ctx.message.guild.members, name=arg1)
                        except:
                            await ctx.send("User not found!")
            if user is None:
                await ctx.send("User not found!")
            else:
                embed = discord.Embed(title="User Information", color=discord.Color.green(),
                    description="DiscordTag: %s#%s" % (user.name, user.discriminator))
                embed.add_field(name="ID:", value="%s" % user.id, inline=True)
                embed.add_field(name="Created at:", value="%s" % discord.utils.snowflake_time(user.id).strftime("%Y-%m-%d %H:%M:%S"), inline=True)
                embed.add_field(name="Banned:", value="Pending...", inline=True)
                embed.add_field(name="In guild with bot:", value="Pending...", inline=True)
                embed.set_thumbnail(url=user.avatar_url)
                embed.set_footer(text="Userinfo requested by %s" % ctx.author.name, icon_url=ctx.author.avatar_url)
                embed_message = await ctx.send(embed=embed)

                banned = ""
                banguild = bot.get_guild(int(os.getenv('banlistguild')))
                ban_list = await banguild.bans()
                for BanEntry in ban_list:
                    if user == BanEntry.user:
                        banned = "Yes"
                        break
                    else:
                        banned = "No"
                embed.set_field_at(index=2, name="Banned:", value="%s" % banned, inline=True)
                await embed_message.edit(embed=embed)

                inguildwithbot = ""
                for guild in bot.guilds:
                    for member in guild.members:
                        if user.id == member.id:
                            inguildwithbot = "Yes"
                            break
                        else:
                            inguildwithbot = "No"
                if inguildwithbot == "Yes":
                    status = "Unknown"
                    if str(member.status) == "dnd":
                        status = "Do Not Disturb"
                    elif str(member.status) == "do_not_disturb":
                        status = "Do Not Disturb"
                    elif str(member.status) == "offline":
                        status = "Offline"
                    elif str(member.status) == "online":
                        status = "Online"
                    elif str(member.status) == "idle":
                        status = "Idle"
                    elif str(member.status) == "invisible":
                        status = "Offline"
                    else:
                        status = "Unknown"
                    embed.add_field(name="Status:", value="%s" % status, inline=True)
                embed.set_field_at(index=3, name="In guild with bot:", value="%s" % inguildwithbot, inline=True)
                await embed_message.edit(embed=embed)
            
def setup(bot):
    bot.add_cog(Info(bot))
