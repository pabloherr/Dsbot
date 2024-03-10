from pydantic import BaseModel
from models.pipo import Pipo

class User(BaseModel):
    id: int
    name: str
    gold: int = 40
    defender: Pipo = None
    pipos: list = []
    items: dict = {"potions": 0, "super_potions": 0, "hyper_potions": 0, "max_potions": 0, "passive_reroll": 0}