from operator import index
from typing import Optional
from fastapi import FastAPI , Response, status, HTTPException      
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()

class Post(BaseModel):
    title : str
    content : str
    published : bool = True
    #rating : Optional[int] = None

while True:
        try:
            conn = psycopg2.connect(host = 'localhost', database = 'fastapi_database', user = 'postgres', \
                                    password = 'disha', cursor_factory = RealDictCursor, port = 5433)
            cursor = conn.cursor()
            print("DAtabase connection was successful!")
            break

        except Exception as error:
            print("Connecting to database failed")
            print("Error: ", error)
            time.sleep(2)

            
my_posts = [{"title" : "title of post1" , "content" : "content of post1" , "id" : 1} , {"title" : "favorite foods" \
    , "content" :"I like Pizza" , "id" : 2}]

def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p
        
def find_index_post(id):
    for i,p in enumerate(my_posts):
        if p["id"] == id:
            return i


@app.get("/")
def root():
    return {"message" : "Welcome to my API."}

@app.get("/posts")
def get_posts():
    cursor.execute(""" select * from posts""")
    posts = cursor.fetchall()
    
    return {"data" : posts}

@app.post("/posts", status_code = status.HTTP_201_CREATED)
def create_posts(post : Post):
    cursor.execute(""" insert into posts (title, content, published) values (%s, %s, %s) returning * """, \
                   (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data" : new_post}

@app.get("/posts/{id}")
def get_posts(id : int):
    print(type(id))
    post = find_post(id)
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = "post with id: {id} was not found")
        return{"post_detail" : post}

@app.delete("/posts/{id}", status_code= status.HTTP_204_NO_CONTENT)
def delete_posts(id: int):
    index = find_index_post(id)

    if index == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail= f"Post with id: {id} does not exist")
    my_posts.pop(index)
    return Response(status_code = status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    print(post)
    index = find_index_post(id)

    if index == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail= f"Post with id: {id} does not exist")
    
    post_dict = post.dict()
    post_dict['id'] = id
    my_posts[index] = post_dict
    return{"data": post_dict}