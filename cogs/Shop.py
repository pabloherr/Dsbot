import discord
import random
from discord.ext import commands
from database import db_client
from models.pipo import Pipo

class Shop(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.mongo_client = db_client
        self.db = self.mongo_client["discord"] 
        self.collection = self.db["shop"]
    
    @commands.command()
    async def shop(self, ctx):
        await ctx.send("Welcome to the shop! Here you can buy Pipos with your cash.")
        await ctx.send("Type !buy and de number of the pipo to buy it.")
        await ctx.send("Here are the Pipos available:")
        for i in range(2):
            await ctx.send(random_pipo())
            self.collection.insert_one(random_pipo())


async def setup(client):
    await client.add_cog(Shop(client))

# Funtion to create a new pipo
async def random_pipo() -> Pipo:
    rarity = random.choice(["common", "uncommon", "rare"])
    if rarity == "common":
        stats = [1, 1, 2, 3]
    elif rarity == "uncommon":
        stats = [1, 1, 2, 4]
    else:
        stats = [2, 2, 3, 4]
    random.shuffle(stats)
    pipo_name = "Pipo_" + str(random.randint(1, 100))
    
    pipo = Pipo(rarity=rarity, name=pipo_name,
                hp=5+stats[0], attack=stats[1], 
                defense=stats[2], speed=stats[3])
    return pipo.dict()