from Global import *


description = """Adds an emoji reaction to a message that you send."""
permission = 0
aliases = ['reactions', 'reacts']
usage = []


async def handle(message: discord.Message, args: list=None, c: cmds.Context=None):
    if not await check_permission(message, permission, c): raise PermissionError

    guild = message.guild
    author = message.author

    try:
        with open(f'./reactions/{author.id}.json') as fileIn: reactions = json.load(fileIn)
    except: reactions = []

    embed = get_reaction(author, reactions, 0)
        
    return await reply("", [embed], DefaultMenu(original_author=message.author, reactions=reactions, pos=0), m=message, c=c)


@Client.hybrid_command()
async def reactions(ctx: cmds.Context):
    """
    Adds an emoji reaction to a message that you send.
    
    Parameters
    ----------
    ctx: cmds.Context
        Context
    """
    try: await handle(ctx.message, c=ctx)
    except PermissionError: return


class DefaultMenu(discord.ui.View):
    def __init__(self, original_author: discord.Member, reactions: list, pos: int, timeout = 60.0):
        super().__init__(timeout=timeout)

        self.original_author = original_author
        self.reactions = reactions
        self.pos = 0

        self.move_position(pos)
        
    @discord.ui.button(custom_id="prev", style=discord.ButtonStyle.gray, emoji='◀️')
    async def prev(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user != self.original_author: return
        self.move_position(-1)
        await interaction.response.edit_message(embeds=[get_reaction(self.original_author, self.reactions, self.pos)], view=self)

    @discord.ui.button(custom_id="remove", style=discord.ButtonStyle.gray, emoji="➖")
    async def remove(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user != self.original_author: return
        self.reactions.pop(self.pos)
        with open(f'./reactions/{self.original_author.id}.json', 'w') as fileOut: fileOut.write(json.dumps(self.reactions, indent=4))
        self.move_position(-1)
        await interaction.response.edit_message(embeds=[get_reaction(self.original_author, self.reactions, self.pos)], view=self)

    @discord.ui.button(custom_id="edit", style=discord.ButtonStyle.gray, emoji='*️⃣')
    async def edit(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user != self.original_author: return
        await interaction.response.send_modal(RequirementsModal(original_author=self.original_author, response=interaction.message, reactions=self.reactions, pos=self.pos))

    @discord.ui.button(custom_id="add", style=discord.ButtonStyle.gray, emoji='➕')
    async def add(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user != self.original_author: return

        await interaction.response.edit_message(content="> Loading...", embeds=[], view=None)

        embed = discord.Embed(color=0x69a9d9,
                              title="React to this message with the emoji you want to use",
                              description="(PZazS has to have access to this emoji for this to work.)") \
        .set_footer(text="Closing prompt in 60s")
        dialogue = await interaction.message.edit(content="", embeds=[embed])
        try: reaction, _ = await Client.wait_for('reaction_add',
                                                 check=lambda x, y: y == self.original_author,
                                                 timeout=60.0)
        except TimeoutError: return await dialogue.edit(content="> Timed out; Closing dialogue.", embeds=[])

        newReaction = {
            "emoji": None,
            "emojiID": None,
            "requirements": {
                "serverID": None,
                "channelID": None
            },
            "message": {
                "contains": [],
                "excludes": [],
                "isExactly": []
            }
        }

        try: newReaction['emojiID'] = reaction.emoji.id
        except: newReaction['emoji'] = reaction.emoji

        self.reactions.append(newReaction)
        await interaction.message.clear_reactions()

        with open(f'./reactions/{self.original_author.id}.json', 'w') as fileOut: fileOut.write(json.dumps(self.reactions, indent=4))
        self.move_position(-self.pos)
        self.move_position(len(self.reactions)-1)
        return await interaction.message.edit(embeds=[get_reaction(self.original_author, self.reactions, len(self.reactions)-1)], view=self)

    @discord.ui.button(custom_id="next", style=discord.ButtonStyle.gray, emoji='▶️')
    async def next(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user != self.original_author: return
        self.move_position(1)
        await interaction.response.edit_message(embeds=[get_reaction(self.original_author, self.reactions, self.pos)], view=DefaultMenu(self.original_author, self.reactions, self.pos))

    def move_position(self, pos: int):
        self.pos = max(0, self.pos+pos)
        self.children[0].disabled = not self.pos
        self.children[1].disabled = self.children[2].disabled = not len(self.reactions)
        self.children[3].disabled = len(self.reactions) >= 10
        self.children[4].disabled = self.pos + 1 >= len(self.reactions)


class RequirementsModal(discord.ui.Modal):
    def __init__(self, *, original_author: discord.Member, response: discord.Message, reactions: list, pos: int, title = "Message requirements for this reaction", timeout = None, custom_id = "requirements"):
        super().__init__(title=title, timeout=timeout, custom_id=custom_id)

        self.original_author = original_author
        self.response = response
        self.pos = pos
        self.reactions = reactions

        requirements = reactions[pos]['message']

        contains  = ('"' + '\" \"'.join(requirements['contains']) + '"') if len(requirements['contains']) else ""
        excludes  = ('"' + '\" \"'.join(requirements['excludes']) + '"') if len(requirements['excludes']) else ""
        isExactly = ('"' + '\" \"'.join(requirements['isExactly']) + '"') if len(requirements['isExactly']) else ""

        self.add_item(discord.ui.TextInput(label="Message contains:",   placeholder="Format: \"text 1\" \"text 2\"", default=contains,  required=False))
        self.add_item(discord.ui.TextInput(label="Message excludes:",   placeholder="Format: \"text 1\" \"text 2\"", default=excludes,  required=False))
        self.add_item(discord.ui.TextInput(label="Message is exactly:", placeholder="Format: \"text 1\" \"text 2\"", default=isExactly, required=False))

    async def on_submit(self, interaction: discord.Interaction):
        self.reactions[self.pos]['message']['contains'] = [snip.replace('"', "") for snip in self.children[0].value.split('" "')] if len(self.children[0].value) else []
        self.reactions[self.pos]['message']['excludes'] = [snip.replace('"', "") for snip in self.children[1].value.split('" "')] if len(self.children[1].value) else []
        self.reactions[self.pos]['message']['isExactly'] = [snip.replace('"', "") for snip in self.children[2].value.split('" "')] if len(self.children[2].value) else []

        with open(f'./reactions/{interaction.user.id}.json', 'w') as fileOut: fileOut.write(json.dumps(self.reactions, indent=4))
        await self.response.edit(embeds=[get_reaction(interaction.user, self.reactions, self.pos)], view=DefaultMenu(original_author=self.original_author, reactions=self.reactions, pos=self.pos))
        await interaction.response.defer()


def get_reaction(user: discord.Member, reactions: list | None, pos: int) -> discord.Embed:
    embed = discord.Embed(color=0x69a9d9,
                          title=f"Reaction __{pos + 1}__ of {len(reactions)}")
    embed.set_author(name=f"{user}'s reactions", icon_url=user.avatar.url)
    embed.set_footer(text="Closing prompt in 60s")
    if len(reactions):
        requirements = reactions[pos]['message']

        contains  = ('"' + '\" \"'.join(requirements['contains']) + '"') if len(requirements['contains']) else ""
        excludes  = ('"' + '\" \"'.join(requirements['excludes']) + '"') if len(requirements['excludes']) else ""
        isExactly = ('"' + '\" \"'.join(requirements['isExactly']) + '"') if len(requirements['isExactly']) else ""

        try:
            emoji = Client.get_emoji(reactions[pos]['emojiID'])
            
            embed.set_thumbnail(url=emoji.url)
            embed.add_field(name="Type:", value="Custom")
            embed.add_field(name="Name:", value=emoji.name)
            embed.add_field(name="From:", value=emoji.guild.name)
        except:
            emoji = reactions[pos]['emoji']

            embed.add_field(name="Type:", value="Default")
            embed.add_field(name="Name:", value=emoji)
            embed.add_field(name="From:", value="Unicode Consortium")

        embed.add_field(name="Will add reaction if the message", value="", inline=False)
        embed.add_field(name="Contains:",              value=contains,  inline=False)
        embed.add_field(name="And, does not contain:", value=excludes,  inline=False)
        embed.add_field(name="Or, is exactly:",        value=isExactly, inline=False)

        return embed
    else:
        embed.title = "Reaction __0__ of 0"
        embed.add_field(name="Press ➕ to add a reaction", value="")

        return embed