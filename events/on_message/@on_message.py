import discord, importlib, os
from Global import Client, LOGGER


@Client.event
async def on_message(message: discord.Message):
    if message.author.bot: return

    for file in os.listdir('./events/on_message'):
        if not file.startswith('@') and file.endswith('.py'):
            module = importlib.import_module(f'events.on_message.{file.split(".py")[0]}')
            try: await module.handle(message)
            except Exception as e: LOGGER.error(e)