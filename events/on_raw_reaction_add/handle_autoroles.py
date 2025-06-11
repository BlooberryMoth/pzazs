from Global import *


async def handle(ctx: discord.RawReactionActionEvent):
    try:
        with open(f'./autoroles/{ctx.guild_id}.json') as file_in: messages = json.load(file_in); assert isinstance(messages, list)
        message = [message for message in messages if message['messageID'] == ctx.message_id][0]
    except: return


    try:
        roleID = [role['roleID'] for role in message['roles'] if (role['emojiID'] and role['emojiID'] == ctx.emoji.id) or role['emoji'] == ctx.emoji.name][0]
    except: return
    guild = Client.get_guild(ctx.guild_id)
    role = guild.get_role(roleID)
    if not role: return

    if ctx.member.get_role(roleID): await ctx.member.remove_roles(role)
    else: await ctx.member.add_roles(role)

    real_message = guild.get_channel(message['channelID']).get_partial_message(message['messageID'])
    await real_message.remove_reaction(ctx.emoji, ctx.member)