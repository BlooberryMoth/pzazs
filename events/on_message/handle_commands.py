from Global import *


async def handle(message: discord.Message):
    if message.content.startswith(prefix):
        alias, *args = message.content.removeprefix(prefix).split(' ')
        for command in commands:
            if alias in commands[command]['aliases']:
                try: await commands[command]['module'].handle(message, args)
                except PermissionError: return