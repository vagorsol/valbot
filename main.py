import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
intents.reactions = True

bot = commands.Bot(intents = intents)

# need on_raw_reaction_add and on_raw_reaction_remove