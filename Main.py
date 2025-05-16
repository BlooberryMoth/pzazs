from Global import *

# ////.:•,,•:.\\\\ -"yummy bugs"

if __name__== '__main__':
    if not os.path.exists('./commands'): os.mkdir("./commands")
    for file in os.listdir('./commands'):
        if file.endswith('.py'):
            file = file.split('.py')[0]
            module = importlib.import_module(f'commands.{file}')
            commands[file] = {'aliases': module.aliases, 'module': module}
    log("Commands loaded.")

    if not os.path.exists('./events'): os.mkdir("./events")
    for folder in os.listdir('./events'):
        for file in os.listdir(f'./events/{folder}'):
            if file.startswith('@') and file.endswith('py'): module = importlib.import_module(f'events.{folder}.{file.removesuffix(".py")}')
    log("Events loaded.")

    if not os.path.exists('./starboards'): os.mkdir("./starboards")
    for file in os.listdir('./starboards'):
        if file.endswith('.json'):
            with open(f'./starboards/{file}') as fileIn: starboards[file.removesuffix('.json')] = json.load(fileIn)
    log("Starboards loaded.")

    if not os.path.exists('./reactions'): os.mkdir("./reactions")

    Client.run(token=token)
    log(f"Closing client \"{Client.user}\".")