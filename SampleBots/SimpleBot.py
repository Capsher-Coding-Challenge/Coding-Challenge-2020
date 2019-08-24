import os
import discord
from discord.ext import commands

# load token into shell environment variables
# ex. export DISCORD_BOT_TOKEN="<insert_token_here>"
token = os.environ['DISCORD_BOT_TOKEN']

bot = commands.Bot(command_prefix='>')

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

# This token should be your bot token from discord
bot.run(token)
