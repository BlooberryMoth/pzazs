from Global import *


description = """Test"""
permission = 2
aliases = ['test']
usage = []


async def handle(message: discord.Message, args: list=None, c: cmds.Context=None):
    if not await check_permission(message, permission, c): raise PermissionError

    response = await reply("> Loading...", m=message, c=c)

    view = TestCommandMenu(response, message.author)
    await response.edit(content="", view=view)


@Client.hybrid_command()
async def test(ctx: cmds.Context):
    """
    Test
    
    Parameters
    ----------
    ctx: cmds.Context
        Context
    """
    try: await handle(ctx.message, c=ctx)
    except PermissionError: return


class TestCommandMenu(CommandScrollMenu):
    def __init__(self, attached_message, original_author):
        super().__init__(attached_message, original_author)

    @discord.ui.button(emoji="✳️")
    async def button_2(self, interaction: discord.Interaction, button: discord.Button):
        self.interact(interaction)

        new_time = dt.now() + rd(seconds=self.timer.seconds)
        await interaction.response.edit_message(content=f"<t:{int(new_time.timestamp())}:R>", view=self)