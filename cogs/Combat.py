import random
from discord.ext import commands
from database import db_client
from tools import damage, wild, velocity
from math import ceil as cl

class Combat(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.mongo_client = db_client
        self.db = self.mongo_client["discord"]


    #combat defender
    @commands.command(brief='Combat the defender pipo of another user. !combat_def <your_pipo_name> <@user>')
    async def combat_def(self, ctx, pipo_name: str):
        user1 = self.db["users"].find_one({"id": ctx.author.id})
        user2 = self.db["users"].find_one({"id": ctx.message.mentions[0].id})
        pipo1 = next((pipo for pipo in user1["pipos"] if pipo["name"] == pipo_name), None)
        pipo2 = user2["defender"]
        
        await self.precombat(ctx, pipo1, pipo2)
        
        winner, pipo1["hp"], pipo2["hp"] = await self.fight(ctx, pipo1, pipo2)
        self.db["users"].update_one({"id": user1["id"]}, {"$set": user1})
        
        if winner == 'pipo1':
            await self.postgame(ctx, winner= pipo1, loser = pipo2, loser_to=True, user_win = user1, user_lose= user2, leaderboards=True)
        else:
            await self.postgame(ctx, pipo2, pipo1, loser_to=True, user_win= user2, user_lose= user1, leaderboards=True)
    
    #combat wild pipo
    @commands.command(brief='Combat a wild pipo. !wild_combat <your_pipo_name> <zone>(forest, desert, mountain)')
    async def wild_combat(self, ctx, pipo_name: str, zone: str):
        user = self.db["users"].find_one({"id": ctx.author.id})
        pipo1 = next((pipo for pipo in user["pipos"] if pipo["name"] == pipo_name), None)
        pipo2 = await wild(zone)
        
        await ctx.send(pipo2)
        await self.precombat(ctx, pipo1, pipo2)
        
        winner, pipo1["hp"], pipo2["hp"] = await self.fight(ctx, pipo1, pipo2)
        self.db["users"].update_one({"id": user["id"]}, {"$set": user})
        if winner == 'pipo1':
            await self.postgame(ctx, winner= pipo1, loser = pipo2, user_win = user)
        if winner == 'pipo2':
            self.db["wild_pipos"].insert_one(pipo2)
    
    #combat other user
    @commands.command(brief='Combat another user. !combat <your_pipo_name> <other_user_pipo_name> <@user>')
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
        winner, pipo1["hp"], pipo2["hp"] = await self.fight(ctx, pipo1, pipo2)
        
        self.db["users"].update_one({"id": user1["id"]}, {"$set": user1})
        self.db["users"].update_one({"id": user2["id"]}, {"$set": user2})
        
        if winner == 'pipo1':
            await self.postgame(winner=pipo1, loser=pipo2, loser_to=True, bet= bet, user_win= user1, user_lose= user2, leaderboards=True)
        else:
            await self.postgame(winner=pipo2, loser=pipo1, loser_to=True,bet= bet, user_win= user2,user_lose= user1, leaderboards=True)
    
    #combat pipo vs wild pipo of the list of survivors
    @commands.command(brief='Combat a wild pipo who survive a combat. !wild_combat <your_pipo_name> <wild_pipo_name>')
    async def wild_combat_def(self, ctx, pipo_name: str, wild_pipo: str):
        user = self.db["users"].find_one({"id": ctx.author.id})
        pipo1 = next((pipo for pipo in user["pipos"] if pipo["name"] == pipo_name), None)
        pipo2 = self.db["wild_pipos"].find_one({"name": wild_pipo})
        
        await self.precombat(ctx, pipo1, pipo2)
        
        winner, pipo1_hp, pipo2_hp = await self.fight(ctx, pipo1, pipo2)
        
        pipo1["hp"] = pipo1_hp
        await ctx.send(f"{pipo1['name']} HP: {pipo1['hp']}")
        self.db["users"].update_one({"id": user["id"]}, {"$set": user})
        if winner == 'pipo1':
            await self.postgame(ctx,ctx,winner= pipo1, loser = pipo2, user_win = user)
            self.db["wild_pipos"].delete_one({"name": wild_pipo})
    
    #raid combat pipos vs mega pipo
    @commands.command(brief='Combat a mega pipo. !mega_raid <mega_pipo_name> <@user1> <@user2>',
                      description='The mega pipo is a boss who can be defeated by a team of 3 pipos of 3 different users')
    async def mega_raid(self, ctx,mega_pipo: str = None):
        user1 = None
        user2 = None
        user3 = None
        
        pipo1 = None
        pipo2 = None
        pipo3 = None
        #get users and pipos
        users_to_confirm = []
        users_to_confirm.append(ctx.author.id)
        if ctx.message.mentions:
            for i in range(ctx.message.mentions):
                users_to_confirm.append(ctx.message.mentions[i])
        if len(users_to_confirm) < 3:
            await ctx.send("Not enough users")
        if len(users_to_confirm) > 3:
            await ctx.send("Too many users")
            return
        #get pipos
        user1 = self.db["users"].find_one({"id": users_to_confirm[0]})
        pipo1 = user1["defender"]
        if len(users_to_confirm) > 1:
            user2 = self.db["users"].find_one({"id": users_to_confirm[1]})
            pipo2 = user2["defender"]
        if len(users_to_confirm) > 2:
            user3 = self.db["users"].find_one({"id": users_to_confirm[2]})
            pipo3 = user3["defender"]
        await ctx.send(f'The team going to the raid is:')
        
        #show pipos
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
        
        #confirm
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
        
        fight, pipo1["hp"], pipo2["hp"], pipo3["hp"] = await self.raid(ctx, pipo1, pipo2, pipo3, mega_pipo)
        self.db["users"].update_one({"id": user1["id"]}, {"$set": user1})
        self.db["users"].update_one({"id": user2["id"]}, {"$set": user2})
        self.db["users"].update_one({"id": user3["id"]}, {"$set": user3})
        
        mega_pipo["lvl"] = mega_pipo["lvl"]/2
        if fight:
            await self.postgame(ctx, winner= pipo1, loser = mega_pipo, user_win = user1)
            if pipo2 is not None:
                await self.postgame(ctx, winner= pipo2, loser = mega_pipo, user_win = user2)
            if pipo3 is not None:
                await self.postgame(ctx, winner= pipo3, loser = mega_pipo, user_win = user3)
    
    
    
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
    
    
    #combat [1:3]pipos vs [1:3]pipo
    async def raid(self, ctx, pipo1, pipo2, pipo3, mega_pipo):
        turn1 = 0
        turn2 = 0
        turn3 = 0
        turn_mega = 0
        round = 0
        tanks =[]
        dps = []
        if pipo1["tank"]:
            tanks.append(pipo1)
        else:
            dps.append(pipo1)
        if pipo2["tank"]:
            tanks.append(pipo2)
        else:
            dps.append(pipo2)
        if pipo3["tank"]:
            tanks.append(pipo3)
        else:
            dps.append(pipo3)
            
        def defender():
            defend = random.choices([0, 1], weights=[1, 3], k=1)
            if defend[0] == 1:
                return random.choice(tanks)
            else:
                return random.choice(dps)
        await ctx.send(f"----------------------------------------------------------------------------------------")
        while pipo1["hp"] > 0 or pipo2["hp"] > 0 or pipo3["hp"] > 0 and mega_pipo["hp"] > 0:
            mega_check = False
            await ctx.send(f".")
            turn1 += pipo1["speed"]
            turn2 += pipo2["speed"]
            turn3 += pipo3["speed"]
            turn_mega += mega_pipo["speed"]
            
            #fight
            if turn1 >= 12 or turn2 >= 12 or turn3 >= 12 or turn_mega >= 12:
                round +=1
                await ctx.send(f"ROUND {round}")
                dmg_pipo1 = await damage(pipo1, mega_pipo)
                dmg_pipo2 = await damage(pipo2, mega_pipo)
                dmg_pipo3 = await damage(pipo3, mega_pipo)
                ff_dmg1 = cl(pipo1["attack"]/3)
                ff_dmg2 = cl(pipo2["attack"]/3)
                ff_dmg3 = cl(pipo3["attack"]/3)
                ff_mega = cl(mega_pipo["attack"]/3)
                #pipo1 attacks
                if turn1 >= 12 and  turn_mega < 12:
                    turn1 = 0
                    mega_pipo["hp"] -= dmg_pipo1
                    await ctx.send(f"   {pipo1['name']} attacks! ")
                    await ctx.send(f"   Dealing {dmg_pipo1} damage!")
                    
                #pipo2 attacks
                if turn2 >= 12 and turn_mega < 12:
                    turn2 = 0
                    mega_pipo["hp"] -= dmg_pipo2
                    await ctx.send(f"   {pipo2['name']} attacks!")
                    await ctx.send(f"   Dealing {dmg_pipo2} damage!")
                    
                #pipo3 attacks
                if turn3 >= 12 and turn_mega < 12:
                    turn3 = 0
                    mega_pipo["hp"] -= dmg_pipo3
                    await ctx.send(f"   {pipo3['name']} attacks!")
                    await ctx.send(f"   Dealing {dmg_pipo3} damage!")
                #mega pipo attacks
                if turn_mega >= 12 and turn1 < 12 and turn2 < 12 and turn3 < 12:
                    turn_mega = 0
                    
                    defender_pipo = defender()
                    dmg = await damage(defender_pipo, mega_pipo)
                    defender_pipo["hp"] -= dmg
                    await ctx.send(f"   {mega_pipo['name']} attacks!")
                    await ctx.send(f"   Dealing {dmg} damage!")
                
                #FF
                #both attack
                speed_tie = []
                if turn1 >= 12 and turn_mega >= 12:
                    speed_tie.append(pipo1)
                if turn2 >= 12 and turn_mega >= 12:
                    speed_tie.append(pipo2)
                if turn3 >= 12 and turn_mega >= 12:
                    speed_tie.append(pipo3)
                for pipo in speed_tie:
                    if pipo["passive"] == "Fight First":
                        if pipo == pipo1:
                            dmg_pipo1 += ff_dmg1
                        if pipo == pipo2:
                            dmg_pipo2 += ff_dmg2
                        if pipo == pipo3:
                            dmg_pipo3 += ff_dmg3
                        pipo["speed"] += 200
                    if mega_pipo["passive"] == "Fight First":
                        mega_pipo["speed"] += 200
                        
                        
                    pipo_faster = await velocity(pipo, mega_pipo)
                    
                    
                    if pipo_faster["name"] == pipo1["name"]:
                        
                        turn1 = 0
                        mega_pipo["hp"] -= dmg_pipo1
                        
                        if mega_pipo["hp"] > 0 and mega_check == False:
                            turn_mega = 0
                            
                            if mega_pipo["passive"] == "Fight First":
                                dmg += ff_mega
                            
                            defender_pipo = defender()
                            dmg = await damage(defender_pipo, mega_pipo)
                            defender_pipo["hp"] -= dmg
                            mega_check = True
                            
                        await ctx.send(f"   {pipo_faster['name']} it's faster!")
                        await ctx.send(f"   {pipo_faster['name']} deals {dmg_pipo1} damage!")
                        if not mega_check:
                            await ctx.send(f"   {mega_pipo['name']} deals {ff_mega} damage!")
                    
                    
                    elif pipo_faster["name"] == pipo2["name"]:
                        
                        turn2 = 0
                        mega_pipo["hp"] -= dmg_pipo2
                        
                        if mega_pipo["hp"] > 0 and mega_check == False:
                            turn_mega = 0
                            
                            if mega_pipo["passive"] == "Fight First":
                                dmg += ff_mega
                            
                            defender_pipo = defender()
                            dmg = await damage(defender_pipo, mega_pipo)
                            defender_pipo["hp"] -= dmg
                            mega_check = True
                            
                        await ctx.send(f"   {pipo_faster['name']} it's faster!")
                        await ctx.send(f"   {pipo_faster['name']} deals {dmg_pipo2} damage!")
                        if not mega_check:
                            await ctx.send(f"   {mega_pipo['name']} deals {ff_mega} damage!")
                    
                    
                    elif pipo_faster["name"] == pipo3["name"]:
                        
                        turn3 = 0
                        mega_pipo["hp"] -= dmg_pipo3
                        
                        if mega_pipo["hp"] > 0 and mega_check == False:
                            turn_mega = 0
                            
                            if mega_pipo["passive"] == "Fight First":
                                dmg += ff_mega
                            
                            defender_pipo = defender()
                            dmg = await damage(defender_pipo, mega_pipo)
                            defender_pipo["hp"] -= dmg
                            mega_check = True
                            
                            
                        await ctx.send(f"   {pipo_faster['name']} it's faster!")
                        await ctx.send(f"   {pipo_faster['name']} deals {dmg_pipo3} damage!")
                        if not mega_check:
                            await ctx.send(f"   {mega_pipo['name']} deals {ff_mega} damage!")
                            
                if pipo1["passive"] == "Fight First":
                    dmg_pipo1 -= ff_dmg1
                    pipo
                if pipo2["passive"] == "Fight First":
                    dmg_pipo2 -= ff_dmg2
                if pipo3["passive"] == "Fight First":
                    dmg_pipo3 -= ff_dmg3
                if mega_pipo["passive"] == "Fight First":
                    ff_mega -= ff_mega
                    
                if pipo1["hp"]<= 0:
                    pipo1["hp"] = 0
                    await ctx.send(f"   {pipo1['name']} fainted!")
                if pipo2["hp"]<= 0:
                    pipo2["hp"] = 0
                    await ctx.send(f"   {pipo2['name']} fainted!")
                if pipo3["hp"]<= 0:
                    pipo3["hp"] = 0
                    await ctx.send(f"   {pipo3['name']} fainted!")
                if mega_pipo["hp"]<= 0:
                    mega_pipo["hp"] = 0
                    
                await ctx.send(f"   {pipo1['name']} HP: {pipo1['hp']} \n{pipo2['name']} HP: {pipo2['hp']} \n{pipo3['name']} HP: {pipo3['hp']} \n{mega_pipo['name']} HP: {mega_pipo['hp']}")
                await ctx.send(f"----------------------------------------------------------------------------------------")
        await ctx.send(f"----------------------------------------------------------------------------------------")
        await ctx.send("COMBAT ENDED!")
        if pipo1["hp"] <= 0 and pipo2["hp"] <= 0 and pipo3["hp"] <= 0:
            await ctx.send(f"   The team fainted!")
            await ctx.send(f"   {mega_pipo['name']} wins!")
            return False, pipo1["hp"], pipo2["hp"], pipo3["hp"]
        else:
            await ctx.send(f"   {mega_pipo['name']} fainted!")
            await ctx.send(f"   The team wins!")
            pipo1["hp"] = pipo1["max_hp"]
            pipo2["hp"] = pipo2["max_hp"]
            pipo3["hp"] = pipo3["max_hp"]
            return True, pipo1["hp"], pipo2["hp"], pipo3["hp"]
    
    #combat pipo vs pipo
    async def fight(self, ctx, pipo1, pipo2):
        turn1 = 0
        turn2 = 0
        round = 0
        await ctx.send(f"----------------------------------------------------------------------------------------")
        while pipo1["hp"] > 0 and pipo2["hp"] > 0:
            turn1 += pipo1["speed"]
            turn2 += pipo2["speed"]
            
            #fight
            if turn1 >= 12 or turn2 >= 12:
                round +=1
                await ctx.send(f"ROUND {round}")
                dmg_pipo1 = await damage(pipo1, pipo2)
                dmg_pipo2 = await damage(pipo2, pipo1)
                ff_dmg1 = cl(pipo1["attack"]/3)
                ff_dmg2 = cl(pipo2["attack"]/3)
                #pipo1 attacks
                if turn1 >= 12 and turn2 < 12:
                    turn1 = 0
                    pipo2["hp"] -= dmg_pipo1
                    await ctx.send(f"   {pipo1['name']} attacks! ")
                    await ctx.send(f"   Dealing {dmg_pipo1} damage!")
                    
                #pipo2 attacks
                if turn2 >= 12 and turn1 < 12:
                    turn2 = 0
                    pipo1["hp"] -= dmg_pipo2
                    await ctx.send(f"   {pipo2['name']} attacks!")
                    await ctx.send(f"   Dealing {dmg_pipo2} damage!")
                    
                #FF
                #both attack
                if turn1 >= 12 and turn2 >= 12:
                    if pipo1["passive"] == 'Fight First':
                        dmg_pipo1 += ff_dmg1
                        pipo1["speed"] += 200
                    if pipo2["passive"] == 'Fight First':
                        dmg_pipo2 += ff_dmg2
                        pipo2["speed"] += 200
                    
                    pipo_faster = await velocity(pipo1, pipo2)
                    
                    if pipo_faster["name"] == pipo1["name"]:
                        pipo2["hp"] -= dmg_pipo1
                        if pipo2["hp"] > 0:
                            pipo1["hp"] -= dmg_pipo2
                        await ctx.send(f"   {pipo1['name']} it's faster!")
                        await ctx.send(f"   {pipo1['name']} deals {dmg_pipo1} damage!")
                        await ctx.send(f"   {pipo2['name']} deals {dmg_pipo2} damage!")
                    else:
                        pipo1["hp"] -= dmg_pipo2
                        if pipo1["hp"] > 0:
                            pipo2["hp"] -= dmg_pipo1
                        await ctx.send(f"   {pipo2['name']} it's faster!")
                        await ctx.send(f"   {pipo2['name']} deals {dmg_pipo2} damage!")
                        await ctx.send(f"   {pipo1['name']} deals {dmg_pipo1} damage!")
                        
                if pipo1["passive"] == "Fight First":
                    dmg_pipo1 -= ff_dmg1
                    pipo1["speed"] -= 200
                if pipo2["passive"] == "Fight First":
                    dmg_pipo2 -= ff_dmg2
                    pipo2["speed"] -= 200
                if pipo1["hp"]<= 0:
                    pipo1["hp"] = 0
                    await ctx.send(f"   {pipo1['name']} fainted!")
                if pipo2["hp"]<= 0:
                    pipo2["hp"] = 0
                    await ctx.send(f"   {pipo2['name']} fainted!")
                
                await ctx.send(f"   {pipo1['name']} HP: {pipo1['hp']} {pipo2['name']} HP: {pipo2['hp']}")
                await ctx.send(f"----------------------------------------------------------------------------------------")
        await ctx.send(f"----------------------------------------------------------------------------------------")
        await ctx.send("COMBAT ENDED!")
        if pipo1["hp"] <= 0:
            await ctx.send(f"   {pipo1['name']} fainted!")
            await ctx.send(f"   {pipo2['name']} wins!")
            return 'pipo2', pipo1["hp"], pipo2["hp"]

        else:
            await ctx.send(f"   {pipo2['name']} fainted!")
            await ctx.send(f"   {pipo1['name']} wins!")
            return 'pipo1', pipo1["hp"], pipo2["hp"]
    
    
    #exp gain and gold after combat and leaderboards
    async def postgame(self, ctx, winner, loser, loser_to = False, bet = 0, user_win = None, user_lose = None, leaderboards = False):
        
        exp_gold = {1:2, 2:5, 3:8, 4:10, 5:15, 6:20, 7:32, 8:50, 9:80, 10:100, 11:150, 12:200, 13:320, 14:500, 15:800, 16:1000, 17:1500, 18:2000, 19:3200, 20:5000}
        exp = exp_gold[loser["lvl"]]
        gold = exp_gold[loser["lvl"]]
        if bet > 0:
            gold = bet
            
        
        #gold
        if not user_win == None:
            self.db["users"].update_one({"id": user_win["id"]}, {"$inc": {"gold": gold}})
            await ctx.send(f"{user_win['name']} gained {gold} gold")
        
        #exp
        if not user_win == None:
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