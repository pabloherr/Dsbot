import random
from math import ceil as cl
from math import floor as fl
from models.pipo import Pipo
from database import db_client

db = db_client["discord"]
# Command to create a random pipo
async def random_pipo( wild = False) -> Pipo:
    
    rarity = random.choices(["common", "uncommon", "rare", "legendary"], weights=[60, 30, 10, 3], k=1)[0]
    passive = random.choice(["None", "Invulnerable","Feel No Pain", "Lethal Hits", "Fight First", "Sustained Hits", "Parry", "Rapid Metabolism", "Regeneration", "Void", "Berserker", "Healing Touch", "Poisoneous Skin"])
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
        lvl = 15
    if zone == "megadesert":
        lvl = 25
    if zone == "megamountain":
        lvl = 35
    
    for i in range(lvl):
        stat1 = random.choice(["hp", "attack", "defense", "speed"])
        stat2 = random.choice(["hp", "attack", "defense", "speed"])
        while stat2 == stat1:
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
async def alt_velocity(pipo1: dict, pipo2: dict, pipo3:dict = None, pipo4:dict = None):
    ff1 = random.randint(0, 3)
    ff2 = random.randint(0, 3)
    ff3 = random.randint(0, 3)
    ff4 = random.randint(0, 3)
    if pipo1["passive"] == "Fight First":
        pipo1["speed"] += ff1
    if pipo2["passive"] == "Fight First":
        pipo2["speed"] += ff2
    vel = [pipo1, pipo2]
    if pipo3 is not None:
        if pipo3["passive"] == "Fight First":
            pipo3["speed"] += ff3
        vel.append(pipo3)
        if pipo4["passive"] == "Fight First":
            pipo4["speed"] += ff4
        vel.append(pipo4)
    random.shuffle(vel)
    vel = sorted(vel, key=lambda x: x['speed'], reverse=True)
    if pipo1["passive"] == "Fight First":
        pipo1["speed"] -= ff1
    if pipo2["passive"] == "Fight First":
        pipo2["speed"] -= ff2
    if pipo3 is not None:
        if pipo3["passive"] == "Fight First":
            pipo3["speed"] -= ff3
        if pipo4["passive"] == "Fight First":
            pipo4["speed"] -= ff4
    if pipo3 is None:
        return vel[0], vel[1]
    return vel[0], vel[1], vel[2], vel[3]
    
# Command to calculate the damage
async def damage(pipoatk: dict, pipodef: dict) -> int:
    lethal = 0
    feel = False
    if pipodef['passive'] == "Feel No Pain":
        feel = True
    ###############
    if pipoatk['passive'] == "Lethal Hits":
        r = random.choice([0,1/2,1/4])
        lethal = cl(pipoatk['attack'] * r)
        if r == 0:
            lethal = 0
    #########
        
    if pipodef['passive'] == "Invulnerable":
        inv = random.randint(0, 2)
        if inv == 0:
            return 0
        
    dmg = pipoatk['attack'] + lethal - fl(pipodef['defense']*0.75)
    if dmg <= 0:
        dmg = 1 + lethal
    if feel:
        for i in range(dmg):
            r = random.randint(0, 1)
            if r == 0:
                dmg -= 1
    return dmg