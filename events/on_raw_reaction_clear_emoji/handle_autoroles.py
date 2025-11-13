import discord, json
from Global import Client


async def handle(ctx: discord.RawReactionClearEmojiEvent):
    try:
        with open(f'./features/autoroles/{ctx.guild_id}.json') as file_in: messages = json.load(file_in); assert isinstance(messages, list)
        message = [message for message in messages if message['messageID'] == ctx.message_id][0]
    except: return

    guild = Client.get_guild(ctx.guild_id)
    real_message = guild.get_channel(message['channelID']).get_partial_message(message['messageID'])
    if ctx.emoji in [_['emoji'] for _ in message['roles']] or ctx.emoji.id in [_['emojiID'] for _ in message['roles']]: await real_message.clear_reactions()