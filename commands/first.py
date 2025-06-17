from Global import *


description = """(Moderator Only) Opens menu for controlling the First game."""
permission = 2
aliases = ['first']
usage = ['start [channel] [timezone] [start date]', 'disabled', 'resync']


async def handle(message: discord.Message, args: list=None, c: cmds.Context=None):
    if not await check_permission(message, permission, c): raise PermissionError

    if len(args):
        if args[0] == "start":
            if not len(args) >= 2: channel = message.channel
            else:
                try:
                    channel = message.guild.get_channel_or_thread(int(args[1].removeprefix('<#').removesuffix('>')))
                    if not channel: raise
                except: return await message.reply(f"> Unable to parse channel from \"{args[1]}\".", silent=True, allowed_mentions=none)
            args += [None, None, None]
            return await _start(await Client.get_context(message), channel, args[2], args[3])

        if args[0] == "disable": return await _disable(await Client.get_context(message))
        if args[0] == "resync": return await _resync(await Client.get_context(message))


@Client.hybrid_group()
async def first(ctx: cmds.Context): ...

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
    if not await check_permission(ctx.message, permission, ctx): return
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
    if not await check_permission(ctx.message, permission, ctx): return
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
    if not await check_permission(ctx.message, permission, ctx): return

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
    today = dt.now(tz(timezone))
    game = {
        "currentWinner":   None,
        "perviousWinner":  None,
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

        if (curr_date - last_date).days > 1: game['perviousWinner'] = game['currentWinner'] = None
        if [curr_date.year, curr_date.month] != [last_date.year, last_date.month]:
            highest_score = max([game['statistics'][userID]['points'] for userID in game['statistics']] + [0])
            last_month_winner = []
            for userID in game['statistics']:
                if game['statistics'][userID]['points'] == highest_score and highest_score:
                    game['statistics'][userID]['wins'] += 1
                    game['lastMonthWinner'] += [int(userID)]
                game['statistics'][userID]['points'] = 0
            game['lastMonthWinner'] = last_month_winner

        game['perviousWinner'] = game['currentWinner']
        game['currentWinner'] = message.author.id
        if game['currentWinner'] == game['perviousWinner']: game['currentStreak'] += 1
        else: game['currentStreak'] = 1

        if message.author.id not in game['statistics']:
            user = {     
                "wins":        0,
                "points":      0,
                "totalPoints": 0,
                "bestStreak":  0,
                "firstPoint":  str(curr_date),
                "lastPoint":   str(curr_date)
            }
        else: user = game['statistics'][message.author.id]

        if message.author.id not in graph: graph[message.author.id] = [[message.id, str(curr_date)]]
        else: graph[message.author.id] += [[message.id, str(curr_date)]]

        user['points'] += 1
        user['totalPoints'] += 1
        user['bestStreak'] = max(user['bestStreak'], game['currentStreak'])

        game['statistics'][message.author.id] = user

        last_date = curr_date

    if today.date() != curr_date:
        game['previousWinner'] = game['currentWinner']
        game['currentWinner'] = None
    if (today.date() - curr_date).days > 1: game['previousWinner'] = None
    if [today.year, today.month] != [curr_date.year, curr_date.month]:
        highest_score = max([game['statistics'][userID]['points'] for userID in game['statistics']] + [0])
        last_month_winner = []
        for userID in game['statistics']:
            if game['statistics'][userID]['points'] == highest_score and highest_score:
                game['statistics'][userID]['wins'] += 1
                game['lastMonthWinner'] += [int(userID)]
            game['statistics'][userID]['points'] = 0
        game['lastMonthWinner'] = last_month_winner
    if rd(today.date().replace(day=1), curr_date.replace(day=1)).months > 1: game['lastMonthWinner'] = []

    with open(f'./games/first/{channel.guild.id}.json', 'w') as file_out: file_out.write(json.dumps(game, indent=4))
    with open(f'./http/res/games/first/{channel.guild.id}.json', 'w') as file_out: file_out.write(json.dumps(graph))