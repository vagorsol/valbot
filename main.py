import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
intents.reactions = True

bot = commands.Bot(intents = intents)

@bot.event
async def on_ready():
    Channel = client.get_channel(CHANNEL_ID)

# need on_raw_reaction_add and on_raw_reaction_remove
@bot.event
async def on_reaction_add(reaction, user):
    # TODO