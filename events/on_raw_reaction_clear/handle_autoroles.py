from Global import *


async def handle(ctx: discord.RawReactionClearEvent):
    try:
        with open(f'./autoroles/{ctx.guild_id}.json') as fileIn: messages = json.load(fileIn); assert isinstance(messages, list)
        message = [message for message in messages if message['messageID'] == ctx.message_id][0]
    except: return

    guild = Client.get_guild(ctx.guild_id)
    real_message = guild.get_channel(message['channelID']).get_partial_message(message['messageID'])
    for role in message['roles']:
        try:
            emoji = Client.get_emoji(role['emojiID'])
            if not emoji: raise
        except: emoji = role['emoji']

        await real_message.add_reaction(emoji)