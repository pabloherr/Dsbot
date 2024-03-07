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
        
    #combat pipos
    @commands.command()
    async def combat(self, ctx, pipo_name: str):
        user1 = self.db["users"].find_one({"id": ctx.author.id})
        user2 = self.db["users"].find_one({"id": ctx.message.mentions[0].id})
        pipo1 = next((pipo for pipo in user1["pipos"] if pipo["name"] == pipo_name), None)
        pipo2 = user2["defender"]
        
        if pipo1 is None:
            await ctx.send("Pipo1 not found")
            return
        if pipo2 is None:
            await ctx.send("Pipo2 not found")
            return
        
        await ctx.send(f"{pipo1['name']} is ready to fight!")
        await ctx.send(f"{pipo2['name']} is ready to fight!")
        turn1 = 0
        turn2 = 0
        pipo1_hp = pipo1["hp"]
        pipo2_hp = pipo2["hp"]
        round = 0
        
        while pipo1["hp"] > 0 and pipo2["hp"] > 0:
            round +=1
            await ctx.send(f"ROUND: {round}")
            turn1 += pipo1["speed"]
            turn2 += pipo2["speed"]
            
            #fight
            if turn1 >= 12 or turn2 >= 12:
                
                #pipo1 attacks
                if turn1 >= 12 and turn2 < 12:
                    turn1 = 0
                    dmg = await fight(pipo1, pipo2)
                    pipo2["hp"] -= dmg
                    await ctx.send(f"   {pipo1['name']} attacks!")
                    
                #pipo2 attacks
                if turn2 >= 12 and turn1 < 12:
                    turn2 = 0
                    dmg = await fight(pipo2, pipo1)
                    pipo1["hp"] -= dmg
                    await ctx.send(f"   {pipo2['name']} attacks!")
                    
                #both attack
                if turn1 >= 12 and turn2 >= 12:
                    p1_vel = pipo1["speed"]
                    p2_vel = pipo2["speed"]
                    if pipo1["passive"] == "Fight Fist":
                        p1_vel += 20
                    if pipo2["passive"] == "Fight Fist":
                        p2_vel += 20
                    #pipo1 faster
                    if p1_vel > p2_vel:
                        turn1 = 0
                        turn2 = 0
                        dmg = await fight(pipo1, pipo2)
                        pipo2["hp"] -= dmg
                        dmg = await fight(pipo2, pipo1)
                        pipo1["hp"] -= dmg
                        await ctx.send(f"   {pipo1['name']} it's faster!")
                        
                    #pipo2 faster
                    elif p1_vel < p2_vel:
                        turn1 = 0
                        turn2 = 0
                        dmg = await fight(pipo2, pipo1)
                        pipo1["hp"] -= dmg
                        dmg = await fight(pipo1, pipo2)
                        pipo2["hp"] -= dmg
                        await ctx.send(f"   {pipo2['name']} it's faster!")
                    
                    #speed tie
                    else:
                        await ctx.send("    Speed tie!")
                        r = random.randint(0, 1)
                        
                        #pipo1 attacks first
                        if r == 0:
                            turn1 = 0
                            turn2 = 0
                            dmg = await fight(pipo1, pipo2)
                            pipo2["hp"] -= dmg
                            
                            if pipo2["hp"] > 0:
                                dmg = await fight(pipo2, pipo1)
                                pipo1["hp"] -= dmg
                                
                            await ctx.send(f"   {pipo1['name']} attacks fist!")
                        
                        #pipo2 attacks first
                        else:
                            turn1 = 0
                            turn2 = 0
                            dmg = await fight(pipo2, pipo1)
                            pipo1["hp"] -= dmg
                            
                            if pipo1["hp"] > 0:
                                dmg = await fight(pipo1, pipo2)
                                pipo2["hp"] -= dmg
                                
                            await ctx.send(f"   {pipo2['name']} attacks fist!")
                            
                            
                await ctx.send(f"   {pipo1['name']} HP: {pipo1["hp"]} {pipo2['name']} HP: {pipo2["hp"]}")
        
        await ctx.send("COMBAT ENDED!")
        if pipo1["hp"] <= 0:
            await ctx.send(f"   {pipo1['name']} fainted!")
            await ctx.send(f"   {pipo2['name']} wins!")
        else:
            await ctx.send(f"   {pipo2['name']} fainted!")
            await ctx.send(f"   {pipo1['name']} wins!")
        pipo1["hp"] = pipo1_hp
        pipo2["hp"] = pipo2_hp
        
async def setup(client):
    await client.add_cog(Pipos(client))
    

async def fight(pipoatk: dict, pipodef: dict) -> int:
    lethal = 0
    if pipoatk['passive'] == "Feel No Pain":
        feel = True
    if pipoatk['passive'] == "Lethal Hits":
        lethal = 2
    
    if pipodef['passive'] == "Invulnerable":
        inv = random.randint(0, 1)
        if inv == 0:
            return 0
        return pipoatk['attack']
    
    if pipodef['defense'] > pipoatk['attack']+lethal:
        dmg = cl(pipoatk['attack']/4)
        if feel:
            for i in range(dmg):
                r = random.randint(1, 6)
                if r == 6:
                    dmg -= 1
        return dmg
    
    elif pipodef['defense'] == pipoatk['attack']+lethal:
        dmg =  cl(pipoatk['attack']/2)
        if feel:
            for i in range(dmg):
                r = random.randint(1, 6)
                if r == 6:
                    dmg -= 1
        return dmg
    else:
        dmg =  pipoatk['attack']
        if feel:
            for i in range(dmg):
                r = random.randint(1, 6)
                if r == 6:
                    dmg -= 1
        return dmg