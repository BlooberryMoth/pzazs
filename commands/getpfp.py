import discord
from discord.ext import commands
from Global import Permission, Client, none


description = """Gets info about user. Defaults to you if no one is specified"""
permission = Permission.DIRECT_MESSAGES
aliases = ['getpfp', 'pfp']
usage = ['[@user]']


async def handle(message: discord.Message, *_):
    try: user = message.mentions[0]
    except: user = message.author
    await getpfp(await Client.get_context(message), user)


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
    if not await Permission.check(ctx, permission): raise PermissionError

    if not user: user = ctx.author
    await ctx.reply(user.avatar.url, allowed_mentions=none, silent=True)