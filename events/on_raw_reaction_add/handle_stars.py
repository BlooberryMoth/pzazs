import discord, json, os, re, requests
from datetime import datetime as dt
from Global import Client, none


async def handle(ctx: discord.RawReactionActionEvent):
    if ctx.emoji.name != '⭐' or not os.path.exists(f'./features/starboards/{ctx.guild_id}.json'): return

    with open(f'./features/starboards/{ctx.guild_id}.json') as file_in: starboard = json.load(file_in)
    if ctx.message_id in starboard['messageCache'] or ctx.channel_id == starboard['channelID']: return

    guild          = Client.get_guild(ctx.guild_id)
    channel        = guild.get_channel(ctx.channel_id)
    message        = await channel.fetch_message(ctx.message_id)
    star_reactions = [_ for _ in message.reactions if _.emoji == '⭐']
    if not len(star_reactions): return

    if star_reactions[0].count >= starboard['minimumReactions']:
        starboard['messageCache'] = starboard['messageCache'][-24:] + [message.id]
        with open(f'./features/starboards/{ctx.guild_id}.json', 'w') as file_out: file_out.write(json.dumps(starboard, indent=4))

        channel = guild.get_channel(starboard['channelID'])
        if not channel: return await message.reply(f"Unable to find/access the Starboard channel!", allowed_mentions=none, silent=True)

        i = 0
        embeds = [discord.Embed(color=0xffac33, url="https://pzazs.thatgalblu.com", description="test") for _ in range(4)]
        embeds[0].description = f"[Jump to message ;](<{message.jump_url}>)"
        embeds[0].timestamp =  dt.now()
        embeds[0].set_author(name=message.author.name, icon_url=message.author.avatar.url or "https://pzazs.thatgalblu.com/api/res/images/404.png")

        if message.reference:
            reply = await message.channel.fetch_message(message.reference.message_id)
            links = [_.group() for _ in re.finditer(r"((h|H)(t|T)(t|T)(p|P))\S*(\s|)", reply.content)]
            if len(links):
                if 'tenor.com/view' in links[0]:
                    r = requests.get(links[0])
                    url = f"https://c.tenor.com/{str(r.content).split('media1.tenor.com/m/')[1].split('/')[0]}/tenor.gif"
                else: url = links[0]
                embeds[0].set_thumbnail(url=url)
                reply.content = "\n".join(reply.content.split(links[-1]))
            embeds[0].add_field(name=f"Replying to __@**{reply.author.global_name}**__:", value=reply.content, inline=False)
            if len(reply.attachments) and not embeds[0].thumbnail.url: embeds[0].set_thumbnail(url=reply.attachments[0].url)
            if len(reply.stickers) and not embeds[0].thumbnail.url: embeds[0].set_thumbnail(url=reply.stickers[0].url)

        for attachment in message.attachments:
            if i >= 4: break
            if 'video' in attachment.content_type: i -= 1
            else: embeds[i].set_image(url=attachment.url)
            i += 1

        links = [_.group() for _ in re.finditer(r"((h|H)(t|T)(t|T)(p|P))\S*(\s|)", message.content)]
        for link in links[:4]:
            if i >= 4: break
            if 'tenor.com/view' in link:
                r = requests.get(link)
                url = f"https://c.tenor.com/{str(r.content).split('media1.tenor.com/m/')[1].split('/')[0]}/tenor.gif"
            else: url = link
            embeds[i].set_image(url=url)
            i += 1
            message.content = "\n".join(message.content.split(link))
        embeds[0].add_field(name=f"__@**{message.author.global_name}**__:", value=message.content, inline=False)

        if True in ['video' in attachment.content_type for attachment in message.attachments]: embeds[0].description += " (video attachment(s))"
        if i >= 4 and False in ['video' in attachment.content_type for attachment in message.attachments]: embeds[0].description += " (+ more attachment(s))" 
        
        for sticker in message.stickers:
            if i >= 4:
                embeds[0].description += "(+ stickers)"
                break
            embeds[i].set_image(url=sticker.url)
            i += 1
        
        await channel.send(content='', embeds=embeds)