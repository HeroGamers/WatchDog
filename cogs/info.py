import discord
from discord import Embed
from discord.ext import commands
from Util import logger
import os

from database import isModerator
from database import isBanned
from database import getBan


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="code", aliases=["source", "sourcecode"])
    async def _code(self, ctx):
        """View and/or help with the source code of WatchDog."""
        await ctx.send("The source code for WatchDog can be found here: https://github.com/Fido2603/WatchDog")

    @commands.command(name="support")
    async def _support(self, ctx):
        """Get help and support regarding the bot."""
        await ctx.send("The forest where WatchDog roams, Treeland: https://discord.gg/PvFPEfd")

    @commands.command(name="appeal")
    async def _appeal(self, ctx):
        """Appeal bans through the appeal server."""
        await ctx.send("Banned? Appeal here: https://discord.gg/J9YVWgF")

    @commands.command(name="invite")
    async def _invite(self, ctx):
        """How to invite the bot."""
        await ctx.send(
            "Invite me to your server with this link: "
            "<https://discordapp.com/oauth2/authorize?scope=bot&client_id=475447317072183306&permissions"
            "=0x00000004>")

    @commands.command(name="botinfo", aliases=["bot"])
    async def _botinfo(self, ctx):
        """Retrives information about the bot."""
        embed = discord.Embed(title="Bot Information", color=discord.Color.green(),
                              description="")
        embed.add_field(name="Creation Date",
                        value="%s" % discord.utils.snowflake_time(ctx.bot.user.id).strftime(
                            "%Y-%m-%d %H:%M:%S"), inline=True)
        embed.add_field(name="Guilds", value="%s" % len(self.bot.guilds), inline=True)
        ban_list_guild = self.bot.get_guild(int(os.getenv('banlistguild')))
        ban_list = await ctx.guild.bans()
        embed.add_field(name="Global Bans", value="%s" % len(ban_list), inline=True)
        embed.add_field(name="Central Server", value=ban_list_guild.name,
                        inline=True)
        embed.add_field(name="Privacy Policy", value="For the Privacy Policy, please send a DM to HeroGamers through the support server!", inline=True)
        embed.set_footer(text="%s" % ctx.author.name,
                         icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name="userinfo", aliases=["whois", "lookup", "info"])
    async def _userinfo(self, ctx, arg1):
        """Gets info about a user."""
        try:
            user = await ctx.bot.fetch_user(arg1)
        except Exception as e:
            logger.logDebug("User not found! - %s" % e)
            try:
                user = await ctx.bot.fetch_user(ctx.message.mentions[0].id)
            except Exception as e:
                logger.logDebug("User not found! - %s" % e)
                try:
                    user = await ctx.bot.fetch_user(ctx.message.mentions[0].id)
                except Exception as e:
                    logger.logDebug("User not found! - %s" % e)
                    try:
                        user = discord.utils.get(ctx.message.guild.members, name=arg1)
                    except Exception as e:
                        logger.logDebug("User not found! - %s" % e)
                        await ctx.send("User not found!")
        if user is None:
            await ctx.send("User not found!")
        else:
            embed = discord.Embed(title="User Information", color=discord.Color.green(),
                                  description="DiscordTag: %s#%s" % (user.name, user.discriminator))
            embed.add_field(name="ID:", value="%s" % user.id, inline=True)
            embed.add_field(name="Created at:",
                            value="%s" % discord.utils.snowflake_time(user.id).strftime("%Y-%m-%d %H:%M:%S"),
                            inline=True)
            isUserBanned = isBanned(user.id)
            embed.add_field(name="Banned:", value="Yes" if isUserBanned else "No", inline=True)
            embed.add_field(name="In guild with bot:", value="Pending...", inline=True)
            if isUserBanned & isModerator(ctx.author.id):
                banreason = getBan(user.id).Reason
                if banreason is None:
                    banreason = "None"
                embed.add_field(name="Ban reason:", value=banreason, inline=True)
            embed.set_thumbnail(url=user.avatar_url)
            embed.set_footer(text="Userinfo requested by %s" % ctx.author.name, icon_url=ctx.author.avatar_url)
            embed_message = await ctx.send(embed=embed)

            inguildwithbot = "No"
            member = None
            for guild in self.bot.guilds:
                if inguildwithbot == "Yes":
                    break
                member = guild.get_member(user.id)
                if member:
                    inguildwithbot = "Yes"
                    break

            if inguildwithbot == "Yes":
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
