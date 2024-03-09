
import discord
from discord.ext import commands
from database import db_client
import os

mongo_client = db_client
db = mongo_client["discord"]
time = db["time"]
leaderboard = db["leaderboard"]


intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix='!', intents=intents)

# Load all cogs
@client.event
async def setup_hook():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await client.load_extension(f'cogs.{filename[:-3]}')
            print(f"Loaded Cog: {filename[:-3]}")
        else:
            print("Unable to load pycache folder.")


client.run('MTIxMjk5MzYyMDc0ODAwOTQ4Mg.GZdqg0.DfFaXTyo1peQQuL_7UvDRywrSeIJBczsO8Mh34') # Replace with your own token.