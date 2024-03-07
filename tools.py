import random
from math import ceil as cl
from models.pipo import Pipo

async def random_pipo( wild = False) -> Pipo:
    rarity = random.choices(["common", "uncommon", "rare", "legendary"], weights=[60, 30, 10, 3], k=1)[0]
    passive = random.choice(["None", "Invulnerable","Feel No Pain", "Lethal Hits", "Fight First"])
    if rarity == "common":
        stats = [1, 1, 2, 3]
        price = 2
    elif rarity == "uncommon":
        stats = [1, 1, 2, 4]
        price = 4
    elif rarity == "rare":
        stats = [2, 2, 3, 4]
        price = 8
    else:
        stats = [2, 3, 4, 4]
        price = 16
    random.shuffle(stats)
    pipo_name = "Pipo_" + str(random.randint(1, 100))
    
    pipo = Pipo(wild = wild, rarity=rarity,price=price, name=pipo_name,
                hp=5+stats[0],max_hp=5+stats[0], attack=stats[1], 
                defense=stats[2], speed=stats[3], passive=passive)
    return pipo.dict()


async def fight(pipoatk: dict, pipodef: dict) -> int:
    lethal = 0
    feel = False
    if pipodef['passive'] == "Feel No Pain":
        feel = True
    if pipoatk['passive'] == "Lethal Hits":
        lethal = 2
    
    if pipodef['passive'] == "Invulnerable":
        inv = random.randint(0, 2)
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
                r = random.randint(0,2)
                if r == 0:
                    dmg -= 1
        return dmg
    else:
        dmg =  pipoatk['attack']
        if feel:
            for i in range(dmg):
                r = random.randint(0,2)
                if r == 0:
                    dmg -= 1
        return dmg
    