import asyncio
import discord
from discord import Embed
import globalmods
from discord.ext import commands

class TheCog:
    def __init__(self,bot):
        self.bot = bot
        
        @bot.command()
        async def ban(ctx, user_id: int, *, reason = "No reason given"):
            """Bans a user globally."""
            user = await ctx.bot.get_user_info(user_id)
            if user == ctx.bot.user:
                await ctx.send(embed=Embed(color=discord.Color.red(), description="What are you trying to do? Shame!"))
            elif user in globalmods.mods:
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

        @bot.command()
        async def unban(ctx, user_id: int, *, reason = "No reason given"):
            """Unbans an user globally."""
            user = await ctx.bot.get_user_info(user_id)
            embed = discord.Embed(title="Account unbanned", color=discord.Color.green(),
                                description="`%s` has been globally unbanned 👌" % user)
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.set_image(url="https://cdn.discordapp.com/attachments/456229881064325131/475498943178866689/unban.gif")
            await ctx.send(embed=embed)
            for guild in bot.guilds:   
                await guild.unban(user, reason=f"WatchDog - Global Unban")
            
def setup(bot):
    bot.add_cog(TheCog(bot))
