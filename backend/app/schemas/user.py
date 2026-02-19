from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    email:EmailStr


class UserCreate(UserBase):
    password:str


class UserResponse(UserBase):
    id:int
    created_at: datetime

class UserLogin(BaseModel):
    email:str
    password:str

    class Config:
        orm_mode = True