from pydantic import BaseModel

class Pipo(BaseModel):
    wild: bool = False
    tank: bool = False
    
    rarity: str
    price : int
    
    name: str
    
    max_hp: int
    hp: int
    attack: int
    defense: int
    speed: int
    
    lvl: int = 1
    exp: int = 0
    
    passive: str
    item: str = None
    
    in_fight: bool = False
    poisoned: bool = False
