#MTIxMjk5MzYyMDc0ODAwOTQ4Mg.GajbKv.xF5D8xWQeqhs4NmTossIx4OwZdzvOwZaLpbxd0
#137439348800
import discord
from discord.ext import commands
#from client import client
import os



#db = client['discord']
#'users = db['users']
intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix='!', intents=intents)

# Cargar la extensión
#initial_extensions = []
#
#for filename in os.listdir('./cogs'):
#    if filename.endswith('.py'):
#        initial_extensions.append(f'cogs.{filename[:-3]}')

@client.event
async def setup_hook():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await client.load_extension(f'cogs.{filename[:-3]}')
            print(f"Loaded Cog: {filename[:-3]}")
        else:
            print("Unable to load pycache folder.")

#print(initial_extensions)
#if __name__ == '__main__':
#    for extension in initial_extensions:
#        client.load_extension(extension)
#        print(f'Loaded {extension}')


client.run('MTIxMjk5MzYyMDc0ODAwOTQ4Mg.GajbKv.xF5D8xWQeqhs4NmTossIx4OwZdzvOwZaLpbxd0') # Replace with your own token.