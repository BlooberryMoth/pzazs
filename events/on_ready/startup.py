from Global import dt, os, LOGGER, Client, Threads

async def handle():
    await Client.tree.sync()
    LOGGER.info(f"Logged in as {Client.user}.")

    # The threads are opened here as some of the data used in ./threads/http.py -> ./APIServer.py, and ./threads/update_api.py
    # is only accessable after the Client has full initialized.
    LOGGER.info("Opening threads...")
    now = dt.now()
    if not os.path.exists('./threads'): os.mkdir("./threads")
    for file in os.listdir('./threads'):
        if file.endswith('.py'):
            module = dt.import_module(f'threads.{file.removesuffix(".py")}')
            try: thread = dt.Thread(target=module.execute, args=())
            except Exception as e: LOGGER.error(e)
            else:
                Threads.append(thread)
                thread.start()
    LOGGER.info(f"Threads opened in {dt.now() - now}.")