import random
from discord.ext import commands
from database import db_client
from tools import damage, wild
from math import ceil as cl

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
        
        await self.precombat(ctx, pipo1, pipo2)
        
        winner = await self.fight(ctx, pipo1, pipo2)
        if winner == 'pipo1':
            await self.postgame(ctx, winner= pipo1, loser = pipo2, loser_to=True, user_win = user1, user_lose= user2, leaderboards=True)
        else:
            await self.postgame(ctx, pipo2, pipo1, loser_to=True, user_win= user2, user_lose= user1, leaderboards=True)
    
    #combat wild pipo
    @commands.command()
    async def wild_combat(self, ctx, pipo_name: str, zone: str):
        user = self.db["users"].find_one({"id": ctx.author.id})
        pipo1 = next((pipo for pipo in user["pipos"] if pipo["name"] == pipo_name), None)
        pipo2 = await wild(zone)
        
        await ctx.send(pipo2)
        await self.precombat(ctx, pipo1, pipo2)
        
        winner = await self.fight(ctx, pipo1, pipo2)
        
        if winner == 'pipo1':
            await self.postgame(ctx, winner= pipo1, loser = pipo2, user_win = user)
        if winner == 'pipo2':
            self.db["wild_pipos"].insert_one(pipo2)
            await self.postgame(ctx, winner= pipo2, loser = pipo1, loser_to=True)
    
    #combat other user
    @commands.command()
    async def combat(self, ctx, pipo1: str, pipo2:str, bet = 0):
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
        
        if user1["gold"] < bet or user2["gold"] < bet:
            await ctx.send("Not enough gold")
            return
        
        if pipo1 is None:
            await ctx.send("Pipo1 not found")
            return
        if pipo2 is None:
            await ctx.send("Pipo2 not found")
            return
        
        await ctx.send(f"{pipo1['name']} is ready to fight!")
        await ctx.send(f"{pipo2['name']} is ready to fight!")
        winner = await self.fight(ctx, pipo1, pipo2)
        
        if winner == 'pipo1':
            await self.postgame(winner=pipo1, loser=pipo2, loser_to=True, bet= bet, user_win= user1, user_lose= user2, leaderboards=True)
        else:
            await self.postgame(winner=pipo2, loser=pipo1, loser_to=True,bet= bet, user_win= user2,user_lose= user1, leaderboards=True)

    #combat pipo vs wild pipo
    @commands.command()
    async def wild_combat_def(self, ctx, pipo_name: str, wild_pipo: str):
        user = self.db["users"].find_one({"id": ctx.author.id})
        pipo1 = next((pipo for pipo in user["pipos"] if pipo["name"] == pipo_name), None)
        pipo2 = self.db["wild_pipos"].find_one({"name": wild_pipo})
        
        await self.precombat(ctx, pipo1, pipo2)
        
        winner = await self.fight(ctx, pipo1, pipo2)
        if winner == 'pipo1':
            await self.postgame(ctx,ctx,winner= pipo1, loser = pipo2, user_win = user)
            self.db["wild_pipos"].delete_one({"name": wild_pipo})
        else:
            await self.postgame(ctx, winner= pipo2, loser = pipo1, loser_to=True)
    
    #raid combat pipos vs mega pipo
    @commands.command()
    async def mega_raid(self, ctx,mega_pipo: str = None):
        user1 = None
        user2 = None
        user3 = None
        
        pipo1 = None
        pipo2 = None
        pipo3 = None
        
        users_to_confirm = []
        users_to_confirm.append(ctx.author.id)
        if ctx.message.mentions:
            for i in range(ctx.message.mentions):
                users_to_confirm.append(ctx.message.mentions[i])
        
        if len(users_to_confirm) > 3:
            await ctx.send("Too many users")
            return
        
        user1 = self.db["users"].find_one({"id": users_to_confirm[0]})
        pipo1 = user1["defender"]
        if len(users_to_confirm) > 1:
            user2 = self.db["users"].find_one({"id": users_to_confirm[1]})
            pipo2 = user2["defender"]
        if len(users_to_confirm) > 2:
            user3 = self.db["users"].find_one({"id": users_to_confirm[2]})
            pipo3 = user3["defender"]
        await ctx.send(f'The team going to the raid is:')
        
        
        if user1 is not None:
            if user1["defender"] is not None:
                if user1["tank"]:
                    await ctx.send(f'{user1["name"]} - Tank')
            await ctx.send(f"{pipo1['name']} ({pipo1['rarity']}) | Lvl:{pipo1['lvl']} \n{pipo1['hp']} HP \n{pipo1['attack']} ATK \n{pipo1['defense']} DEF \n{pipo1['speed']} SPD \nPassive: {pipo1['passive']}")
        if user2 is not None:
            if user2["defender"] is not None:
                if user2["tank"]:
                    await ctx.send(f'{user2["name"]} - Tank')
            await ctx.send(f"{pipo2['name']} ({pipo2['rarity']}) | Lvl:{pipo2['lvl']} \n{pipo2['hp']} HP \n{pipo2['attack']} ATK \n{pipo2['defense']} DEF \n{pipo2['speed']} SPD \nPassive: {pipo2['passive']}")
        if user3 is not None:
            if user3["defender"] is not None:
                if user3["tank"]:
                    await ctx.send(f'{user3["name"]} - Tank')
            await ctx.send(f"{pipo3['name']} ({pipo3['rarity']}) | Lvl:{pipo3['lvl']} \n{pipo3['hp']} HP \n{pipo3['attack']} ATK \n{pipo3['defense']} DEF \n{pipo3['speed']} SPD \nPassive: {pipo3['passive']}")
        
        
        for user_id in users_to_confirm:
            await ctx.send(f'<@{user_id}> confirm the fight with yes')
            
            def check(message):
                return message.author.id == user_id and message.content.lower() == 'yes'

            try:
                await self.client.wait_for('message', check=check, timeout=60.0)
            except TimeoutError:
                await ctx.send(f'<@{user_id}> do not confirm the fight.')
            else:
                await ctx.send(f'<@{user_id}> confirmed the fight.')
        await ctx.send('go')
    #precombat
    async def precombat(self, ctx, pipo1, pipo2):
        if pipo1 is None:
            await ctx.send("Pipo1 not found")
            return
        if pipo2 is None:
            await ctx.send("Pipo2 not found")
            return
        
        await ctx.send(f"{pipo1['name']} is ready to fight!")
        await ctx.send(f"{pipo2['name']} is ready to fight!")
    
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
                    await ctx.send(f"   {pipo1['name']} attacks! ")
                    await ctx.send(f"   Dealing {dmg} damage!")
                    
                #pipo2 attacks
                if turn2 >= 12 and turn1 < 12:
                    turn2 = 0
                    dmg = await damage(pipo2, pipo1)
                    pipo1["hp"] -= dmg
                    await ctx.send(f"   {pipo2['name']} attacks!")
                    await ctx.send(f"   Dealing {dmg} damage!")
                    
                #both attack
                ff_damage = cl(pipo1["attack"]/2)
                ff_damage = cl(pipo2["attack"]/2)
                if turn1 >= 12 and turn2 >= 12:
                    p1_vel = pipo1["speed"]
                    p2_vel = pipo2["speed"]
                    if pipo1["passive"] == "Fight Fist":
                        pipo1["attack"] += ff_damage
                        p1_vel += 200
                    if pipo2["passive"] == "Fight Fist":
                        pipo1["attack"] += ff_damage
                        p2_vel += 200
                    #pipo1 faster
                    if p1_vel > p2_vel:
                        turn1 = 0
                        turn2 = 0
                        dmg = await damage(pipo1, pipo2)
                        pipo2["hp"] -= dmg
                        
                        if pipo2["hp"] > 0:
                            dmg = await damage(pipo2, pipo1)
                            pipo1["hp"] -= dmg
                        await ctx.send(f"   {pipo1['name']} it's faster!")
                        await ctx.send(f"   {pipo1['name']} deals {dmg} damage!")
                        await ctx.send(f"   {pipo2['name']} deals {dmg} damage!")
                        
                    #pipo2 faster
                    elif p1_vel < p2_vel:
                        turn1 = 0
                        turn2 = 0
                        dmg = await damage(pipo2, pipo1)
                        pipo1["hp"] -= dmg
                        
                        if pipo1["hp"] > 0:
                            dmg = await damage(pipo1, pipo2)
                            pipo2["hp"] -= dmg
                        await ctx.send(f"   {pipo2['name']} it's faster!")
                        await ctx.send(f"   {pipo2['name']} deals {dmg} damage!")
                        await ctx.send(f"   {pipo1['name']} deals {dmg} damage!")
                    
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
                            await ctx.send(f"   {pipo1['name']} deals {dmg} damage!")
                            await ctx.send(f"   {pipo2['name']} deals {dmg} damage!")
                        
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
                            await ctx.send(f"   {pipo2['name']} deals {dmg} damage!")
                            await ctx.send(f"   {pipo1['name']} deals {dmg} damage!")
                
                if pipo1["passive"] == "Fight Fist":
                    pipo1["attack"] -= ff_damage
                if pipo2["passive"] == "Fight Fist":
                    pipo2["attack"] -= ff_damage        
                
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
    
    #exp gain and gold after combat and leaderboards
    async def postgame(self, ctx, winner, loser, loser_to = False, bet = 0, user_win = None, user_lose = None, leaderboards = False):
        
        exp_gold = {1:2, 2:5, 3:8, 4:10, 5:15, 6:20, 7:32, 8:50, 9:80, 10:100}
        exp = exp_gold[loser["lvl"]]
        gold = exp_gold[loser["lvl"]]
        if bet > 0:
            gold = bet
            
        
        #gold
        self.db["users"].update_one({"id": user_win["id"]}, {"$inc": {"gold": gold}})
        await ctx.send(f"{user_win['name']} gained {gold} gold")
        
        #exp
        user = self.db["users"].find_one({"id": user_win["id"]})
        pipo = next((pipo for pipo in user["pipos"] if pipo["name"] == winner["name"]), None)
        pipo["exp"] += exp
        self.db["users"].update_one({"id": user_win["id"]}, {"$set": {"pipos": user["pipos"]}})
        await ctx.send(f"{winner['name']} gained {exp} exp")
        
        #loser exp
        if loser_to:
            user = self.db["users"].find_one({"id": user_lose["id"]})
            pipo = next((pipo for pipo in user["pipos"] if pipo["name"] == loser["name"]), None)
            pipo["exp"] += exp
            self.db["users"].update_one({"id": user_lose["id"]}, {"$set": {"pipos": user["pipos"]}})
            await ctx.send(f"{loser['name']} gained {exp} exp")
        
        #leaderboards
        if leaderboards:
            if self.db["leaderboards"].find_one({"id": user_win["id"]}) is None:
                self.db["leaderboards"].insert_one({"id": user_win["id"], "points": exp})
            else:
                point = self.db["leaderboards"].find_one({"id": user_win["id"]})["points"] + exp
                self.db["leaderboards"].update_one({"id": user_win["id"]}, {"$set": {"points": point}})

    
async def setup(client):
    await client.add_cog(Combat(client))