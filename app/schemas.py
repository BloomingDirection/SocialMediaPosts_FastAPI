
from turtle import st
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from pydantic.types import conint


class PostBase(BaseModel): #for request result structure
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass

class UserOut(BaseModel):
    id : int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True

class Post(PostBase): #for response result structure
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

    class Config: #pydantic model reads from dictionary typ by default. 
        #Query returns re sults ORM form. 
        #So it tells pydentic to read data from ORM
        orm_mode = True 

class PostOut(BaseModel) :
    Post: Post
    votes: int
     
    class Config:
        orm_mode = True 

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None

class Vote(BaseModel):
    post_id: int
    dir: conint(ge = 0, le = 1)  # type: ignore
