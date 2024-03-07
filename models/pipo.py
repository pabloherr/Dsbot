from pydantic import BaseModel

class Pipo(BaseModel):
    rarity: str
    price : int
    name: str
    hp: int
    attack: int
    defense: int
    speed: int
    passive: str