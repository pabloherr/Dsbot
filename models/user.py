from pydantic import BaseModel

class User(BaseModel):
    id: int
    cash: int = 5
    pipos: list = []