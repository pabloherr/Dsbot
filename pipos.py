from pydantic import BaseModel
#from models.pipo import Pipo
import random

pipos_list= []

class Pipo(BaseModel):
    rarity: str
    name: str
    hp: int
    attack: int
    defense: int
    speed: int

async def get_pipo(pipo_name: str) -> Pipo:
    for pipo in pipos_list:
        if pipo.name == pipo_name:
            return pipo
    return None

async def get_pipos() -> list[Pipo]:
    return pipos_list

def create_random_pipo() -> Pipo:
    rarity = random.choice(["common", "uncommon", "rare"])
    if rarity == "common":
        stats = [1, 1, 2, 3]
    elif rarity == "uncommon":
        stats = [1, 1, 2, 4]
    else:
        stats = [2, 2, 3, 4]
    random.shuffle(stats)
    pipo_name = "Pipo_" + str(random.randint(1, 100))
    
    return Pipo(rarity=rarity, name=pipo_name,
                hp=stats[0], attack=stats[1], 
                defense=stats[2], speed=stats[3])

