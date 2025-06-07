from Global import Client, discord, importlib, os


@Client.event
async def on_raw_reaction_clear(ctx: discord.RawReactionClearEvent):
    for file in os.listdir('./events/on_raw_reaction_clear'):
        if not file.startswith('@') and file.endswith('.py'):
            module = importlib.import_module(f'events.on_raw_reaction_clear.{file.split(".py")[0]}')
            await module.handle(ctx)