import discord
from Global import PREFIX, command_aliases


async def handle(message: discord.Message):
    if message.content.startswith(PREFIX):
        alias, *args = message.content.lower().removeprefix(PREFIX).split(' ')
        for command in command_aliases:
            if alias in command_aliases[command]['aliases']:
                try: await command_aliases[command]['module'].handle(message, args)
                except PermissionError: return