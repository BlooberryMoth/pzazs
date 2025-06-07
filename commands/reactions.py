from Global import *


description = """Adds an emoji reaction to a message that you send."""
permission = 0
aliases = ['reactions', 'reacts']
usage = []


async def handle(message: discord.Message, args: list=None, c: cmds.Context=None):
    if not await check_permission(message, permission, c): raise PermissionError

    response = await reply("> Loading...", m=message, c=c)

    try:
        with open(f'./reactions/{message.author.id}.json') as fileIn: reactions = json.load(fileIn)
    except: reactions = []

    view = MessageReactionsMenu(message.author, reactions, response)
    await response.edit(content="", embeds=[view.get_embed()], view=view)


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


class MessageReactionsMenu(discord.ui.View):
    def __init__(self, original_author: discord.Member, reactions: list, message: discord.Message):
        super().__init__(timeout=60.0)

        self.original_author = original_author
        self.reactions = reactions
        self.message = message

        self.position = 0
        self.move_position(0)
    
        
    @discord.ui.button(custom_id="prev", style=discord.ButtonStyle.gray, emoji='◀️')
    async def prev(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user != self.original_author: return

        self.move_position(-1)
        await interaction.response.edit_message(embeds=[self.get_embed()], view=self)

    @discord.ui.button(custom_id="remove", style=discord.ButtonStyle.gray, emoji="➖")
    async def remove(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user != self.original_author: return

        self.reactions.pop(self.position)
        with open(f'./reactions/{self.original_author.id}.json', 'w') as fileOut: fileOut.write(json.dumps(self.reactions, indent=4))

        self.move_position(-1)
        await interaction.response.edit_message(embeds=[self.get_embed()], view=self)

    @discord.ui.button(custom_id="edit", style=discord.ButtonStyle.gray, emoji='*️⃣')
    async def edit(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user != self.original_author: return

        await interaction.response.send_modal(RequirementsModal(self))

    @discord.ui.button(custom_id="add", style=discord.ButtonStyle.gray, emoji='➕')
    async def add(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user != self.original_author: return

        await interaction.response.edit_message(content="> Loading...", embeds=[], view=None)

        embed = discord.Embed(color=0x69a9d9,
                              title="React to this message with the emoji you want to use",
                              description="(PZazS has to have access to this emoji for this to work.)") \
        .set_footer(text="Closing prompt in 60s")
        await interaction.message.edit(content="", embeds=[embed])
        try: reaction, _ = await Client.wait_for('reaction_add',
                                                 check=lambda x, y: y == self.original_author,
                                                 timeout=60.0)
        except TimeoutError: return await interaction.message.edit(content="> Timed out; Closing dialogue.", embeds=[])

        await interaction.message.clear_reactions()

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

        with open(f'./reactions/{self.original_author.id}.json', 'w') as fileOut: fileOut.write(json.dumps(self.reactions, indent=4))

        self.move_position(-self.position)
        self.move_position(len(self.reactions)-1)
        await interaction.message.edit(embeds=[self.get_embed()], view=self)

    @discord.ui.button(custom_id="next", style=discord.ButtonStyle.gray, emoji='▶️')
    async def next(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user != self.original_author: return

        self.move_position(1)
        await interaction.response.edit_message(embeds=[self.get_embed()], view=self)


    def move_position(self, dposition: int) -> None:
        self.position        = max(0, self.position+dposition)
        self.prev.disabled   = not self.position
        self.remove.disabled = self.edit.disabled   = not len(self.reactions)
        self.add.disabled    = len(self.reactions) >= 10
        self.next.disabled   = self.position + 1   >= len(self.reactions)

    def get_embed(self) -> discord.Embed:
        embed = discord.Embed(color=0x69a9d9,
                              title=f"Reaction __{self.position + 1}__ of {len(self.reactions)}")
        embed.set_author(name=f"{self.original_author}'s reactions", icon_url=self.original_author.avatar.url)
        embed.set_footer(text="Closing prompt in 60s")
        if len(self.reactions):
            requirements = self.reactions[self.position]['message']

            contains  = ('"' + '\" \"'.join(requirements['contains']) + '"') if len(requirements['contains']) else ""
            excludes  = ('"' + '\" \"'.join(requirements['excludes']) + '"') if len(requirements['excludes']) else ""
            isExactly = ('"' + '\" \"'.join(requirements['isExactly']) + '"') if len(requirements['isExactly']) else ""

            try:
                emoji = Client.get_emoji(self.reactions[self.position]['emojiID'])
                
                embed.set_thumbnail(url=emoji.url)
                embed.add_field(name="Type:", value="Custom")
                embed.add_field(name="Name:", value=emoji.name)
                embed.add_field(name="From:", value=emoji.guild.name)
            except:
                emoji = self.reactions[self.position]['emoji']

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

    async def on_timeout(self) -> None:
        await self.message.edit(content="> Timed out.", embeds=[], view=None)


class RequirementsModal(discord.ui.Modal):
    def __init__(self, view: MessageReactionsMenu):
        super().__init__(title="Message requirements for this reaction", custom_id="requirements")

        self.view = view

        requirements = self.view.reactions[self.view.position]['message']
        contains  = ('"' + '\" \"'.join(requirements['contains']) + '"') if len(requirements['contains']) else ""
        excludes  = ('"' + '\" \"'.join(requirements['excludes']) + '"') if len(requirements['excludes']) else ""
        isExactly = ('"' + '\" \"'.join(requirements['isExactly']) + '"') if len(requirements['isExactly']) else ""

        self.add_item(discord.ui.TextInput(label="Message contains:",   placeholder="Format: \"text 1\" \"text 2\"", default=contains,  required=False))
        self.add_item(discord.ui.TextInput(label="Message excludes:",   placeholder="Format: \"text 1\" \"text 2\"", default=excludes,  required=False))
        self.add_item(discord.ui.TextInput(label="Message is exactly:", placeholder="Format: \"text 1\" \"text 2\"", default=isExactly, required=False))

    async def on_submit(self, interaction: discord.Interaction):
        self.view.reactions[self.view.position]['message']['contains'] = [snip.replace('"', "") for snip in self.children[0].value.split('" "')] if len(self.children[0].value) else []
        self.view.reactions[self.view.position]['message']['excludes'] = [snip.replace('"', "") for snip in self.children[1].value.split('" "')] if len(self.children[1].value) else []
        self.view.reactions[self.view.position]['message']['isExactly'] = [snip.replace('"', "") for snip in self.children[2].value.split('" "')] if len(self.children[2].value) else []

        with open(f'./reactions/{interaction.user.id}.json', 'w') as fileOut: fileOut.write(json.dumps(self.view.reactions, indent=4))

        view = MessageReactionsMenu(self.view.original_author, self.view.reactions, self.view.message)
        view.move_position(self.view.position)

        await self.view.message.edit(content="", embeds=[view.get_embed()], view=view)
        await interaction.response.defer()