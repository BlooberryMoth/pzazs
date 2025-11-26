import importlib, os
from Global import Client, command_aliases, TOKEN
from Logging import LOG

# ////.:•,,•:.\\\\ - "yummy bugs"

if __name__== "__main__":
    # These "imports" load the file and activate the @Client.hybrid_command decorated methods,
    # as well as loading all of the commands' aliases into memory for faster access. 
    # The same happens with the events below, which loads the @Client.event decorations.
    # 
    # This allows all the command and event files to be seperated from Main.py/Global.py for extreme levels of abstraction. 
    if not os.path.exists('./commands'): os.mkdir("./commands")
    for file in os.listdir('./commands'):
        if file.endswith('.py'):
            file = file.split('.py')[0]
            module = importlib.import_module(f'commands.{file}')
            command_aliases[file] = { "aliases": module.aliases, "module": module }
    LOG.info("Loaded commands.")

    if not os.path.exists('./events'): os.mkdir("./events")
    for folder in os.listdir('./events'):
        for file in os.listdir(f'./events/{folder}'):
            if file.startswith('@') and file.endswith('py'): module = importlib.import_module(f'events.{folder}.{file.removesuffix(".py")}')
    LOG.info("Loaded events.")

    if not os.path.exists('./features'):             os.mkdir("./features")
    if not os.path.exists('./features/autoroles'):   os.mkdir("./features/autoroles")
    if not os.path.exists('./features/starboards'):  os.mkdir("./features/starboards")
    if not os.path.exists('./features/reactions'):   os.mkdir("./features/reactions")
    if not os.path.exists('./features/games'):       os.mkdir("./features/games")
    if not os.path.exists('./features/games/first'): os.mkdir("./features/games/first")

    Client.run(token=TOKEN) # The rest of intialization happens in ./events/on_ready/@on_ready.py -> ./events/on_ready/startup.py
    LOG.info(f"Closing client \"{Client.user}\".")