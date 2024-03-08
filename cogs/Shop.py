import discord
import random
import datetime
from discord.ext import commands, tasks
from database import db_client
from models.pipo import Pipo
from tools import random_pipo

class Shop(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.daily_shop.start()
        self.mongo_client = db_client
        self.db = self.mongo_client["discord"] 
        self.collection = self.db["shop"]
    
    def cog_unload(self):     
        self.daily_shop.cancel()
    
    # Restock the shop every 24 hours
    @tasks.loop(hours=1)
    async def daily_shop(self):
        if not self.db["time"].find_one({"id": "shop"}):
            self.db["time"].insert_one({"id": "shop", "time": datetime.datetime.now()})
        if self.db["time"].find_one({"id": "shop"})["time"] < datetime.datetime.now():
            self.db["time"].update_one({"id": "shop"}, {"$set": {"time": datetime.datetime.now() + datetime.timedelta(hours=24)}})
        self.collection.delete_many({})
        for i in range(6):
            pipo = await random_pipo()
            self.collection.insert_one(pipo)
    
    # Show the shop
    @commands.command()
    async def shop(self, ctx):
        await ctx.send("Welcome to the shop! Here you can buy Pipos with your gold.")
        await ctx.send("Type !buy and de number of the pipo to buy it.")
        await ctx.send("Here are the Pipos available: \n\n")
        
        for i, pipo in enumerate(self.collection.find()):
            await ctx.send(f"{i+1}. {pipo["name"]} {pipo["rarity"]} \n{pipo["hp"]} HP \n{pipo["attack"]}ATK \n{pipo["defense"]} DEF \n{pipo["speed"]} SPD \n Passive:{pipo["passive"]} \nPrice:{pipo["price"]}\n\n")
        
        if self.collection.count_documents({}) == 0:
            await ctx.send("OUT OF STOCK!")
            await ctx.send("Please wait fot towmorrow to restock the shop.\n\n")
            
        await ctx.send("Type !restock to restock the shop for 50 gold.")
    
    # Buy a pipo
    @commands.command()
    async def buy(self, ctx, pipo_number: str):
        pipo = self.collection.find_one({"name": pipo_number})
        
        if pipo is None:
            await ctx.send("Pipo not found")
            return
        
        user = self.db["users"].find_one({"id": ctx.author.id})
        
        if user["gold"] < pipo["price"]:
            await ctx.send("Not enough gold")
            return
        
        user["gold"] -= pipo["price"]
        user["pipos"].append(pipo)
        self.db["users"].update_one({"id": ctx.author.id}, {"$set": user})
        self.collection.delete_one({"name": pipo_number})
        
        await ctx.send(f"{pipo["name"]} bought!")
    
    # Restock the shop
    @commands.command()
    async def restock(self, ctx):
        
        if self.db["users"].find_one({"id": ctx.author.id})["gold"] < 50:
            await ctx.send("Not enough gold")
            return
        
        self.collection.delete_many({})
        
        for i in range(6):
            pipo = await random_pipo()
            self.collection.insert_one(pipo)
            
        user = self.db["users"].find_one({"id": ctx.author.id})
        user["gold"] -= 50
        await ctx.send("Shop restocked!")
        await self.shop(ctx)


async def setup(client):
    await client.add_cog(Shop(client))
