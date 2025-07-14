import discord, json
from discord.ext import commands as cmds
from Global import CommandScrollMenu, check_permission, reply, Client, request_emoji_embed


description = """Set up an autorole message for user-acquired server roles."""
permission = 2
aliases = ['autorole']
usage = []


async def handle(message: discord.Message, args: list=None, c: cmds.Context=None):
    if not await check_permission(message, permission, c): raise PermissionError

    response = await reply("> Loading...", m=message, c=c)

    try:
        with open(f'./autoroles/{message.guild.id}.json') as file_in: messages = json.load(file_in)
    except: messages = []

    view = AutoroleMessagesMenu(response, message.author, messages)
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


class AutoroleMessagesMenu(CommandScrollMenu):
    def __init__(self, attached_message: discord.Message, original_author: discord.Member, messages: list):
        super().__init__(attached_message, original_author, messages)
        self.move_position(0)
    

    @discord.ui.button(emoji="◀️")
    async def button_prv(self, interaction: discord.Interaction, button: discord.Button):
        self.interact(interaction)

        self.move_position(-1)
        await interaction.response.edit_message(embeds=[self.get_embed()], view=self)

    @discord.ui.button(emoji="➖")
    async def button_rmv(self, interaction: discord.Interaction, button: discord.Button):
        self.interact(interaction)

        try:
            channel = Client.get_channel(self.items[self.position]['channelID'])
            message = channel.get_partial_message(self.items[self.position]['messageID'])
            await message.delete()
        except: pass

        self.items.pop(self.position)
        with open(f'./autoroles/{interaction.guild.id}.json', 'w') as file_out: file_out.write(json.dumps(self.items, indent=4))

        self.move_position(-1)
        await interaction.response.edit_message(embeds=[self.get_embed()], view=self)

    @discord.ui.button(emoji="*️⃣")
    async def button_edt(self, interaction: discord.Interaction, button: discord.Button):
        self.interact(interaction)

        await interaction.response.edit_message(content="> Loading...", embeds=[], view=None)
        channel = Client.get_channel(self.items[self.position]['channelID'])
        message = channel.get_partial_message(self.items[self.position]['messageID'])

        view = AutoroleRolesSubmenu(self, message)
        await interaction.message.edit(content="", embeds=[view.get_embed()], view=view)

    @discord.ui.button(emoji="➕")
    async def button_add(self, interaction: discord.Interaction, button: discord.Button):
        self.interact(interaction)

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

        message = await channel.send("_ _", silent=True)

        new_autorole = {
            "title": response.content[response.content.find(' ')+1:],
            "channelID": channel.id,
            "messageID": message.id,
            "roles": []
        }

        self.items.append(new_autorole)
        try: await response.delete()
        except: pass

        self.position = len(self.items)-1
        
        with open(f'./autoroles/{interaction.guild.id}.json', 'w') as file_out: file_out.write(json.dumps(self.items, indent=4))
        await update(self.items[self.position]['roles'], new_autorole['title'], message)

        view = AutoroleRolesSubmenu(self, message)
        await interaction.message.edit(content="", embeds=[view.get_embed()], view=view)

    @discord.ui.button(emoji="▶️")
    async def button_nxt(self, interaction: discord.Interaction, button: discord.Button):
        self.interact(interaction)

        self.move_position(1)
        await interaction.response.edit_message(embeds=[self.get_embed()], view=self)

    
    def move_position(self, dposition: int) -> None:
        self.position            = max(0, self.position+dposition)
        self.button_prv.disabled = not self.position
        self.button_rmv.disabled = self.button_edt.disabled = not len(self.items)
        self.button_add.disabled = len(self.items)         >= 10
        self.button_nxt.disabled = self.position + 1       >= len(self.items)

    def get_embed(self) -> discord.Embed:
        embed = discord.Embed(color=0x69a9d9)
        embed.set_author(name=f"Auto-role messages for {self.attached_message.guild.name}", icon_url=self.attached_message.guild.icon.url)
        embed.set_footer(text="Closing prompt in 60s")

        if len(self.items):
            embed.title = f"Auto-role message __{self.position+1}__ of {len(self.items)}"
            embed.add_field(name="Title", value=self.items[self.position]['title'], inline=False)
            try:
                message = self.attached_message.guild.get_channel(self.items[self.position]['channelID']).get_partial_message(self.items[self.position]['messageID'])
                embed.add_field(name=f"Number of roles: {len(self.items[self.position]['roles'])}", value=f"[Jump to message ;](<{message.jump_url}>)", inline=False)
            except:
                embed.add_field(name="> The message associated with this auto-role is no longer accessable; The channel might be hidden to PZazS or deleted. You can use ➖ to remove the auto-role.", value="", inline=False)
                self.button_edt.disabled = True
        else:
            embed.title = "Auto-role messages __0__ of 0"
            embed.add_field(name="Press ➕ to add an auto-role message", value="")

        return embed
    

class AutoroleRolesSubmenu(CommandScrollMenu):
    def __init__(self, parent_menu: AutoroleMessagesMenu, message: discord.Message):
        super().__init__(parent_menu.attached_message, parent_menu.original_author, parent_menu.items[parent_menu.position]['roles'])

        self.parent_menu = parent_menu
        self.message = message
        self.move_position(0)

        self.parent_menu.timer.cancel()

    
    @discord.ui.button(emoji="◀️")
    async def button_prv(self, interaction: discord.Interaction, button: discord.Button):
        self.interact(interaction)

        self.move_position(-1)
        await interaction.response.edit_message(embeds=[self.get_embed()], view=self)

    @discord.ui.button(emoji="➖")
    async def button_rmv(self, interaction: discord.Interaction, button: discord.Button):
        self.interact(interaction)

        self.items.pop(self.position)
        with open(f'./autoroles/{interaction.guild.id}.json', 'w') as file_out: file_out.write(json.dumps(self.items, indent=4))
        await update(self.items, self.parent_menu.items[self.parent_menu.position]['title'], self.message)

        self.move_position(-1)
        await interaction.response.edit_message(embeds=[self.get_embed()], view=self)

    @discord.ui.button(style=discord.ButtonStyle.red, emoji="🔙")
    async def button_bck(self, interaction: discord.Interaction, button: discord.Button):
        self.interact(interaction)

        self.parent_menu.items[self.parent_menu.position]['roles'] = self.items
        view = AutoroleMessagesMenu(self.attached_message, self.original_author, self.parent_menu.items)
        view.move_position(self.parent_menu.position)
        await interaction.response.edit_message(embeds=[view.get_embed()], view=view)
        self.timer.cancel()

    @discord.ui.button(emoji="➕")
    async def button_add(self, interaction: discord.Interaction, button: discord.Button):
        self.interact(interaction)

        await interaction.response.edit_message(content="> Loading...", embeds=[], view=None)
        await interaction.message.edit(content="", embeds=[request_emoji_embed])
        try: reaction, _ = await Client.wait_for('reaction_add',
                                                 check=lambda x, y: x.message == interaction.message and y == self.original_author,
                                                 timeout=60.0)
        except TimeoutError: return await interaction.message.edit(content="> Timed out; Closing dialogue.", embeds=[])
        if not reaction.emoji and not Client.get_emoji(reaction.emoji): return await interaction.message.edit(content="> Unable to find that emoji; Closing Dialogue.", embeds=[])

        new_autorole = {
            "emoji": None,
            "emojiID": None,
            "roleID": None
        }

        try:
            new_autorole['emojiID'] = reaction.emoji.id
            if new_autorole['emojiID'] in [autorole['emojiID'] for autorole in self.items]:
                await interaction.message.clear_reactions()
                return await interaction.message.edit(content="> That emoji is already associated with a role in this message.", embeds=[self.get_embed()], view=self)
        except:
            new_autorole['emoji'] = reaction.emoji
            if new_autorole['emoji'] in [autorole['emoji'] for autorole in self.items]:
                await interaction.message.clear_reactions()
                return await interaction.message.edit(content="> That emoji is already associated with a role in this message.", embeds=[self.get_embed()], view=self)
        await interaction.message.clear_reactions()

        embed = discord.Embed(color=0xffffff,
                              title="Respond to this message with the role you want to associate with the emoji. (\"@rolename\")")
        embed.set_footer(text="Closing prompt in 60s")
        await interaction.message.edit(embeds=[embed])
        try: response = await Client.wait_for('message',
                                              check=lambda x: x.author == self.original_author,
                                              timeout=60.0)
        except TimeoutError: return await interaction.message.edit(content="> Timed out; Closing dialogue.", embeds=[])
        try: new_autorole['roleID'] = response.role_mentions[0].id
        except: return await interaction.message.edit(content="> Unable to parse role from response; Closing dialogue.", embeds=[])

        self.items.append(new_autorole)
        await response.delete()

        self.parent_menu.items[self.parent_menu.position]['roles'] = self.items
        with open(f'./autoroles/{interaction.guild.id}.json', 'w') as file_out: file_out.write(json.dumps(self.parent_menu.items, indent=4))
        await update(self.items, self.parent_menu.items[self.parent_menu.position]['title'], self.message)

        self.move_position(-self.position)
        self.move_position(len(self.items)-1)
        await interaction.message.edit(embeds=[self.get_embed()], view=self)

    @discord.ui.button(emoji="▶️")
    async def button_nxt(self, interaction: discord.Interaction, button: discord.Button):
        self.interact(interaction)

        self.move_position(1)
        await interaction.response.edit_message(embeds=[self.get_embed()], view=self)


    def move_position(self, dposition: int) -> None:
        self.position            = max(0, self.position+dposition)
        self.button_prv.disabled = not self.position
        self.button_rmv.disabled = not len(self.items)
        self.button_add.disabled = len(self.items)   >= 20
        self.button_nxt.disabled = self.position + 1 >= len(self.items)

    def get_embed(self) -> discord.Embed:
        embed = discord.Embed(color=0xa7a0ff)
        embed.set_author(name=f"Auto-role message in #{self.message.channel.name}")
        embed.set_footer(text="Closing prompt in 60s")

        if len(self.items):
            try:
                if not self.message.guild.get_role(self.items[self.position]['roleID']): raise
                embed.title = f"Role {self.position+1} of {len(self.items)}"
                try:
                    emoji = Client.get_emoji(self.items[self.position]['emojiID'])

                    embed.set_thumbnail(url=emoji.url)
                    embed.add_field(name="Emoji Type:", value="Custom")
                    embed.add_field(name="Name:", value=emoji.name)
                    embed.add_field(name="From:", value=emoji.guild.name)
                except:
                    emoji = self.items[self.position]['emoji']

                    embed.add_field(name="Emoji Type:", value="Default")
                    embed.add_field(name="Name:", value=emoji)
                    embed.add_field(name="From:", value="Unicode Consortium")
                
                embed.add_field(name="Role:", value=f"<@&{self.items[self.position]['roleID']}>")
            except:
                embed.add_field(name="> The role associated with this emoji is no longer available. You can use ➖ to remove it from the message.", value="")
        else:
            embed.title = f"Role __0__ of 0"
            embed.add_field(name="Press ➕ to add a role", value="")

        return embed


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
        if len(roles) == 1: await message.add_reaction(emoji)

    await message.edit(embeds=[embed])