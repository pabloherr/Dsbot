from pydantic import BaseModel
from models.pipo import Pipo

class User(BaseModel):
    id: int
    name: str
    gold: int = 10000
    defender: Pipo = None
    pipos: list = []