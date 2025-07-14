import discord
from Global import PREFIX, Commands


async def handle(message: discord.Message):
    if message.content.startswith(PREFIX):
        alias, *args = message.content.lower().removeprefix(PREFIX).split(' ')
        for command in Commands:
            if alias in Commands[command]['aliases']:
                try: await Commands[command]['module'].handle(message, args)
                except PermissionError: return