import importlib, logging, os
from Global import LOGGER, Client, command_aliases, token

# ////.:•,,•:.\\\\ -"yummy bugs"

if __name__== '__main__':
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
            command_aliases[file] = {'aliases': module.aliases, 'module': module}
    LOGGER.info("Loaded commands.")

    if not os.path.exists('./events'): os.mkdir("./events")
    for folder in os.listdir('./events'):
        for file in os.listdir(f'./events/{folder}'):
            if file.startswith('@') and file.endswith('py'): module = importlib.import_module(f'events.{folder}.{file.removesuffix(".py")}')
    LOGGER.info("Loaded events.")

    if not os.path.exists('./starboards'):  os.mkdir("./starboards")
    if not os.path.exists('./reactions'):   os.mkdir("./reactions")
    if not os.path.exists('./games'):       os.mkdir("./games")
    if not os.path.exists('./games/first'): os.mkdir("./games/first")

    Client.run(token=token) # The rest of intialization happens in ./events/on_ready/@on_ready.py -> ./events/on_ready/startup.py
    LOGGER.info(f"Closing client \"{Client.user}\".")