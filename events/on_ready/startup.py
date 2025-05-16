from Global import *

async def handle():
    await Client.tree.sync()

    log(f"Logged in as {Client.user}.")

    log("Opening threads...")
    now = dt.now()
    if not os.path.exists('./threads'): os.mkdir("./threads")
    for file in os.listdir('./threads'):
        if file.endswith('.py'):
            module = importlib.import_module(f'threads.{file.removesuffix(".py")}')
            thread = threading.Thread(target=module.execute, args=())
            threads.append(thread)
            thread.start()
    log(f"Threads opened in {dt.now() - now}.")