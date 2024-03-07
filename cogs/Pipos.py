import random
from discord.ext import commands
from database import db_client
from models.pipo import Pipo
from tools import fight, random_pipo

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
    async def lvlup(self, ctx, pipo_name: str, stat1, stat2):
        
        lvl = {1:0, 2:10, 3:30, 4:60, 5:120, 6:240, 7:480, 8:960, 9:1920, 10:3840}
        
        if self.collection.find_one({"name": pipo_name}) is None:
        
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
        else:
            pipo = self.collection.find_one({"name": pipo_name})
            
        if stat1 not in ["hp", "attack", "defense", "speed"] or stat2 not in ["hp", "attack", "defense", "speed"]:
            await ctx.send("Invalid stats")
            return
        
        if stat1 == stat2:
            await ctx.send("Stats must be different")
            return
        
        if stat1 == "hp":
            pipo["max_hp"] += 1
            stat1 = "max_hp"
        elif stat2 == "hp":
            pipo["max_hp"] += 1
            stat2 = "max_hp"
        pipo[stat1] += 1
        pipo[stat2] += 1
        pipo["hp"] = pipo["max_hp"]
        pipo["lvl"] += 1
        pipo["exp"] = 0
        if self.collection.find_one({"name": pipo_name}) is None:
            self.db["users"].update_one({"id": ctx.author.id}, {"$set": user})
            await ctx.send(f"{pipo_name} lvl up to {pipo['lvl']}")
        else:
            self.collection.update_one({"name": pipo_name}, {"$set": pipo})

    # Command to create a wild pipo
    @commands.command()
    async def wild(self, ctx, zone: str = "forest"):
        
        if zone not in ["forest", "desert", "mountain"]:
            await ctx.send("Invalid zone")
            await ctx.send("Valid zones: forest, desert, mountain")
            return
        pipo = await random_pipo(wild=True)
        self.collection.insert_one(pipo)
        pipo = self.collection.find_one({"name": pipo["name"]})
        if zone == "forest":
            lvl = random.randint(1, 3)
            for i in range(lvl-1):
                stat1 = random.choice(["hp", "attack", "defense", "speed"])
                stat2 = random.choice(["hp", "attack", "defense", "speed"])
                while stat1 == stat2:
                    stat2 = random.choice(["hp", "attack", "defense", "speed"])
                await self.lvlup(ctx, pipo["name"], stat1, stat2)
        elif zone == "desert":
            lvl = random.randint(3, 5)
            for i in range(lvl):
                stat1 = random.choice(["hp", "attack", "defense", "speed"])
                stat2 = random.choice(["hp", "attack", "defense", "speed"])
                while stat1 == stat2:
                    stat2 = random.choice(["hp", "attack", "defense", "speed"])
                await self.lvlup(ctx, pipo["name"], stat1, stat2)
        else:
            lvl = random.randint(6, 9)
            for i in range(lvl):
                stat1 = random.choice(["hp", "attack", "defense", "speed"])
                stat2 = random.choice(["hp", "attack", "defense", "speed"])
                while stat1 == stat2:
                    stat2 = random.choice(["hp", "attack", "defense", "speed"])
                await self.lvlup(ctx, pipo["name"], stat1, stat2)

        
        await ctx.send(f"Wild pipo found! \n{pipo['name']} \n{pipo['rarity']} \nLvl:{lvl}")

    # Command to show wild pipos
    @commands.command()
    async def show_wild(self, ctx):
        pipos = self.collection.find({})
        for pipo in pipos:
            await ctx.send(f"{pipo['name']} \n{pipo['rarity']} \nLvl: {pipo['lvl']}")
    
async def setup(client):
    await client.add_cog(Pipos(client))