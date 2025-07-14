import discord, json, os
from Global import Client


async def handle(message: discord.Message):
    author = message.author
    if not os.path.exists(f'./reactions/{author.id}.json'): return
    with open(f'./reactions/{author.id}.json') as file_in: reactions = json.load(file_in)

    for react in reactions:
        if True in [_ in message.content.lower() for _ in react['message']['contains']] \
        and not True in [_ in message.content.lower() for _ in react['message']['excludes']] \
        or message.content.lower() in react['message']['isExactly']:
            try:
                emoji = Client.get_emoji(react['emojiID'])
                emoji.id
            except: emoji = react['emoji']
            await message.add_reaction(emoji)