import random
import datetime
from discord.ext import commands, tasks
from database import db_client
from models.pipo import Pipo
from tools import lvlup, wild

class Pipos(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.mongo_client = db_client
        self.db = self.mongo_client["discord"]
        self.collection = self.db["wild_pipos"]
        self.collection2 = self.db["mega_pipos"]
        self.mega_pipo.start()
    
    def cog_unload(self):
        self.mega_pipo.cancel()
    
    
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
        
        lvl = {1:0, 2:10, 3:40, 4:80, 5:160, 6:320, 7:640, 8:1280, 9:2560, 10:5120}
            #  2:5  5:8   8:10  10:16  15:22 20:32   32:40 50:52    80:64   100
        
        
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
    
    # Weekly wild mega pipo
    @tasks.loop(hours=1)
    async def mega_pipo(self):
        if not self.db["time"].find_one({"id": "mega_pipo"}):
            self.db["time"].insert_one({"id": "mega_pipo", "time": datetime.datetime.now()})
        if self.db["time"].find_one({"id": "mega_pipo"})["time"] < datetime.datetime.now():
            self.db["time"].update_one({"id": "mega_pipo"}, {"$set": {"time": datetime.datetime.now() + datetime.timedelta(hours=168)}})
        if  self.collection2.count_documents({}) > 0:
            self.collection2.delete_many({})
        mega_zone = ["megaforest", "megadesert", "megamountain"] 
        for zone in mega_zone:
            pipo = await wild(zone)
            self.collection2.insert_one(pipo)
            self.collection2.update_one({"name": pipo["name"]}, {"$set": {"name": f"Mega {pipo['name']}"}})
    
    
async def setup(client):
    await client.add_cog(Pipos(client))