from Global import Client, discord, importlib, os


@Client.event
async def on_raw_reaction_add(ctx: discord.RawReactionActionEvent):
    if ctx.member.bot: return

    for file in os.listdir('./events/on_raw_reaction_add'):
        if not file.startswith('@') and file.endswith('.py'):
            module = importlib.import_module(f'events.on_raw_reaction_add.{file.split(".py")[0]}')
            await module.handle(ctx)