import discord, json, os
from discord.ext import commands as cmds
from Global import check_permission, reply, Client, none


description = """(Moderator Only) Enables or disables the Starboard."""
permission = 2
aliases = ['starboard']
usage = ['enable <channel> [minimum_stars]', 'disable']


async def handle(message: discord.Message, args: list=None, ctx: cmds.Context=None):
    if not await check_permission(message, permission, ctx): raise PermissionError

    if len(args):
        if args[0] == "enable":
            if not len(args) >= 2: return await message.reply (f"> You need to specify a channel for Stars to be posted to.", silent=True, allowed_mentions=none)
            else:
                try:
                    channel = message.guild.get_channel_or_thread(int(args[1].removeprefix('<#').removesuffix('>')))
                    if not channel: raise
                except: return await message.reply(f"> Unable to parse channel from \"{args[1]}\".", silent=True, allowed_mentions=none)
            args += [None]
            return await _enable(await Client.get_context(message), channel, args[2])
        
        if args[0] == "disable": return await _disable(await Client.get_context(message))


@Client.hybrid_group()
async def starboard(ctx: cmds.Context): ...

@starboard.command(name="enable")
async def _enable(ctx: cmds.Context, channel: discord.TextChannel, minimum_stars: int=3) -> None:
    """
    (Moderator Only) Enables or disables the Starboard.
    
    Parameters
    ----------
    ctx: cmds.Context
        Context
    channel: discord.TextChannel
        The channel used to post the Stars.
    minimum_stars: int=3
        Minimum number of reactions needed for a Star to be posted.
    """
    if not await check_permission(ctx.message, permission, ctx): return
    if not channel: return await ctx.send(f"> You need to specify a channel for Stars to be posted to.", ephemeral=True)
    if not minimum_stars: minimum_stars = 3

    if os.path.exists(f'./starboards/{ctx.guild.id}.json'):
        with open(f'./starboards/{ctx.guild.id}.json') as file_in: board = json.load(file_in)
    else: board = { "messageCache": [] }

    board['channelID'] = channel.id
    board['minimumReacts'] = minimum_stars
    
    with open(f'./starboards/{ctx.guild.id}.json', 'w') as file_out: file_out.write(json.dumps(board, indent=4))
    await ctx.send(f"Enabled Starboard for {ctx.guild.name} in <#{channel.id}>", silent=True)


@starboard.command(name="disable")
async def _disable(ctx: cmds.Context) -> None:
    """(Moderator Only) Disables the Starboard for the server."""
    if not await check_permission(ctx.message, permission, ctx): return

    if not os.path.exists(f'./starboards/{ctx.guild.id}.json'): return await ctx.send(f"Starboard isn't even enabled here!", ephemeral=True)

    os.remove(f'./starboards/{ctx.guild.id}.json')
    await ctx.send(f"Disabled Starboard for {ctx.guild.name}.", silent=True)