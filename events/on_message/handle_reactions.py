import discord, json, os
from Global import Client


async def handle(message: discord.Message):
    author = message.author
    if not os.path.exists(f'./features/reactions/{author.id}.json'): return
    with open(f'./features/reactions/{author.id}.json') as file_in: reactions = json.load(file_in)

    for react in reactions:
        if (
            message.guild.id in react['requirements']['guilds'] \
            or not len(react['requirements']['guilds'])
        ) \
        and (
            True in         [_ in message.content.lower() for _ in react['requirements']['message']['contains']]
            and not True in [_ in message.content.lower() for _ in react['requirements']['message']['excludes']]
            or message.content.lower() in react['requirements']['message']['isExactly']
        ):
            try:
                emoji = Client.get_emoji(react['emojiID'])
                emoji.id
            except: emoji = react['emoji']
            await message.add_reaction(emoji)