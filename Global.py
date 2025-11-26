import discord
from discord.ext import commands, tasks
from PIL import ImageFont
from Logging import LOG


# Global variables, imports, and methods

try:
    with open("./token.txt") as token: token = fr'{token.read()}'
except Exception as e: raise Exception(f"Unable to load token from \"token.txt\": {e}") from e
try:
    with open("./oauth-secret.txt") as secret: secret = fr'{secret.read()}'
except Exception as e:
    secret = None
    LOG.error(f"Unable to load secret from \"oauth-secret.txt\": {e}")

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

# I feel this class is pretty self-explanatory
class Permission:
    DIRECT_MESSAGES = 0
    USER = 1
    MODERATOR = 2
    SERVER_OWNER = 3

    @staticmethod
    async def check(ctx: commands.Context, permission: int=3) -> bool:
        user_permission_level = Permission.DIRECT_MESSAGES
        if ctx.guild:
            user_permission_level += 1
            if ctx.author.guild_permissions.kick_members: user_permission_level += 1
            if ctx.author == ctx.guild.owner: user_permission_level += 1
        if user_permission_level >= permission: return True
        else:
            if user_permission_level == Permission.DIRECT_MESSAGES: await ctx.send("You have to be in a server to use this command.", ephemeral=True)
            else: await ctx.send("You do not have permission to use this command.", ephemeral=True)
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

    # This is called on every user interaction
    def interact(self, interaction: discord.Interaction):
        if interaction.user != self.original_author: raise
        self.timer.restart()

    # Timer to close command dialogues after one minute
    @tasks.loop(seconds=60.0, count=1) # Dummy loop that can be reset and fires when 1 minute has passed
    async def timer(self): pass
    @timer.after_loop
    async def on_timeout(self):
        if self.timer.current_loop: await self.attached_message.edit(content="> Timed out; Closing dialogue.", embeds=[], view=None)

    def get_page(self) -> discord.Embed: ...


class Font:
    white = (255,255,255)
    dm_sans_24 = ImageFont.truetype("./features/resources/fonts/DM Sans Black.ttf", size=24/3*4)
    gg_sans_14 = ImageFont.truetype("./features/resources/fonts/GG Sans Normal.ttf", size=14/3*4)