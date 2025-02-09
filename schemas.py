from typing import Optional
from pydantic import BaseModel

class ItemId(BaseModel):
    id: int

class NewClothes(BaseModel):
    name: str
    type_id: int
    user_id: int