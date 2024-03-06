from pydantic import BaseModel

class User(BaseModel):
    id: int
    cash: int = 100000000000000000
    pipos: list = []