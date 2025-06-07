from Global import *


description = """Checks the latency between the bot and Discord."""
permission = 4
aliases = ['ping']
usage = []


async def handle(message: discord.Message, args: list=None, c: cmds.Context=None):
    if not await check_permission(message, permission, c): raise PermissionError
    
    response = f"Pong! Response in {dt.now(tz('UTC')) - message.created_at}"
    if c: await c.send(response, allowed_mendtions=none, silent=True)
    else: await message.reply(response, allowed_mentions=none, silent=True)


@Client.hybrid_command()
async def ping(ctx: cmds.Context):
    """
    Checks the latency between the bot and Discord.
    
    Parameters
    ----------
    ctx: cmds.Context
        Context
    """
    try: await handle(ctx.message, c=ctx)
    except PermissionError: return