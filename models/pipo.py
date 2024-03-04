from pydantic import BaseModel

class Pipo(BaseModel):
    rarity: str
    name: str
    hp: int
    attack: int
    defense: int
    speed: int