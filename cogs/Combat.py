import random
from discord.ext import commands
from database import db_client
from tools import damage, wild

class Combat(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.mongo_client = db_client
        self.db = self.mongo_client["discord"]


    #combat defender
    @commands.command()
    async def combat_def(self, ctx, pipo_name: str):
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
        await self.fight(ctx, pipo1, pipo2)
    
    #combat wild pipo
    @commands.command()
    async def wild_combat(self, ctx, pipo_name: str, zone: str):
        user = self.db["users"].find_one({"id": ctx.author.id})
        pipo1 = next((pipo for pipo in user["pipos"] if pipo["name"] == pipo_name), None)
        pipo2 = await wild(zone)
        await ctx.send(pipo2)
        if pipo2 == "Invalid zone":
            await ctx.send("Invalid zone")
            return
        if pipo1 is None:
            await ctx.send("Pipo1 not found")
            return
        
        await ctx.send(f"{pipo1['name']} is ready to fight!")
        await ctx.send(f"{pipo2['name']} is ready to fight!")
        winner = await self.fight(ctx, pipo1, pipo2)
        if winner == 'pipo2':
            self.db["wild_pipos"].insert_one(pipo2)
    
    #combat other user
    @commands.command()
    async def combat(self, ctx, pipo1: str, pipo2:str):
        await ctx.send(f'{ctx.message.mentions[0].name} confirm the fight with yes or no')
        def check(m):
            return m.author == ctx.message.mentions[0] and m.content.lower() in ['yes', 'no']
        
        try:
            msg = await self.client.wait_for('message', check=check, timeout=30)
        except TimeoutError:
            await ctx.send('Timeout')
            return
        if msg.content.lower() == 'no':
            await ctx.send('Combat canceled')
            return
        await ctx.send(f'{ctx.message.mentions[0].name} accepted the fight')
        
        user1 = self.db["users"].find_one({"id": ctx.author.id})
        user2 = self.db["users"].find_one({"id": ctx.message.mentions[0].id})
        pipo1 = next((pipo for pipo in user1["pipos"] if pipo["name"] == pipo1), None)
        pipo2 = next((pipo for pipo in user2["pipos"] if pipo["name"] == pipo2), None)
        
        if pipo1 is None:
            await ctx.send("Pipo1 not found")
            return
        if pipo2 is None:
            await ctx.send("Pipo2 not found")
            return
        
        await ctx.send(f"{pipo1['name']} is ready to fight!")
        await ctx.send(f"{pipo2['name']} is ready to fight!")
        await self.fight(ctx, pipo1, pipo2)
    
    
    
    #combat pipo vs pipo
    async def fight(self, ctx, pipo1, pipo2):
        turn1 = 0
        turn2 = 0
        round = 0
        pipo1_hp = pipo1["hp"]
        pipo2_hp = pipo2["hp"]
        
        while pipo1["hp"] > 0 and pipo2["hp"] > 0:
            await ctx.send(f".")
            turn1 += pipo1["speed"]
            turn2 += pipo2["speed"]
            
            #fight
            if turn1 >= 12 or turn2 >= 12:
                round +=1
                await ctx.send(f"ROUND {round}")
                
                #pipo1 attacks
                if turn1 >= 12 and turn2 < 12:
                    turn1 = 0
                    dmg = await damage(pipo1, pipo2)
                    pipo2["hp"] -= dmg
                    await ctx.send(f"   {pipo1['name']} attacks!")
                    
                #pipo2 attacks
                if turn2 >= 12 and turn1 < 12:
                    turn2 = 0
                    dmg = await damage(pipo2, pipo1)
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
                        dmg = await damage(pipo1, pipo2)
                        pipo2["hp"] -= dmg
                        dmg = await damage(pipo2, pipo1)
                        pipo1["hp"] -= dmg
                        await ctx.send(f"   {pipo1['name']} it's faster!")
                        
                    #pipo2 faster
                    elif p1_vel < p2_vel:
                        turn1 = 0
                        turn2 = 0
                        dmg = await damage(pipo2, pipo1)
                        pipo1["hp"] -= dmg
                        dmg = await damage(pipo1, pipo2)
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
                            dmg = await damage(pipo1, pipo2)
                            pipo2["hp"] -= dmg
                            
                            if pipo2["hp"] > 0:
                                dmg = await damage(pipo2, pipo1)
                                pipo1["hp"] -= dmg
                                
                            await ctx.send(f"   {pipo1['name']} attacks fist!")
                        
                        #pipo2 attacks first
                        else:
                            turn1 = 0
                            turn2 = 0
                            dmg = await damage(pipo2, pipo1)
                            pipo1["hp"] -= dmg
                            
                            if pipo1["hp"] > 0:
                                dmg = await damage(pipo1, pipo2)
                                pipo2["hp"] -= dmg
                                
                            await ctx.send(f"   {pipo2['name']} attacks fist!")
                            
                            
                await ctx.send(f"   {pipo1['name']} HP: {pipo1['hp']} {pipo2['name']} HP: {pipo2['hp']}")
        
        
        await ctx.send("COMBAT ENDED!")
        if pipo1["hp"] <= 0:
            await ctx.send(f"   {pipo1['name']} fainted!")
            await ctx.send(f"   {pipo2['name']} wins!")
            pipo1["hp"] = pipo1_hp
            pipo2["hp"] = pipo2_hp
            return 'pipo2'
        else:
            await ctx.send(f"   {pipo2['name']} fainted!")
            await ctx.send(f"   {pipo1['name']} wins!")
            pipo1["hp"] = pipo1_hp
            pipo2["hp"] = pipo2_hp
            return 'pipo1'

async def setup(client):
    await client.add_cog(Combat(client))