from Global import *


description = """Set up an autorole message for user-acquired server roles."""
permission = 2
aliases = ['autorole']
useage = []


async def handle(message: discord.Message, args: list=None, c: cmds.Context=None):
    if not await check_permission(message, permission, c): raise PermissionError

    response = await reply("> Loading...", m=message, c=c)

    try:
        with open(f'./autoroles/{message.guild.id}.json') as fileIn: messages = json.load(fileIn)
    except: messages = []

    view = AutoroleMessagesMenu(message.author, messages, response)
    await response.edit(content="", embeds=[view.get_embed()], view=view)


@Client.hybrid_command()
async def autorole(ctx: cmds.Context):
    """
    Set up an autorole message for user-acquired server roles.

    Parameters
    ----------
    ctx: cmds.Context
        Context
    """
    try: await handle(ctx.message, c=ctx)
    except PermissionError: return


class AutoroleMessagesMenu(discord.ui.View):
    def __init__(self, original_author: discord.Member, messages: list, message: discord.Message):
        super().__init__(timeout=60.0)

        self.original_author = original_author
        self.messages = messages
        self.message = message

        self.position = 0
        self.move_position(0)
    

    @discord.ui.button(custom_id="prev", style=discord.ButtonStyle.gray, emoji="◀️")
    async def prev(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user != self.original_author: return

        self.move_position(-1)
        await interaction.response.edit_message(embeds=[self.get_embed()], view=self)

    @discord.ui.button(custom_id="remove", style=discord.ButtonStyle.gray, emoji="➖")
    async def remove(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user != self.original_author: return

        try:
            channel = await Client.fetch_channel(self.messages[self.position]['channelID'])
            message = await channel.fetch_message(self.messages[self.position]['messageID'])
            await message.delete()
        except: pass

        self.messages.pop(self.position)
        with open(f'./autoroles/{interaction.guild.id}.json', 'w') as fileOut: fileOut.write(json.dumps(self.messages, indent=4))

        self.move_position(-1)
        await interaction.response.edit_message(embeds=[self.get_embed()], view=self)

    @discord.ui.button(custom_id="edit", style=discord.ButtonStyle.gray, emoji="*️⃣")
    async def edit(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user != self.original_author: return

        await interaction.response.edit_message(content="> Loading...", embeds=[], view=None)

        channel = await Client.fetch_channel(self.messages[self.position]['channelID'])
        autorole_message = await channel.fetch_message(self.messages[self.position]['messageID'])

        view = AutoroleRolesMenu(self, autorole_message)
        await interaction.message.edit(content="", embeds=[view.get_embed()], view=view)

    @discord.ui.button(custom_id="add", style=discord.ButtonStyle.gray, emoji="➕")
    async def add(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user != self.original_author: return

        await interaction.response.edit_message(content="> Loading...", embeds=[], view=None)

        embed = discord.Embed(color=0x69a9d9,
                              title="Response to this message with the channel you want the autorole to be in, and the title of the message. (i.e \"#channel-name title goes here\")",
                              description="(PZazS has to have access to this channel for this to work.)") \
        .set_footer(text="Closing prompt in 60s")

        await interaction.message.edit(content="", embeds=[embed])
        try: response = await Client.wait_for('message',
                                              check=lambda x: x.author == self.original_author,
                                              timeout=60.0)
        except TimeoutError: return await interaction.message.edit(content="> Timed out; Closing dialogue.", embeds=[])

        try: channel = response.channel_mentions[0]
        except: return await interaction.message.edit(content="> Unable to parse channel from response; Closing dialogue.", embeds=[])

        autorole_message = await channel.send("_ _", silent=True)

        new_autorole = {
            "title": response.content[response.content.find(' ')+1:],
            "channelID": channel.id,
            "messageID": autorole_message.id,
            "roles": []
        }

        self.messages.append(new_autorole)
        try: await response.delete()
        except: pass

        self.position = len(self.messages)-1
        
        with open(f'./autoroles/{interaction.guild.id}.json', 'w') as fileOut: fileOut.write(json.dumps(self.messages, indent=4))
        await update(self.messages[self.position]['roles'], new_autorole['title'], autorole_message)

        view = AutoroleRolesMenu(self, autorole_message)
        await interaction.message.edit(content="", embeds=[view.get_embed()], view=view)

    @discord.ui.button(custom_id="next", style=discord.ButtonStyle.gray, emoji="▶️")
    async def next(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user != self.original_author: return

        self.move_position(1)
        await interaction.response.edit_message(embeds=[self.get_embed()], view=self)

    
    def move_position(self, dposition: int) -> None:
        self.position        = max(0, self.position+dposition)
        self.prev.disabled   = not self.position
        self.remove.disabled = self.edit.disabled  = not len(self.messages)
        self.add.disabled    = len(self.messages) >= 10
        self.next.disabled   = self.position + 1  >= len(self.messages)

    def get_embed(self) -> discord.Embed:
        embed = discord.Embed(color=0x69a9d9)
        embed.set_author(name=f"Auto-role messages for {self.message.guild.name}", icon_url=self.message.guild.icon.url)
        embed.set_footer(text="Closing prompt in 60s")

        if len(self.messages):
            embed.title = f"Auto-role message __{self.position+1}__ of {len(self.messages)}"
            embed.add_field(name="Title", value=self.messages[self.position]['title'], inline=False)
            try:
                message = self.message.guild.get_channel(self.messages[self.position]['channelID']).get_partial_message(self.messages[self.position]['messageID'])

                embed.add_field(name=f"Number of roles: {len(self.messages[self.position]['roles'])}", value=f"[Jump to message ;](<{message.jump_url}>)", inline=False)
            except:
                embed.add_field(name="> The message associated with this auto-role is no longer accessable; The channel might be hidden to PZazS or deleted. You can use ➖ to remove the auto-role.", value="", inline=False)
                self.edit.disabled = True
        else:
            embed.title = "Auto-role messages __0__ of 0"
            embed.add_field(name="Press ➕ to add an auto-role message", value="")

        return embed

    async def on_timeout(self) -> None:
        await self.message.edit(content="> Timed out.", embeds=[], view=None)
    

class AutoroleRolesMenu(discord.ui.View):
    def __init__(self, parent_menu: AutoroleMessagesMenu, autorole_message: discord.Message):
        super().__init__(timeout=60.0)

        self.parent_menu = parent_menu
        self.original_author = parent_menu.original_author
        self.messages = parent_menu.messages
        self.message = autorole_message

        self.position = 0
        self.move_position(0)

    
    @discord.ui.button(custom_id="prev", style=discord.ButtonStyle.gray, emoji="◀️")
    async def prev(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user != self.original_author: return

        self.move_position(-1)
        await interaction.response.edit_message(embeds=[self.get_embed()], view=self)

    @discord.ui.button(custom_id="remove", style=discord.ButtonStyle.gray, emoji="➖")
    async def remove(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user != self.original_author: return

        self.messages[self.parent_menu.position]['roles'].pop(self.position)
        with open(f'./autoroles/{interaction.guild.id}.json', 'w') as fileOut: fileOut.write(json.dumps(self.messages, indent=4))
        await update(self.messages[self.parent_menu.position]['roles'], self.messages[self.parent_menu.position]['title'], self.message)

        self.move_position(-1)
        await interaction.response.edit_message(embeds=[self.get_embed()], view=self)

    @discord.ui.button(custom_id="back", style=discord.ButtonStyle.red, emoji="🔙")
    async def back(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user != self.original_author: return

        view = AutoroleMessagesMenu(self.original_author, self.messages, self.message)
        view.move_position(self.parent_menu.position)
        await interaction.response.edit_message(embeds=[view.get_embed()], view=view)

    @discord.ui.button(custom_id="add", style=discord.ButtonStyle.gray, emoji="➕")
    async def add(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user != self.original_author: return

        await interaction.response.edit_message(content="> Loading...", embeds=[], view=None)

        embed = discord.Embed(color=0xffffff,
                              title="React to this message with the emoji you want associated.",
                              description="(PZazS has to have access to this emoji for this to work.)")
        embed.set_footer(text="Closing prompt in 60s")

        await interaction.message.edit(content="", embeds=[embed])
        try: reaction, _ = await Client.wait_for('reaction_add',
                                                 check=lambda x, y: y == self.original_author,
                                                 timeout=60.0)
        except TimeoutError: return await interaction.message.edit(content="> Timed out; Closing dialogue.", embeds=[])

        newRole = {
            "emoji": None,
            "emojiID": None,
            "roleID": None
        }

        try: newRole['emojiID'] = reaction.emoji.id
        except: newRole['emoji'] = reaction.emoji

        await interaction.message.clear_reactions()

        embed = discord.Embed(color=0xffffff,
                              title="Respond to this message with the role you want to associate with the emoji. (\"@rolename\")")
        embed.set_footer(text="Closing prompt in 60s")

        await interaction.message.edit(embeds=[embed])
        try: response = await Client.wait_for('message',
                                              check=lambda x: x.author == self.original_author,
                                              timeout=60.0)
        except TimeoutError: return await interaction.message.edit(content="> Timed out; Closing dialogue.", embeds=[])

        try: newRole['roleID'] = response.role_mentions[0].id
        except: return await interaction.message.edit(content="> Unable to parse role from response; Closing dialogue.", embeds=[])

        self.messages[self.parent_menu.position]['roles'].append(newRole)
        await response.delete()

        with open(f'./autoroles/{interaction.guild.id}.json', 'w') as fileOut: fileOut.write(json.dumps(self.messages, indent=4))
        await update(self.messages[self.parent_menu.position]['roles'], self.messages[self.parent_menu.position]['title'], self.message)

        self.move_position(-self.position)
        self.move_position(len(self.messages[self.parent_menu.position]['roles'])-1)
        await interaction.message.edit(embeds=[self.get_embed()], view=self)

    @discord.ui.button(custom_id="next", style=discord.ButtonStyle.gray, emoji="▶️")
    async def next(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user != self.original_author: return

        self.move_position(1)
        await interaction.response.edit_message(embeds=[self.get_embed()], view=self)


    def move_position(self, dposition: int) -> None:
        self.position        = max(0, self.position+dposition)
        self.prev.disabled   = not self.position
        self.remove.disabled = not len(self.messages[self.parent_menu.position]['roles'])
        self.add.disabled    = len(self.messages[self.parent_menu.position]['roles']) >= 20
        self.next.disabled   = self.position + 1 >= len(self.messages[self.parent_menu.position]['roles'])

    def get_embed(self) -> discord.Embed:
        embed = discord.Embed(color=0xa7a0ff)
        embed.set_author(name=f"Auto-role message in #{self.message.channel.name}")
        embed.set_footer(text="Closing prompt in 60s")

        autoroles = self.messages[self.parent_menu.position]['roles']
        if len(autoroles):
            try:
                if not self.message.guild.get_role(autoroles[self.position]['roleID']): raise
                embed.title = f"Role {self.position+1} of {len(autoroles)}"
                try:
                    emoji = Client.get_emoji(autoroles[self.position]['emojiID'])

                    embed.set_thumbnail(url=emoji.url)
                    embed.add_field(name="Emoji Type:", value="Custom")
                    embed.add_field(name="Name:", value=emoji.name)
                    embed.add_field(name="From:", value=emoji.guild.name)
                except:
                    emoji = autoroles[self.position]['emoji']

                    embed.add_field(name="Emoji Type:", value="Default")
                    embed.add_field(name="Name:", value=emoji)
                    embed.add_field(name="From:", value="Unicode Consortium")
                
                embed.add_field(name="Role:", value=f"<@&{autoroles[self.position]['roleID']}>")
            except:
                embed.add_field(name="> The role associated with this emoji is no longer available. You can use ➖ to remove it from the message.", value="")
        else:
            embed.title = f"Role __0__ of 0"
            embed.add_field(name="Press ➕ to add a role", value="")

        return embed

    async def on_timeout(self) -> None:
        await self.parent_menu.message.edit(content="> Timed out.", embeds=[], view=None)


async def update(roles: list, title: str, message: discord.Message):
    await message.clear_reactions()

    embed = discord.Embed(color=0x69a9d9,
                          title=f"{title}")
    embed.add_field(name="React with the corresponding emoji to get/remove the role!", value="")
    for autorole in roles:
        try:
            emoji = Client.get_emoji(autorole['emojiID'])
            if not emoji: raise

            embed.add_field(name="", value=f"<{'a' if emoji.animated else ''}:{emoji.name}:{emoji.id}> `-` <@&{autorole['roleID']}>", inline=False)
        except:
            emoji = autorole['emoji']
            embed.add_field(name="", value=f"{emoji} `-` <@&{autorole['roleID']}>", inline=False)
        await message.add_reaction(emoji)

    await message.edit(embeds=[embed])