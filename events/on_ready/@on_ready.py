from Global import importlib, os, Client


@Client.event
async def on_ready():
    for file in os.listdir('./events/on_ready'):
        if not file.startswith('@') and file.endswith('.py'):
            module = importlib.import_module(f'events.on_ready.{file.split(".py")[0]}')
            await module.handle()