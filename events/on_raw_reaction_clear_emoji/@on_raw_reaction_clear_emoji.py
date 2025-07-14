import discord, importlib, os
from Global import Client


@Client.event
async def on_raw_reaction_clear_emoji(ctx: discord.RawReactionActionEvent):
    for file in os.listdir('./events/on_raw_reaction_clear_emoji'):
        if not file.startswith('@') and file.endswith('.py'):
            module = importlib.import_module(f'events.on_raw_reaction_clear_emoji.{file.split(".py")[0]}')
            await module.handle(ctx)