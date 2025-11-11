import time
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from Global import Client
from website import HTTPHandler


def execute():
    while True:
        HTTPHandler.server_count = len(Client.guilds)
        users = []
        for guild in Client.guilds:
            for user in guild.members:
                if user.id in users: continue
                users.append(user.id)
        HTTPHandler.user_count = len(users)

        then = dt.now().replace(hour=0, minute=0, second=0, microsecond=0) + rd(days=1)
        till = (then - dt.now())
        time.sleep(float(f'{till.seconds}.{till.microseconds}'))