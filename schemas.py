from typing import Literal, Optional
from pydantic import BaseModel
import uuid

class ItemId(BaseModel):
    id: int

class BaseUser(BaseModel):
    username: str
    password: str

class CreateUser(BaseUser):
    firstname: str
    lastname: str
    password: str
    email: Optional[str]

class Reg(BaseUser):
    pass

class UpdateUser(BaseModel):
    username: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    password: Optional[str] = None

class UserModel(BaseModel):
    id: int
    firstname: str
    lastname: str
    username: str

class ResponseUserData(UserModel):
    firstname: str
    lastname: str

class Login(BaseUser):
    pass


class LoginResponse(BaseModel):
    token: uuid.UUID

class StatusResponse(BaseModel):
    status: Literal['success', 'deleted', 'error']

class NewClothes(BaseModel):
    name: str
    type_id: int
    user_id: int

class ClothesModelAll(BaseModel):
    id: int
    name: str
    type: str
    url: str
    category: str
    user_id: int

class UpdateClothes(BaseModel):
    name: Optional[str] = None
    type_id: Optional[int] = None


class ClothesTypeModel(BaseModel):
    id: int
    name: str
    category: str

    class Config:
        from_attributes = True

class ClothesModel(BaseModel):
    id: int
    name: str
    type: ClothesTypeModel

    class Config:
        from_attributes = True