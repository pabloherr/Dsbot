import discord
import random
from math import ceil as cl
from discord.ext import commands
from pydantic import BaseModel
from database import db_client
from models.pipo import Pipo

class Pipos(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.mongo_client = db_client
        self.db = self.mongo_client["discord"] 

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
        
        
    @commands.command()
    async def combat(self, ctx, pipo_name: str):
        user1 = self.db["users"].find_one({"id": ctx.author.id})
        user2 = self.db["users"].find_one({"id": ctx.message.mentions[0].id})
        pipo1 = next((pipo for pipo in user1["pipos"] if pipo["name"] == pipo_name), None)
        if pipo1 is None:
            await ctx.send("Pipo not found")
            return
        else:
            await ctx.send(f"{pipo1['name']} is ready to fight!")
        pipo2 = random.choice(user2["pipos"])
        await ctx.send(f"{pipo2['name']} is ready to fight!")
        turn1 = 0
        turn2 = 0
        pipo1_hp = pipo1["hp"]
        pipo2_hp = pipo2["hp"]
        while pipo1["hp"] > 0 and pipo2["hp"] > 0:
            turn1 += pipo1["speed"]
            turn2 += pipo2["speed"]
            if turn1 >= 12 or turn2 >= 12:
                if turn1 >= 12 and turn2 < 12:
                    turn1 = 0
                    dmg = await fight(pipo1, pipo2)
                    await ctx.send(dmg)
                    pipo2["hp"] -= dmg
                    
                if turn2 >= 12 and turn1 < 12:
                    turn2 = 0
                    dmg = await fight(pipo2, pipo1)
                    pipo1["hp"] -= dmg
                    
                if turn1 >= 12 and turn2 >= 12:
                    if pipo1["speed"] > pipo2["speed"]:
                        turn1 = 0
                        dmg = await fight(pipo1, pipo2)
                        pipo2["hp"] -= dmg
                    elif pipo1["speed"] < pipo2["speed"]:
                        turn2 = 0
                        dmg = await fight(pipo2, pipo1)
                        pipo1_hp -= dmg
                        
                    else:
                        r = random.randint(0, 1)
                        if r == 0:
                            turn1 = 0
                            dmg = await fight(pipo1, pipo2)
                            pipo2["hp"] -= dmg
                        else:
                            turn2 = 0
                            dmg = await fight(pipo2, pipo1)
                            pipo1["hp"] -= dmg
                            
                await ctx.send(f"{pipo1['name']} HP: {pipo1["hp"]} {pipo2['name']} HP: {pipo2["hp"]}")
        if pipo1["hp"] <= 0:
            await ctx.send(f"{pipo1['name']} fainted!")
            await ctx.send(f"{pipo2['name']} wins!")
        else:
            await ctx.send(f"{pipo2['name']} fainted!")
            await ctx.send(f"{pipo1['name']} wins!")
            
            

async def setup(client):
    await client.add_cog(Pipos(client))
    

async def fight(pipo1: dict, pipo2: dict) -> int:
    print(pipo1)
    if pipo2["defence"] > pipo1["attack"]:
        dmg = pipo2["hp"] - cl(pipo1["attack"]/4)
        return dmg
    elif pipo2["defence"] == pipo1["attack"]:
        return pipo2["hp"] - cl(pipo1["attack"]/2)
    else:
        return pipo2["hp"] - pipo1["attack"]