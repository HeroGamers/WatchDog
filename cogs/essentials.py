import asyncio
import discord
from discord import Embed
from discord.ext import commands
from contextlib import redirect_stdout
import inspect
import io
import textwrap
import traceback
import os

class essentials:
    def __init__(self,bot):
        self.bot = bot
        
        @bot.command()
        async def loadcog(ctx, arg1):
            """Loads a cog"""
            mods = list(map(int, os.getenv("mods").split()))
            if ctx.author.id in mods:
                try:
                    bot.load_extension(f"cogs.{arg1}")
                    await ctx.send(f"Successfully loaded the {arg1} extension")
                    channel = bot.get_channel(int(os.getenv('botlog')))
                    await channel.send("**[Info]** Moderator `%s` loaded the extension %s" % (ctx.author.name, arg1))
                except Exception as e:
                    await ctx.send(f"Failed to load the extension {arg1}")
                    channel = bot.get_channel(int(os.getenv('botlog')))
                    await channel.send(f"**[ERROR]** Failed to load the extension {arg1} - {e}")
            else:
                await ctx.send(embed=Embed(color=discord.Color.red(), description="You are not a Global Moderator! Shame!"))

        @bot.command()
        async def listcogs(ctx):
            """Lists all the cogs"""
            mods = list(map(int, os.getenv("mods").split()))
            if ctx.author.id in mods:
                embed = discord.Embed(title="Cogs", color=discord.Color.green(),
                    description="`essentials, fun, info, moderation, test`")
                embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
            else:
                await ctx.send(embed=Embed(color=discord.Color.red(), description="You are not a Global Moderator! Shame!"))

        @bot.command()
        async def unloadcog(ctx, arg1):
            """Unloads a cog"""
            mods = list(map(int, os.getenv("mods").split()))
            if ctx.author.id in mods:
                try:
                    bot.unload_extension(f"cogs.{arg1}")
                    await ctx.send(f"Successfully unloaded the {arg1} extension")
                    channel = bot.get_channel(int(os.getenv('botlog')))
                    await channel.send("**[Info]** Moderator `%s` unloaded the extension %s" % (ctx.author.name, arg1))
                except Exception as e:
                    await ctx.send(f"Failed to unload the extension {arg1}")
                    channel = bot.get_channel(int(os.getenv('botlog')))
                    await channel.send(f"**[ERROR]** Failed to unload the extension {arg1} - {e}")
            else:
                await ctx.send(embed=Embed(color=discord.Color.red(), description="You are not a Global Moderator! Shame!"))

        #Stolen from https://github.com/fourjr/eval-bot/blob/master/src/eval.py
        #Kinda broken, but ehhhh, shh
        @bot.command(name='eval')
        async def _eval(ctx, *, body):
            """Evaluates python code"""
            botowner = int(os.getenv('ownerid'))
            if ctx.author.id == botowner:
                env = {
                    'ctx': ctx,
                    'channel': ctx.channel,
                    'author': ctx.author,
                    'guild': ctx.guild,
                    'message': ctx.message,
                    'source': inspect.getsource,
                }

                env.update(globals())

                body = cleanup_code(body)
                stdout = io.StringIO()
                err = out = None

                to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

                def paginate(text: str):
                    '''Simple generator that paginates text.'''
                    last = 0
                    pages = []
                    for curr in range(0, len(text)):
                        if curr % 1980 == 0:
                            pages.append(text[last:curr])
                            last = curr
                            appd_index = curr
                    if appd_index != len(text)-1:
                        pages.append(text[last:curr])
                    return list(filter(lambda a: a != '', pages))
                
                try:
                    exec(to_compile, env)
                except Exception as e:
                    err = await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')
                    return await ctx.message.add_reaction('\u2049')

                func = env['func']
                try:
                    with redirect_stdout(stdout):
                        ret = await func()
                except Exception as e:
                    value = stdout.getvalue()
                    err = await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
                else:
                    value = stdout.getvalue()
                    if ret is None:
                        if value:
                            try:
                                
                                out = await ctx.send(f'```py\n{value}\n```')
                            except:
                                paginated_text = paginate(value)
                                for page in paginated_text:
                                    if page == paginated_text[-1]:
                                        out = await ctx.send(f'```py\n{page}\n```')
                                        break
                                    await ctx.send(f'```py\n{page}\n```')
                    else:
                        bot._last_result = ret
                        try:
                            out = await ctx.send(f'```py\n{value}{ret}\n```')
                        except:
                            paginated_text = paginate(f"{value}{ret}")
                            for page in paginated_text:
                                if page == paginated_text[-1]:
                                    out = await ctx.send(f'```py\n{page}\n```')
                                    break
                                await ctx.send(f'```py\n{page}\n```')

                if out:
                    await ctx.message.add_reaction('\u2705')  # tick
                elif err:
                    await ctx.message.add_reaction('\u2049')  # x
                else:
                    await ctx.message.add_reaction('\u2705')
            else:
                await ctx.send(embed=Embed(color=discord.Color.red(), description="You are not the Bot Owner! Shame!"))
        def cleanup_code(content):
            """Automatically removes code blocks from the code."""
            # remove ```py\n```
            if content.startswith('```') and content.endswith('```'):
                return '\n'.join(content.split('\n')[1:-1])

            # remove `foo`
            return content.strip('` \n')

def setup(bot):
    bot.add_cog(essentials(bot))
