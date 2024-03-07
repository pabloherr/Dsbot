import discord
import random
from discord.ext import commands
from database import db_client
from models.pipo import Pipo
from tools import random_pipo

class Shop(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.mongo_client = db_client
        self.db = self.mongo_client["discord"] 
        self.collection = self.db["shop"]
    
    
    # Show the shop
    @commands.command()
    async def shop(self, ctx):
        await ctx.send("Welcome to the shop! Here you can buy Pipos with your cash.")
        await ctx.send("Type !buy and de number of the pipo to buy it.")
        await ctx.send("Here are the Pipos available:")
        if self.collection.count_documents({}) < 3:
            r = 3 - self.collection.count_documents({})
            for i in range(r):
                pipo = await random_pipo()
                self.collection.insert_one(pipo)
        for i, pipo in enumerate(self.collection.find()):
            await ctx.send(f"{i+1}. {pipo["name"]} {pipo["rarity"]} \n{pipo["hp"]} HP \n{pipo["attack"]}ATK \n{pipo["defense"]} DEF \n{pipo["speed"]} SPD \n Passive:{pipo["passive"]} \nPrice:{pipo["price"]}\n\n")
        await ctx.send("Type !restock to restock the shop for 10 cash.")
    
    # Buy a pipo
    @commands.command()
    async def buy(self, ctx, pipo_number: str):
        pipo = self.collection.find_one({"name": pipo_number})
        if pipo is None:
            await ctx.send("Pipo not found")
            return
        user = self.db["users"].find_one({"id": ctx.author.id})
        if user["cash"] < 1:
            await ctx.send("Not enough cash")
            return
        user["cash"] -= 1
        user["pipos"].append(pipo)
        self.db["users"].update_one({"id": ctx.author.id}, {"$set": user})
        self.collection.delete_one({"name": pipo_number})
        await ctx.send(f"{pipo["name"]} bought!")
    
    # Restock the shop
    @commands.command()
    async def restock(self, ctx):
        if self.db["users"].find_one({"id": ctx.author.id})["cash"] < 10:
            await ctx.send("Not enough cash")
            return
        self.collection.delete_many({})
        for i in range(3):
            pipo = await random_pipo()
            self.collection.insert_one(pipo)
        user = self.db["users"].find_one({"id": ctx.author.id})
        user["cash"] -= 10
        await ctx.send("Shop restocked!")

async def setup(client):
    await client.add_cog(Shop(client))
