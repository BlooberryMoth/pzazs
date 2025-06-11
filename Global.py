# Variables

prefix = '..'
try:
    with open("./token.txt") as token: token = fr'{token.read()}'
except ValueError: raise "Unable to load token from \"token.txt\"."
try:
    with open("./oauth-secret.txt") as secret: secret = fr'{secret.read()}'
except ValueError: raise "Unable to load secret from \"secret.txt\"."

activityText = fr"in dev mode"

# Imports, global variables, and methods

import discord, importlib, json, os, threading
from discord.ext import commands as cmds, tasks
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from pytz import timezone as tz

intents  = discord.Intents.default(); intents.members = intents.message_content = True
activity = discord.Activity(name=activityText, type=discord.ActivityType.playing)
Client   = cmds.Bot(command_prefix=prefix, intents=intents, activity=activity)

# Global variables

threads = []
commands = {}

none = discord.AllowedMentions.none()

# Global methods

def log(text: str) -> None: print(f'{dt.now().replace(microsecond=0)} LOG      {text}')

async def reply(content: str, embeds: list=[], view: discord.ui.View=None, m: discord.Message=None, c: cmds.Context=None, ephemeral: bool=False) -> discord.Message:
    if c: return await c.send(content, embeds=embeds, view=view, allowed_mentions=none, silent=True, ephemeral=ephemeral)
    else: return await m.reply(content, embeds=embeds, view=view, allowed_mentions=none, silent=True)

async def check_permission(message: discord.Message, permission: int=3, ctx: cmds.Context=None) -> bool:
    userPermissionLevel = 0
    if message.guild:
        userPermissionLevel += 1
        if message.author.guild_permissions.kick_members: userPermissionLevel += 1
        if message.author == message.guild.owner: userPermissionLevel += 1
    if userPermissionLevel >= permission: return True
    else:
        if ctx: await ctx.send("You do not have permission to use this command.", ephemeral=True)
        else: await message.reply("You do not have permission to use this command.", allowed_mentions=none, silent=True)
        return False
    

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


request_emoji_embed = discord.Embed(color=0x69a9d9,
                                    title="React to this message with the emoji you want to use",
                                    description="(PZazS has to have access to this emoji for this to work.)") \
.set_footer(text="Closing prmopt in 60s")