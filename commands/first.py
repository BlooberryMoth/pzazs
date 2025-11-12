import discord, io, json, os, requests
from discord.ext import commands as cmds
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from pytz import timezone as tz
from PIL import Image, ImageDraw, ImageOps
from Global import Permission, Font, Client, none


description = """(Moderator Only) Opens menu for controlling the First game. | (All Users) Show rank for you or another user in the First game."""
permission = Permission.USER
aliases = ['first']
usage = ['rank [@user]', '(MOD) start [#channel] [timezone] [start date]', '(MOD) disable', '(MOD) resync']


async def handle(message: discord.Message, args: list=None, c: cmds.Context=None):
    if not await Permission.check(message, permission, c): raise PermissionError

    if len(args):
        match args[0]:
            case "rank":
                try: user = message.mentions[0]
                except: user = message.author
                return await _rank(await Client.get_context(message), user)
            case "start":
                if not await Permission.check(message, Permission.MODERATOR, c): raise PermissionError
                if not len(args) >= 2: channel = message.channel
                else:
                    try:
                        channel = message.guild.get_channel_or_thread(int(args[1].removeprefix('<#').removesuffix('>')))
                        if not channel: raise
                    except: return await message.reply(f"> Unable to parse channel from \"{args[1]}\".", silent=True, allowed_mentions=none)
                args += [None, None, None]
                return await _start(await Client.get_context(message), channel, args[2], args[3])
            case "disable": return await _disable(await Client.get_context(message))
            case "resync": return await _resync(await Client.get_context(message))


@Client.hybrid_group()
async def first(ctx: cmds.Context): ...


@first.command(name="rank")
async def _rank(ctx: cmds.Context, user: discord.User=None):
    """
    Show rank for you or another user in the First game.

    Parameters
    ----------
    ctx: cmds.Context
        Context
    user: discord.User
        User
    """
    if not await Permission.check(ctx.message, permission, ctx): return

    try:
        with open(f"./games/first/{ctx.guild.id}.json") as file_in: game = json.load(file_in)
    except: return await ctx.reply("> The First game isn't even enabled here!", ephemeral=True)
    if not user:
        user = ctx.author
        if str(user.id) not in game['statistics']: return await ctx.reply("You haven't placed yet! Try winning a round *first*. verbal wink", silent=True, allowed_mentions=none)
    else:
        if str(user.id) not in game['statistics']: return await ctx.reply(f"<@{user.id}> hasn't place in this server's First game!", silent=True, allowed_mentions=none)

    response = await ctx.reply("> Loading...", silent=True, allowed_mentions=none)

    # Stream in the image data of the user's icon via requests and BytesIO, resize, and trim border into a circle.
    session = requests.session()
    try: icon = Image.open(io.BytesIO(session.get(user.avatar.url, stream=True).content))
    except: icon = Image.open("./http/res/images/404.png")
    icon = icon.convert("RGBA").resize((232,232))
    mask = Image.new("L", (232,232)); mask_draw = ImageDraw.Draw(mask)
    mask_draw.circle(xy=(116,116), radius=116, fill=255)
    icon.putalpha(mask)

    # Gather strings for drawing.
    wins             = str(game['statistics'][str(user.id)]['wins'])
    points           = str(game['statistics'][str(user.id)]['points'])
    total_points     = str(game['statistics'][str(user.id)]['totalPoints'])
    best_streak      = str(game['statistics'][str(user.id)]['bestStreak'])
    first_point      =     game['statistics'][str(user.id)]['firstPoint']
    last_point       =     game['statistics'][str(user.id)]['lastPoint']
    last_win_message = f"\"{game['statistics'][str(user.id)]['lastWinMessage']}\""

    # Sort players to find the rank of the selected user.
    sorted_stats = dict(sorted(game['statistics'].items(), key=lambda x: (x[1]['wins'], x[1]['totalPoints']), reverse=True))
    place = f"#{[_ for _ in sorted_stats].index(str(user.id)) + 1}"

    # Open the base card.
    card = Image.open("./games/first/resources/user_card.png").convert("RGBA"); draw = ImageDraw.Draw(card)
    card.paste(icon, (29,29, 29+232,29+232), icon) # Put player's icon.
    _, _, w, h = draw.textbbox((0,0), text=place, font=Font.dm_sans_24) # Used to center the text of the placement (#1 or #28).
    draw.text(text=place,        xy=(262+34-(w/2), 20), fill=Font.white, font=Font.dm_sans_24) # Center placement text with X + dX/2 - w/2, where dX is the width of the container you center inside of.
    draw.text(text=user.name,    xy=(352, 19),          fill=Font.white, font=Font.dm_sans_24)
    draw.text(text=points,       xy=(640, 80),          fill=Font.white, font=Font.dm_sans_24)
    draw.text(text=wins,         xy=(561, 132),         fill=Font.white, font=Font.dm_sans_24)
    draw.text(text=total_points, xy=(555, 183),         fill=Font.white, font=Font.dm_sans_24)
    draw.text(text=best_streak,  xy=(549, 235),         fill=Font.white, font=Font.dm_sans_24)
    draw.text(text=first_point,  xy=(531, 287),         fill=Font.white, font=Font.dm_sans_24)
    draw.text(text=last_point,   xy=(528, 338),         fill=Font.white, font=Font.dm_sans_24)
    _, _, w, h = draw.textbbox((0,0), text=last_win_message, font=Font.dm_sans_24)
    draw.text(text=last_win_message, xy=(39+(212/2)-(w/4), 311+(70/2)-(h/3)), fill=Font.white, font=Font.gg_sans_14)


    with io.BytesIO() as bytesIO:
        card.save(bytesIO, 'PNG')
        bytesIO.seek(0)
        await response.edit(content='', attachments=[discord.File(bytesIO, filename='card.png')], allowed_mentions=none)


@first.command(name="start")
async def _start(ctx: cmds.Context,
                 channel: discord.TextChannel=None,
                 timezone: str=None,
                 start_date: str=None):
    """
    (Moderator Only) Used to start/reset the First game for the server.
    
    Parameters
    ----------
    ctx: cmds.Context
        Context
    channel: discord.TextChannel=None
        The channel used for playing, usually the "general" channel. Defaults to current channel.
    timezone: str=None
        The timezone used for when each round starts. Defaults to UTC.
    start_date: str=None
        'all' | YYYY-mm-dd -|- Starting date used to gather messages if you've already played before. Defaults to midnight, today.
    """
    if not await Permission.check(ctx.message, Permission.MODERATOR, ctx): return
    if not channel:  channel  = ctx.channel
    if not timezone: timezone = "UTC"
    else:
        try: tz(timezone)
        except: return await ctx.send(f"> Unable to parse time zone \"{timezone}\".\n> Use any timezone from [This List](<https://wikipedia.org.wiki.List_of_tz_database_time_zones>) under 'TZ Identifier'", ephemeral=True)
    if not start_date: start_date = dt.now(tz(timezone)).replace(hour=0, minute=0, second=0, microsecond=0)
    elif start_date == "all": start_date = ctx.guild.created_at.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        try: start_date = dt.strptime(start_date, '%Y-%m-%d')
        except: return await ctx.send(f"> Unable to parse starting date \"{start_date}\". Please make sure to format as YYYY-mm-dd", ephemeral=True)

    response = await ctx.send(f"> Building First game statistics from {start_date.date()}. This may take awhile...", silent=True)
    then = dt.now()
    async with ctx.channel.typing(): await build_statistics(channel, timezone, start_date)
    await response.edit(content=f"> Finished building statistics in {dt.now() - then}")


@first.command(name="disable")
async def _disable(ctx: cmds.Context):
    """
    (Moderator Only) Used to disabled the First game, removing all points from everyone in the server.
    
    Parameters
    ----------
    ctx: cmds.Context
        Context
    """
    if not await Permission.check(ctx.message, Permission.MODERATOR, ctx): return
    if not os.path.exists(f'./games/first/{ctx.guild.id}.json'): return await ctx.send("> The First game isn't even enabled here!", ephemeral=True)

    os.remove(f'./games/first/{ctx.guild.id}.json')
    await ctx.send(f"> Disabled First game for {ctx.guild.name}.", silent=True)


@first.command(name="resync")
async def _resync(ctx: cmds.Context):
    """
    (Moderator Only) Used to resync the messages for the First game. This can take a long time...
    
    Parameters
    ----------
    ctx: cmds.Context
        Context
    """
    if not await Permission.check(ctx.message, Permission.MODERATOR, ctx): return

    try:
        with open(f'./games/first/{ctx.guild.id}.json') as file_in: game = json.load(file_in)
    except: return await ctx.send("> The First game isn't even enabled here!", ephemeral=True)

    channel = ctx.guild.get_channel_or_thread(game['channelID'])
    if not channel: return await ctx.send(f"> Unable to find/access channel <#{game['channelID']}>, If may have been deleted.", ephemeral=True)
    timezone = game['timezone']
    start_date = dt.strptime(game['startDate'], '%Y-%m-%d')

    reply = await ctx.send(f"> Rebuilding First game statistics from {start_date.date()}. This may take awhile...", silent=True)
    then = dt.now()
    async with ctx.channel.typing(): await build_statistics(channel, timezone, start_date)
    await reply.edit(content=f"> Finished rebuilding statistics in in {dt.now() - then}")


async def build_statistics(channel: discord.TextChannel, timezone: str, start_date: dt) -> None:
    today = dt.now(tz(timezone)).date()
    game = {
        "currentWinner":   None,
        "previousWinner":  None,
        "currentStreak":   0,
        "lastMonthWinner": [],
        "channelID":       channel.id,
        "timezone":        timezone,
        "startDate":       str(start_date.date()),
        "statistics":      {}
    }

    graph = {}

    curr_date = last_date = start_date.date()
    async for message in channel.history(limit=None, after=start_date, oldest_first=True):
        if message.author.bot: continue
        curr_date = message.created_at.astimezone(tz(timezone)).date()
        if curr_date == last_date or 'first' not in message.content.lower(): continue
        if 'first' not in message.content.lower(): continue

        if (curr_date - last_date).days > 1: game['previousWinner'] = game['currentWinner'] = None
        if [curr_date.year, curr_date.month] != [last_date.year, last_date.month]:
            highest_score = max([game['statistics'][user_ID]['points'] for user_ID in game['statistics']] + [0])
            last_month_winner = []
            for user_ID in game['statistics']:
                if game['statistics'][user_ID]['points'] == highest_score and highest_score:
                    game['statistics'][user_ID]['wins'] += 1
                    last_month_winner += [int(user_ID)]
                game['statistics'][user_ID]['points'] = 0
            game['lastMonthWinner'] = last_month_winner

        game['previousWinner'] = game['currentWinner']
        game['currentWinner'] = message.author.id
        if game['currentWinner'] == game['previousWinner']: game['currentStreak'] += 1
        else: game['currentStreak'] = 1

        if str(message.author.id) not in game['statistics']:
            user = {     
                "wins":           0,
                "points":         0,
                "totalPoints":    0,
                "bestStreak":     0,
                "firstPoint":     str(curr_date),
                "lastPoint":      str(curr_date),
                "lastWinMessage": "",
                "streakBrokenBy": 0
            }
        else: user = game['statistics'][str(message.author.id)]

        if str(message.author.id) not in graph: graph[str(message.author.id)] = [[message.id, str(curr_date)]]
        else: graph[str(message.author.id)] += [[message.id, str(curr_date)]]

        user['points']        += 1
        user['totalPoints']   += 1
        user['bestStreak']     = max(user['bestStreak'], game['currentStreak'])
        user['lastPoint']      = str(curr_date)
        user['lastWinMessage'] = message.clean_content

        game['statistics'][str(message.author.id)] = user

        last_date = curr_date

    if today != curr_date:
        game['previousWinner'] = game['currentWinner']
        game['currentWinner'] = None
    if (today - curr_date).days > 1: game['previousWinner'] = None
    if [today.year, today.month] != [curr_date.year, curr_date.month]:
        highest_score = max([game['statistics'][user_ID]['points'] for user_ID in game['statistics']] + [0])
        last_month_winner = []
        for user_ID in game['statistics']:
            if game['statistics'][user_ID]['points'] == highest_score and highest_score:
                game['statistics'][user_ID]['wins'] += 1
                last_month_winner += [int(user_ID)]
            game['statistics'][user_ID]['points'] = 0
        game['lastMonthWinner'] = last_month_winner
    if rd(today.replace(day=1), curr_date.replace(day=1)).months > 1: game['lastMonthWinner'] = []

    with open(f'./games/first/{channel.guild.id}.json', 'w') as file_out: file_out.write(json.dumps(game, indent=4))
    with open(f'./games/first/{channel.guild.id}_graph.json', 'w') as file_out: file_out.write(json.dumps(graph))