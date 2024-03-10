from pydantic import BaseModel

class Shop(BaseModel):
    potions: int
    super_potions: int
    hyper_potions: int
    max_potions: int
    
    xp_potion: int
    xp_super_potion: int
    xp_hyper_potion: int
    
    passive_reroll:int
    
    revivify: int