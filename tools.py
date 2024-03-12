import random
from math import ceil as cl
from models.pipo import Pipo
from database import db_client

db = db_client["discord"]
channel = 1212525884070699079
# Command to create a random pipo
async def random_pipo( wild = False) -> Pipo:
    
    rarity = random.choices(["common", "uncommon", "rare", "legendary"], weights=[60, 30, 10, 3], k=1)[0]
    passive = random.choice(["None", "Invulnerable","Feel No Pain", "Lethal Hits", "Fight First"])
    if rarity == "common":
        stats = [1, 1, 2, 3]
        price = 10
    elif rarity == "uncommon":
        stats = [1, 2, 3, 3]
        price = 40
    elif rarity == "rare":
        stats = [2, 2, 3, 4]
        price = 80
    else:
        stats = [2, 3, 4, 4]
        price = 160
    random.shuffle(stats)
    pipo_name = "Pipo_" + str(random.randint(1, 100))
    
    pipo = Pipo(wild = wild, rarity=rarity,price=price, name=pipo_name,
                hp=5+stats[0],max_hp=5+stats[0], attack=stats[1], 
                defense=stats[2], speed=stats[3], passive=passive)
    return pipo.dict()

# Command to create a wild pipo
async def wild(zone: str = "forest") -> dict:
    if zone not in ["forest", "desert", "mountain", "megaforest", "megadesert", "megamountain"]:
        return "Invalid zone"
    pipo = await random_pipo(wild=True)
    
    if zone == "forest":
        lvl = random.randint(0, 2)
    if zone == "desert":
        lvl = random.randint(3, 5)
    if zone == "mountain":
        lvl = random.randint(6, 9)
    if zone == "megaforest":
        lvl = 9
    if zone == "megadesert":
        lvl = 19
    if zone == "megamountain":
        lvl = 29
    
    for i in range(lvl):
        stat1 = random.choice(["hp", "attack", "defense", "speed"])
        stat2 = random.choice(["hp", "attack", "defense", "speed"])
        pipo = await lvlup(pipo, stat1, stat2)
    return pipo


# Command to level up the pipos
async def lvlup(pipo: dict, stat1: str, stat2: str) -> dict:
    
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
    return pipo

# Command to calculate the velocity
async def velocity(pipo1: dict, pipo2: dict):
    ff1 = False
    ff2 = False
    if pipo1["passive"] == "Fight First":
        prob = random.randint(1, 4)
        if prob == 1:
            ff1 = True
            pipo1["speed"] += 2
        else:
            pipo1["speed"] -= 2
    if pipo2["passive"] == "Fight First":
        prob = random.randint(1, 4)
        if prob == 1:
            ff2 = True
            pipo2["speed"] += 2
        else:
            pipo2["speed"] -= 2
        
    
    #pipo1 faster
    if pipo1['speed'] > pipo2['speed']:
        if pipo1["passive"] == "Fight First":
            if ff1:
                pipo1["speed"] -= 2
            else:
                pipo1["speed"] += 2
        if pipo2["passive"] == "Fight First":
            if ff2:
                pipo2["speed"] -= 2
            else:
                pipo2["speed"] += 2
        return pipo1
    #pipo2 faster
    elif pipo1['speed'] < pipo2['speed']:
        if pipo1["passive"] == "Fight First":
            if ff1:
                pipo1["speed"] -= 2
            else:
                pipo1["speed"] += 2
        if pipo2["passive"] == "Fight First":
            if ff2:
                pipo2["speed"] -= 2
            else:
                pipo2["speed"] += 2
        return pipo2
    #speed tie
    else:
        if pipo1["passive"] == "Fight First":
            if ff1:
                pipo1["speed"] -= 2
            else:
                pipo1["speed"] += 2
        if pipo2["passive"] == "Fight First":
            if ff2:
                pipo2["speed"] -= 2
            else:
                pipo2["speed"] += 2
        r = random.randint(0, 1)
        if r == 0:
            return pipo1
        else:
            return pipo2

# Command to calculate the damage
async def damage(pipoatk: dict, pipodef: dict) -> int:
    lethal = 0
    feel = False
    if pipodef['passive'] == "Feel No Pain":
        feel = True
        ###############
        if pipoatk['passive'] == "Lethal Hits":
            lethal = cl(pipoatk['attack']/2)
        #########
    if pipodef['passive'] == "Invulnerable":
        inv = random.randint(0, 2)
        if inv == 0:
            return 0
        return pipoatk['attack']
    
    else:
        dmg = pipoatk['attack'] + lethal - pipodef['defense']
        if dmg <= 0:
            dmg = 1 + lethal
        if feel:
            for i in range(dmg):
                r = random.randint(0, 2)
                if r == 0:
                    dmg -= 1
        return dmg