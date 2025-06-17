import APIServer, time
from Global import Client, dt, rd


def execute():
    while True:
        APIServer.server_count = len(Client.guilds)
        users = []
        for guild in Client.guilds:
            for user in guild.members:
                if user.id in users: continue
                users.append(user.id)
        APIServer.user_count = len(users)

        then = dt.now().replace(hour=0, minute=0, second=0, microsecond=0) + rd(days=1)
        till = (then - dt.now())
        time.sleep(float(f'{till.seconds}.{till.microseconds}'))