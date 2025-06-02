from enum import auto
from operator import index
from typing import Optional, List
from fastapi import FastAPI , Response, status, HTTPException, Depends
from fastapi.params import Body
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from app import schemas
from . import models, schemas, utils
from .database import engine, get_db
from sqlalchemy.orm import Session
from .routers import post, user, auth


models.Base.metadata.create_all(bind = engine)

app = FastAPI()

#https://fastapi.tiangolo.com/tutorial/sql-databases/


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

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)


@app.get("/")
def root():
    return {"message" : "Welcome to my API."}


#Code to get all posts using SQL:
@app.get("/posts", response_model = List[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    cursor.execute(""" select * from posts""")
    posts = cursor.fetchall()
    
    return posts

#code to insert one post using SQL
@app.post("/posts", status_code = status.HTTP_201_CREATED, response_model = schemas.Post)
def create_posts(post : schemas.PostCreate):
    cursor.execute(""" insert into posts (title, content, published) values (%s, %s, %s) returning * """, \
                   (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return new_post

#code for get one post using SQL
@app.get("/posts/{id}", response_model = schemas.Post)
def get_posts(id : int):
    cursor.execute("""select * from posts where id = %s""", (str(id)))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f"post with id: {id} was not found")
    return post

#code to delete one record using SQL
@app.delete("/posts/{id}", status_code= status.HTTP_204_NO_CONTENT)
def delete_posts(id: int):
    cursor.execute("""delete from posts where id = %s returning * """, (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail= f"Post with id: {id} does not exist")
    
    return Response(status_code = status.HTTP_204_NO_CONTENT)

# code to update one record using SQL
@app.put("/posts/{id}")
def update_post(id: int, post: schemas.PostCreate, response_model = schemas.Post):
    
    cursor.execute("""update posts set title = %s, content = %s, published = %s where id = %s returning *""", \
    (post.title, post.content, post.published, str(id)))

    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail= f"Post with id: {id} does not exist")
    

    return updated_post  

