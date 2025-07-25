import discord
from discord.ext import commands, tasks
from Logging import LOGGER


# Global variables, imports, and methods

try:
    with open("./token.txt") as token: token = fr'{token.read()}'
except Exception as e: raise Exception(f"Unable to load token from \"token.txt\": {e}") from e
try:
    with open("./oauth-secret.txt") as secret: secret = fr'{secret.read()}'
except Exception as e:
    secret = None
    LOGGER.error(f"Unable to load secret from \"oauth-secret.txt\": {e}")

# Global variables

PREFIX = '..'
activityText = fr"in dev mode"
intents  = discord.Intents.default(); intents.members = intents.message_content = True
activity = discord.Activity(name=activityText, type=discord.ActivityType.playing)
Client   = commands.Bot(command_prefix=PREFIX, intents=intents, activity=activity)

threads = []
command_aliases = {}

request_emoji_embed = discord.Embed(color=0x69a9d9,
                                    title="React to this message with the emoji you want to use",
                                    description="(PZazS has to have access to this emoji for this to work.)") \
.set_footer(text="Closing prmopt in 60s")

none = discord.AllowedMentions.none()

# Global methods

async def reply(content: str, embeds: list=[], view: discord.ui.View=None, message: discord.Message=None, ctx: commands.Context=None, ephemeral: bool=False) -> discord.Message:
    if ctx: return await ctx.send(content, embeds=embeds, view=view, allowed_mentions=none, silent=True, ephemeral=ephemeral)
    else: return await message.reply(content, embeds=embeds, view=view, allowed_mentions=none, silent=True)

async def check_permission(message: discord.Message, permission: int=3, ctx: commands.Context=None) -> bool:
    userPermissionLevel = 0
    if message.guild:
        userPermissionLevel += 1
        if message.author.guild_permissions.kick_members: userPermissionLevel += 1
        if message.author == message.guild.owner: userPermissionLevel += 1
    if userPermissionLevel >= permission: return True
    else:
        if userPermissionLevel == 0:
            if ctx: await ctx.send("You have to be in a server to use this command.", ephemeral=True)
            else: await message.reply("You have to be in a server to use this command.", allowed_mentions=none, silent=True)
        else:
            if ctx: await ctx.send("You do not have permission to use this command.", ephemeral=True)
            else: await message.reply("You do not have permission to use this command.", allowed_mentions=none, silent=True)
        return False
    
# Global classes

class CommandScrollMenu(discord.ui.View):
    def __init__(self, attached_message: discord.Message, original_author: discord.Member, items: list|dict=[]):
        super().__init__(timeout=None)

        self.attached_message = attached_message
        self.original_author  = original_author
        self.items = items

        self.position = 0

        self.timer.start()

    def interact(self, interaction: discord.Interaction):
        if interaction.user != self.original_author: raise
        self.timer.restart()

    @tasks.loop(seconds=60.0, count=1)
    async def timer(self): pass
    @timer.after_loop
    async def on_timeout(self):
        if self.timer.current_loop: await self.attached_message.edit(content="> Timed out; Closing dialogue.", embeds=[], view=None)

    def get_embed(self) -> discord.Embed: ...