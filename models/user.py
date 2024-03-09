from pydantic import BaseModel
from models.pipo import Pipo

class User(BaseModel):
    id: int
    name: str
    gold: int = 40
    defender: Pipo = None
    tank: bool = False
    pipos: list = []