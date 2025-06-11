from Global import *


async def handle(message: discord.Message):
    if 'first' not in message.content.lower() or not os.path.exists(f'./games/first/{message.guild.id}.json'): return

    with open(f'./games/first/{message.guild.id}.json') as file_in: game = json.load(file_in)
    if message.channel.id != game['channelID'] or game['currentWinner']: return
    game['currentWinner'] = message.author.id
    with open(f'./games/first/{message.guild.id}.json') as file_out: file_out.write(json.dumps(game, indent=4))

    if game['currentWinner'] == game['previousWinner']: game['currentStreak'] += 1
    else: game['currentStreak'] = 1

    today = dt.now(tz(game['timezone']))
    if str(message.author.id) not in game['statistics']:
        user = {
            "wins":        0,
            "points":      0,
            "totalPoints": 0,
            "bestStreak":  0,
            "firstPoint":  str(today.date()),
            "lastPoint":   str(today.date())
        }
    else: user = game['statistics'][message.author.id]

    user['points'] += 1
    user['totalPoints'] += 1
    user['bestStreak'] = max(user['bestStreak'], game['currentStreak'])
    user['lastPoint'] = str(today.date())

    game['statistics'][message.author.id] = user

    midnight = dt.now(tz(game['timezone'])).replace(hour=0, minute=0, second=0, microsecond=0)
    await message.reply(f"And today's winner... <@{message.author.id}>!! (exactly {today - midnight} after midnight).", allowed_mentions=none)

    with open(f'./games/first/{message.guild.id}.json') as file_out: file_out.write(json.dumps(game, indent=4))