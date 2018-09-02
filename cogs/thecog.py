import asyncio
import discord
from discord import Embed
#import globalmods
#import config
from discord.ext import commands
import os

class TheCog:
    def __init__(self,bot):
        self.bot = bot
        
        @bot.command()
        @commands.guild_only()
        @commands.bot_has_permissions(ban_members=True)
        @commands.has_permissions(ban_members=True) 
        async def sync(ctx):
            """Sync the bans."""
            #banguild = bot.get_guild(config.banlistguild)
            banguild = bot.get_guild(int(os.getenv('banlistguild')))
            ban_list = await banguild.bans()
            for BanEntry in ban_list:
                await ctx.guild.ban(BanEntry.user, reason=f"WatchDog - Global Ban")
            embed = discord.Embed(title="Sync complete", color=discord.Color.green(),
                description="Synchronisation complete! 👌")
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.set_image(url="https://media0.giphy.com/media/h8UyZ6FiT0ptC/giphy.gif")
            await ctx.send(embed=embed)

        @bot.command()
        async def get_bans(ctx):
            """Get all the bans in List form."""
            #if ctx.author.id in globalmods.mods:
            mods = list(map(int, os.getenv('mods').split()))
            if ctx.author.id in mods:
                #banguild = bot.get_guild(config.banlistguild)
                banguild = bot.get_guild(int(os.getenv('banlistguild')))
                ban_list = await banguild.bans()
                await ctx.send(embed=Embed(color=discord.Color.purple(), description="%s" % ban_list))
            else:
                await ctx.send(embed=Embed(color=discord.Color.red(), description="You are not a Global Moderator! Shame!"))

        @bot.command()
        async def ban(ctx, user_id: int, *, reason = "No reason given"):
            """Bans a user globally."""
            #if ctx.author.id in globalmods.mods:
            mods = list(map(int, os.getenv('mods').split()))
            if ctx.author.id in mods:
                user = await ctx.bot.get_user_info(user_id)
                if user == ctx.bot.user:
                    await ctx.send(embed=Embed(color=discord.Color.red(), description="What are you trying to do? Shame!"))
                #elif user in globalmods.mods:
                elif user in mods:
                    await ctx.send(embed=Embed(color=discord.Color.red(), description="You cannot ban a Global Moderator, sorry!"))
                else:
                    embed = discord.Embed(title="Account banned", color=discord.Color.green(),
                        description="`%s` has been globally banned 👌" % user)
                    embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                    embed.set_image(url="https://cdn.discordapp.com/attachments/456229881064325131/475498849696219141/ban.gif")
                    await ctx.send(embed=embed)
                    guild = []
                    for guild in bot.guilds:
                        await guild.ban(user, reason=f"WatchDog - Global Ban")
                    #channel = bot.get_channel(config.botlog)
                    channel = bot.get_channel(int(os.getenv('botlog')))
                    await channel.send(embed=Embed(color=discord.Color.red(), description="Moderator `%s` banned `%s`" % (ctx.author.name, user.name)))
            else:
                await ctx.send(embed=Embed(color=discord.Color.red(), description="You are not a Global Moderator! Shame!"))

        @bot.command()
        async def unban(ctx, user_id: int, *, reason = "No reason given"):
            """Unbans an user globally."""
            #if ctx.author.id in globalmods.mods:
            mods = list(map(int, os.getenv('mods').split()))
            if ctx.author.id in mods:
                user = await ctx.bot.get_user_info(user_id)
                embed = discord.Embed(title="Account unbanned", color=discord.Color.green(),
                                    description="`%s` has been globally unbanned 👌" % user)
                embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                embed.set_image(url="https://cdn.discordapp.com/attachments/456229881064325131/475498943178866689/unban.gif")
                await ctx.send(embed=embed)
                for guild in bot.guilds:   
                    await guild.unban(user, reason=f"WatchDog - Global Unban")
                #channel = bot.get_channel(config.botlog)
                channel = bot.get_channel(int(os.getenv('botlog')))
                await channel.send(embed=Embed(color=discord.Color.green(), description="Moderator `%s` unbanned `%s`" % (ctx.author.name, user.name)))
            else:
                await ctx.send(embed=Embed(color=discord.Color.red(), description="You are not a Global Moderator! Shame!"))
            
def setup(bot):
    bot.add_cog(TheCog(bot))
