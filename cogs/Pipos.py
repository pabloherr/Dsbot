import random
from discord.ext import commands
from database import db_client
from models.pipo import Pipo
from tools import lvlup

class Pipos(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.mongo_client = db_client
        self.db = self.mongo_client["discord"]
        self.collection = self.db["wild_pipos"]

    # Rename the pipos
    @commands.command()
    async def rename(self, ctx, pipo_name: str, new_name: str):
        user = self.db["users"].find_one({"id": ctx.author.id})
        pipo = next((pipo for pipo in user["pipos"] if pipo["name"] == pipo_name), None)
        if pipo is None:
            await ctx.send("Pipo not found")
            return
        pipo["name"] = new_name
        self.db["users"].update_one({"id": ctx.author.id}, {"$set": user})
        await ctx.send(f"{pipo_name} renamed to {new_name}")

    #Lvl up the pipos
    @commands.command()
    async def levelup(self, ctx, pipo_name: str, stat1, stat2):
        
        lvl = {1:0, 2:10, 3:30, 4:60, 5:120, 6:240, 7:480, 8:960, 9:1920, 10:3840}
        
        
        user = self.db["users"].find_one({"id": ctx.author.id})
        pipo = next((pipo for pipo in user["pipos"] if pipo["name"] == pipo_name), None)
        if pipo is None:
            await ctx.send("Pipo not found")
            return
        
        if pipo["lvl"] == 10:
            await ctx.send("Pipo is max lvl")
            return
        
        if pipo["exp"] < lvl[pipo["lvl"]]:
            await ctx.send("Not enough exp")
            return
        
        if stat1 not in ["hp", "attack", "defense", "speed"] or stat2 not in ["hp", "attack", "defense", "speed"]:
            await ctx.send("Invalid stats")
            return
        
        if stat1 == stat2:
            await ctx.send("Stats must be different")
            return
        
        pipo = await lvlup(user, pipo, stat1, stat2)
        self.db["users"].update_one({"id": ctx.author.id}, {"$set": user})
        await ctx.send(f"{pipo_name} lvl up! \n{stat1} +1 \n{stat2} +1")

    # Command to show wild pipos
    @commands.command()
    async def show_wild(self, ctx):
        pipos = self.collection.find({})
        for pipo in pipos:
            await ctx.send(f"{pipo['name']} \n{pipo['rarity']} \nLvl: {pipo['lvl']}")
    
async def setup(client):
    await client.add_cog(Pipos(client))