from Global import *
import requests, re


async def handle(ctx: discord.RawReactionActionEvent):
    if ctx.emoji.name != '⭐' or not os.path.exists(f'./starboards/{ctx.guild_id}.json'): return

    with open(f'./starboards/{ctx.guild_id}.json') as file_in: starboard = json.load(file_in)
    if ctx.message_id in starboard['messageCache'] or ctx.channel_id == starboard['channelID']: return

    guild          = Client.get_guild(ctx.guild_id)
    channel        = guild.get_channel(ctx.channel_id)
    message        = await channel.fetch_message(ctx.message_id)
    star_reactions = [_ for _ in message.reactions if _.emoji == '⭐']
    if not len(star_reactions): return

    if star_reactions[0].count >= starboard['minimumReactions']:
        starboard['messageCache'] = starboard['messageCache'][-24:] + [message.id]
        with open(f'./starboards/{ctx.guild_id}.json', 'w') as file_out: file_out.write(json.dumps(starboard, indent=4))

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

        if message.content:
            try:
                links = [_.group() for _ in re.finditer("(http)\S*(\s|)", message.content.lower())]
                for link in links[:4]:
                    if 'tenor.com/view/' in link:
                        r = requests.get(link)
                        url = f"https://c.tenor.com/{str(r.content).split('media1.tenor.com/m/')[1].split('/')[0]}/tenor.gif"
                    else: url = link
                    embed.set_image(url=url)
                    embeds.append(embed)
                    embed = discord.Embed(url="https://pzazs.thatgalblu.com")
                message.content = "\n".join(message.content.split(link))
            except: pass
                
            embed.add_field(name=f"__{message.author.name}__:", value=f"{message.content}")

        if len(message.attachments):
            i = len(embeds)
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