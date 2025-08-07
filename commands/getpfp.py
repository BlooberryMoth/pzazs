import discord
from discord.ext import commands
from Global import Permission, Client, none


description = """Gets info about user. Defaults to you if no one is specified"""
permission = Permission.DIRECT_MESSAGES
aliases = ['getpfp', 'pfp']
usage = ['getpfp [@user]']


async def handle(message: discord.Message, args: list=None, c: commands.Context=None, user: discord.User=None):
    if not await Permission.check(message, permission, c): raise PermissionError

    if c:
        if not user: await c.send(c.author.avatar.url, allowed_mentions=none, silent=True)
        else: await c.send(user.avatar.url, allowed_mentions=none, silent=True)
    else:
        try: user = message.mentions[0]
        except: user = message.author
        await message.reply(user.avatar.url, allowed_mentions=none, silent=True)


@Client.hybrid_command()
async def getpfp(ctx: commands.Context, user: discord.User=None):
    """
    Gets info about user. Defaults to you if no one is specified.

    Parameters
    ----------
    ctx: cmds.Context
        Context
    user: discord.User
        User
    """
    try: await handle(ctx.message, c=ctx, user=user)
    except PermissionError: return