from pydantic import BaseModel

class Pipo(BaseModel):
    wild: bool = False
    rarity: str
    price : int
    name: str
    max_hp: int
    hp: int
    attack: int
    defense: int
    speed: int
    passive: str
    lvl: int = 1
    exp: int = 0
    