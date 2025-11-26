import discord, json
from discord.ext import commands
from Global import CommandScrollMenu, Permission, Client, none, request_emoji_embed


description = """Adds an emoji reaction to a message that you send."""
permission = Permission.DIRECT_MESSAGES
aliases = ['reactions', 'reacts']
usage = []


async def handle(message: discord.Message, *_): await reactions(await Client.get_context(message))


@Client.hybrid_command()
async def reactions(ctx: commands.Context):
    """
    Adds an emoji reaction to a message that you send.
    
    Parameters
    ----------
    ctx: cmds.Context
        Context
    """
    if not await Permission.check(ctx, permission): raise PermissionError

    response = await ctx.reply("> Loading...", allowed_mentions=none, silent=True)

    try:
        with open(f'./features/reactions/{ctx.author.id}.json') as file_in: reactions = json.load(file_in)
    except: reactions = []

    view = MessageReactionsMenu(response, ctx.author, reactions)
    await response.edit(content="", embeds=[view.get_page()], view=view)


class MessageReactionsMenu(CommandScrollMenu):
    def __init__(self, attached_message: discord.Message, original_author: discord.Member, reactions: list):
        super().__init__(attached_message, original_author, reactions)
        self.move_position(0)
    
        
    @discord.ui.button(emoji='◀️')
    async def button_prv(self, interaction: discord.Interaction, button: discord.Button):
        self.interact(interaction)

        self.move_position(-1)
        await interaction.response.edit_message(embeds=[self.get_page()], view=self)

    @discord.ui.button(emoji="➖")
    async def button_rmv(self, interaction: discord.Interaction, button: discord.Button):
        self.interact(interaction)

        self.items.pop(self.position)
        with open(f'./features/reactions/{self.original_author.id}.json', 'w') as file_out: file_out.write(json.dumps(self.items, indent=4))

        self.move_position(-1)
        await interaction.response.edit_message(embeds=[self.get_page()], view=self)

    @discord.ui.button(emoji='*️⃣')
    async def button_edt(self, interaction: discord.Interaction, button: discord.Button):
        self.interact(interaction)

        await interaction.response.send_modal(RequirementsModal(self))

    @discord.ui.button(emoji='➕')
    async def button_add(self, interaction: discord.Interaction, button: discord.Button):
        self.interact(interaction)

        await interaction.response.edit_message(content="> Loading...", embeds=[], view=None)
        await interaction.message.edit(content="", embeds=[request_emoji_embed])
        try: reaction, _ = await Client.wait_for('reaction_add',
                                                 check=lambda x, y: x.message == interaction.message and y == self.original_author,
                                                 timeout=60.0)
        except TimeoutError: return await interaction.message.edit(content="> Timed out; Closing dialogue.", embeds=[])
        await interaction.message.clear_reactions()
        if not reaction.emoji and Client.get_emoji(reaction.emoji): return await interaction.message.edit(content="> Unable to find that emoji; Closing Dialogue.", embeds=[])

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
        self.items.append(newReaction)

        with open(f'./features/reactions/{self.original_author.id}.json', 'w') as file_out: file_out.write(json.dumps(self.items, indent=4))

        self.move_position(-self.position)
        self.move_position(len(self.items)-1)
        await interaction.message.edit(embeds=[self.get_page()], view=self)

    @discord.ui.button(emoji='▶️')
    async def button_nxt(self, interaction: discord.Interaction, button: discord.Button):
        self.interact(interaction)

        self.move_position(1)
        await interaction.response.edit_message(embeds=[self.get_page()], view=self)


    def move_position(self, dposition: int) -> None:
        self.position            = max(0, self.position+dposition)
        self.button_prv.disabled = not self.position
        self.button_rmv.disabled = self.button_edt.disabled = not len(self.items)
        self.button_add.disabled = len(self.items)         >= 10
        self.button_nxt.disabled = self.position + 1       >= len(self.items)

    def get_page(self) -> discord.Embed:
        embed = discord.Embed(color=0x69a9d9,
                              title=f"Reaction __{self.position + 1}__ of {len(self.items)}")
        embed.set_author(name=f"{self.original_author}'s reactions", icon_url=self.original_author.avatar.url)
        embed.set_footer(text="Closing prompt in 60s")
        if len(self.items):
            requirements = self.items[self.position]['message']

            contains  = ('"' + '\" \"'.join(requirements['contains']) + '"') if len(requirements['contains']) else ""
            excludes  = ('"' + '\" \"'.join(requirements['excludes']) + '"') if len(requirements['excludes']) else ""
            isExactly = ('"' + '\" \"'.join(requirements['isExactly']) + '"') if len(requirements['isExactly']) else ""

            try:
                emoji = Client.get_emoji(self.items[self.position]['emojiID'])
                
                embed.set_thumbnail(url=emoji.url)
                embed.add_field(name="Type:", value="Custom")
                embed.add_field(name="Name:", value=emoji.name)
                embed.add_field(name="From:", value=emoji.guild.name)
            except:
                emoji = self.items[self.position]['emoji']

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


class RequirementsModal(discord.ui.Modal):
    def __init__(self, view: MessageReactionsMenu):
        super().__init__(title="Message requirements for this reaction", custom_id="requirements")

        self.view = view

        requirements = self.view.items[self.view.position]['message']
        contains  = ('"' + '\" \"'.join(requirements['contains']) + '"') if len(requirements['contains']) else ""
        excludes  = ('"' + '\" \"'.join(requirements['excludes']) + '"') if len(requirements['excludes']) else ""
        isExactly = ('"' + '\" \"'.join(requirements['isExactly']) + '"') if len(requirements['isExactly']) else ""

        self.add_item(discord.ui.TextInput(label="Message contains:",   placeholder="Format: \"text 1\" \"text 2\"", default=contains,  required=False))
        self.add_item(discord.ui.TextInput(label="Message excludes:",   placeholder="Format: \"text 1\" \"text 2\"", default=excludes,  required=False))
        self.add_item(discord.ui.TextInput(label="Message is exactly:", placeholder="Format: \"text 1\" \"text 2\"", default=isExactly, required=False))

    async def on_submit(self, interaction: discord.Interaction):
        self.view.items[self.view.position]['message']['contains'] = [snip.replace('"', "") for snip in self.children[0].value.split('" "')] if len(self.children[0].value) else []
        self.view.items[self.view.position]['message']['excludes'] = [snip.replace('"', "") for snip in self.children[1].value.split('" "')] if len(self.children[1].value) else []
        self.view.items[self.view.position]['message']['isExactly'] = [snip.replace('"', "") for snip in self.children[2].value.split('" "')] if len(self.children[2].value) else []

        with open(f'./features/reactions/{interaction.user.id}.json', 'w') as file_out: file_out.write(json.dumps(self.view.items, indent=4))

        await self.view.attached_message.edit(content="", embeds=[self.view.get_page()], view=self.view)
        await interaction.response.defer()