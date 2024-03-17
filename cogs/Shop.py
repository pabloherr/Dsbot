import datetime
import random
from discord.ext import commands, tasks
from database import db_client
from tools import random_pipo

class Shop(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.mongo_client = db_client
        self.db = self.mongo_client["discord"] 
        self.collection = self.db["pipo_shop"]
        self.collection2 = self.db["obj_shop"]
    
    # Show the shop
    @commands.command(brief='Show the shop where you can buy Pipos.',
                      aliases=['ps'])
    async def pipo_shop(self, ctx):
        await ctx.send("Welcome to the shop! Here you can buy Pipos with your gold.")
        await ctx.send("Type !buy_pipo and the name of the pipo to buy it.")
        await ctx.send("Here are the Pipos available: \n\n")
        await ctx.send(f"----------------------------------------------------------------------------------------")
        await ctx.send(f"{ctx.author} you have {self.db["users"].find_one({"id": ctx.author.id})["gold"]} gold.")
        
        for i, pipo in enumerate(self.collection.find()):
            await ctx.send(f"----------------------------------------------------------------------------------------")
            await ctx.send(f"{i+1}. {pipo["name"]}  ({pipo["rarity"]}) \n{pipo["hp"]} HP \n{pipo["attack"]} ATK \n{pipo["defense"]} DEF\n{pipo["speed"]} SPD \nPassive:{pipo["passive"]} \nPrice:{pipo["price"]}\n\n")
        await ctx.send(f"----------------------------------------------------------------------------------------")
        if self.collection.count_documents({}) == 0:
            await ctx.send("OUT OF STOCK!")
            await ctx.send("Please wait fot towmorrow to restock the shop.\n\n")
            
        await ctx.send("Type !restock to restock the shop for 50 gold.")
    
    # Buy a pipo
    @commands.command(brief='Buy a Pipo from the shop. !buy_pipo <pipo_name>',
                      aliases=['bp'])
    async def buy_pipo(self, ctx, pipo_number: str):
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
    @commands.command(brief='Restock the shop for 50 gold.')
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
    
    # Show the items shop
    @commands.command(brief='Show the shop where you can buy items.',
                      alises=['is'])
    async def item_shop(self, ctx):
        await ctx.send("Welcome to the shop! Here you can buy items with your gold.")
        await ctx.send("Type !buy_item and the number of the item to buy it.")
        await ctx.send("Here are the items available: \n\n")
        
        for i, item in enumerate(self.collection2.find()):
            await ctx.send(f"{i+1}. {item["name"]} \nPrice:{item["price"]} \nStock:{item["stock"]}\n\n")
        
        if self.collection2.count_documents({}) == 0:
            await ctx.send("OUT OF STOCK!")
    
    # Buy an item
    @commands.command(brief='Buy an item from the shop. !buy_item <item_name>',
                      aliases=['bi'])
    async def buy_item(self, ctx, item_name: str, amount: int = 1):
        item = self.collection2.find_one({"name": item_name})
        if amount > self.collection2.find_one({"name": item_name})["stock"]:
            await ctx.send("Not enough stock")
            return
        
        if item is None:
            await ctx.send("Item not found")
            return
        
        user = self.db["users"].find_one({"id": ctx.author.id})
        
        if user["gold"] < item["price"]*amount:
            await ctx.send("Not enough gold")
            return
        
        user["gold"] -= item["price"]*amount
        if item["name"] not in user["items"]:
            user["items"][item["name"]] = 0
        user["backpack"][item["name"]] += amount
        
        self.db["users"].update_one({"id": ctx.author.id}, {"$set": user})
        self.collection2.update_one({"name": item_name}, {"$set": {"stock": item["stock"] - amount}})
        
        await ctx.send(f"{item["name"]} bought!")
    
    
async def setup(client):
    await client.add_cog(Shop(client))
