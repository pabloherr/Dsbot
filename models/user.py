from pydantic import BaseModel
from models.pipo import Pipo

class User(BaseModel):
    id: int
    cash: int = 100000000000000000
    defender: Pipo = None
    pipos: list = []