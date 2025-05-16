from Global import *


async def handle(ctx: discord.RawReactionActionEvent):
    if ctx.emoji.name != '⭐' or str(ctx.guild_id) not in starboards: return

    guild         = Client.get_guild(ctx.guild_id)
    channel       = guild.get_channel(ctx.channel_id)
    message       = await channel.fetch_message(ctx.message_id)
    starboard     = starboards[str(guild.id)]
    starReactions = [_ for _ in message.reactions if _.emoji == '⭐']
    if channel.id == starboard['channelID'] or not len(starReactions): return

    if starReactions[0].count == starboard['minimumReactions']:
        try: channel = guild.get_channel(starboard['channelID'])
        except: return await message.reply(f"Unable to find/access the Starboard channel!", allowed_mentions=none, silent=True)

        embeds = []
        embed = discord.Embed(color=0xffac33,
                              timestamp=dt.now(),
                              description=f"[Jump to message ;](<{message.jump_url}>)",
                              url="https://pzazs.thatgalblu.com") \
        .set_author(name=message.author.name, icon_url=message.author.avatar.url or "https://pzazs.thatgalblu.com/api/res/images/404.png")

        if message.reference:
            reply = await message.channel.fetch_message(message.reference.message_id)
            embed.add_field(name=f"Replying to __{reply.author.name}__:", value=reply.content, inline=False)

        if message.content: embed.add_field(name=f"__{message.author.name}__:", value=f"{message.content}")

        if len(message.attachments):
            i = 0
            for attachment in message.attachments:
                if i > 4: break
                if 'video' in attachment.content_type: i -= 1
                else: embed.set_image(url=attachment.url)
                embeds.append(embed)
                embed = discord.Embed(url="https://pzazs.thatgalblu.com")
                i += 1
        else: embeds.append(embed)

        if True in ['video' in attachment.content_type for attachment in message.attachments]:
            embed.description += " (video attachment(s))"
            if False in ['video' in attachment.content_type for attachment in message.attachments]: embed.description += " (+ more attachment(s))" 
        
        if len(message.stickers):
            if len(embeds) < 4: embeds.append(discord.Embed(url="https://pzazs.thatgalblu.com").set_image(url=message.stickers[0].url))
            else: embed.add_field(name="Sticker", value="")
        
        await channel.send(content='', embeds=embeds)