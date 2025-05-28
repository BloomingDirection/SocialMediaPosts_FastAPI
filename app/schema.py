from pydantic import BaseModel
from datetime import datetime


class PostBase(BaseModel): #for request result structure
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass

class Post(PostBase): #for response result structure
    id: int
    created_at: datetime

    class Config: #pydantic model reads from dictionary typ by default. 
        #Query returns re sults ORM form. 
        #So it tells pydentic to read data from ORM
        orm_mode = True 