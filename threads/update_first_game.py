import json, os, time
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from pytz import timezone as tz
from Global import Client
from Logging import LOG


def execute():
    while True:
        now = dt.now()
        then = now.replace(minute=now.minute-now.minute%15, second=0, microsecond=0) + rd(minutes=15)
        till = then - now
        time.sleep(float(f'{till.seconds}.{till.microseconds}'))

        for file in os.listdir('./games/first'):
            if file.endswith('.json') and not file.endswith('_graph.json'):
                with open(f'./games/first/{file}') as file_in: game = json.load(file_in)
                now_en_loc = then.astimezone(tz(game['timezone']))
                if now_en_loc.hour or now_en_loc.minute: continue
                game['previousWinner'] = game['currentWinner']
                game['currentWinner'] = None
                with open(f'./games/first/{file}', 'w') as file_out: file_out.write(json.dumps(game, indent=4))

                if now_en_loc.day == 1:
                    highest_score = max([game['statistics'][userID]['points'] for userID in game['statistics']] + [0])
                    last_month_winner = []
                    for userID in game['statistics']:
                        if highest_score and game['statistics'][userID]['points'] == highest_score:
                            game['statistics'][userID]['wins'] += 1
                            last_month_winner += [int(userID)]
                        game['statistics'][userID]['points'] = 0
                    game['lastMonthWinner'] = last_month_winner
                
                with open(f'./games/first/{file}', 'w') as file_out: file_out.write(json.dumps(game, indent=4))
                file_out.close()
                LOG.info(f"Next round of First started for {Client.get_guild(int(file.removesuffix('.json'))).name}")