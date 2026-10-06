from discord.ext import commands


DIRECT_MESSAGES = 0
USER = 1
MODERATOR = 2
SERVER_OWNER = 3

@staticmethod
async def check(ctx: commands.Context, permission: int=3) -> bool:
    user_permission_level = DIRECT_MESSAGES
    if ctx.guild:
        user_permission_level += 1
        if ctx.author.guild_permissions.kick_members: user_permission_level += 1
        if ctx.author == ctx.guild.owner: user_permission_level += 1
    if user_permission_level >= permission: return True
    else:
        if user_permission_level == DIRECT_MESSAGES: await ctx.send("You have to be in a server to use this command.", ephemeral=True)
        else: await ctx.send("You do not have permission to use this command.", ephemeral=True)
        return False