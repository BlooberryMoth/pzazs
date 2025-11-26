import discord
from discord.ext import commands
from datetime import datetime as dt
from pytz import timezone as tz
from Global import Permission, Client, none


description = """Checks the latency between the bot and Discord."""
permission = Permission.DIRECT_MESSAGES
aliases = ["ping"]
usage = []


async def handle(message: discord.Message, *_): await ping(await Client.get_context(message))


@Client.hybrid_command()
async def ping(ctx: commands.Context):
    """
    Checks the latency between the bot and Discord.
    
    Parameters
    ----------
    ctx: cmds.Context
        Context
    """
    await ctx.reply(f"Pong! Response in {dt.now(tz('UTC')) - ctx.message.created_at}", allowed_mentions=none, silent=True)