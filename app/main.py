from operator import index
from typing import Optional
from fastapi import FastAPI , Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import models
from .database import engine, get_db
from sqlalchemy.orm import Session


models.Base.metadata.create_all(bind = engine)

app = FastAPI()

#https://fastapi.tiangolo.com/tutorial/sql-databases/

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

#code to get all posts through (sqlalchemy)
@app.get("/sqlalchemy")
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data" : posts}

#code to insert one post using sqlalchemy
@app.post("/sqlalchemy", status_code = status.HTTP_201_CREATED)
def create_posts(post : Post, db: Session = Depends(get_db)):
    #new_post = models.Post(title = post.title, content = post.content, published = post.published)
    print(post.dict())
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data" : new_post}

#code to get one post using sqlalchemy
@app.get("/sqlalchemy/{id}")
def get_posts(id : int,  db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    print(post)

    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f"post with id: {id} was not found")
    return {"post_detail" : post}

#code to delete one record using sqlalchemy
@app.delete("/sqlalchemy/{id}", status_code= status.HTTP_204_NO_CONTENT)
def delete_posts(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    
    if post.first() == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail= f"Post with id: {id} does not exist")
    post.delete(synchronize_session = False)
    db.commit()
    return Response(status_code = status.HTTP_204_NO_CONTENT)

# code to update one record using sqlalchemy
@app.put("/sqlalchemy/{id}")
def update_post(id: int, post: Post, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    updated_post = post_query.first()
    
    if updated_post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail= f"Post with id: {id} does not exist")
    
    post_query.update(post.dict(), synchronize_session = False)
    db.commit()
    #return{"data": post_query.first()}
    return{"data":"Successful!"}

#code to insert one post
@app.post("/posts", status_code = status.HTTP_201_CREATED)
def create_posts(post : Post):
    cursor.execute(""" insert into posts (title, content, published) values (%s, %s, %s) returning * """, \
                   (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data" : new_post}

#code for get one post
@app.get("/posts/{id}")
def get_posts(id : int):
    cursor.execute("""select * from posts where id = %s""", (str(id)))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f"post with id: {id} was not found")
    return {"data" : post}

#code to delete one record
@app.delete("/posts/{id}", status_code= status.HTTP_204_NO_CONTENT)
def delete_posts(id: int):
    cursor.execute("""delete from posts where id = %s returning * """, (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail= f"Post with id: {id} does not exist")
    
    return Response(status_code = status.HTTP_204_NO_CONTENT)

# code to update one record
@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    
    cursor.execute("""update posts set title = %s, content = %s, published = %s where id = %s returning *""", \
    (post.title, post.content, post.published, str(id)))

    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail= f"Post with id: {id} does not exist")
    

    return{"data": updated_post}

@app.get("/posts/{id}")
def get_posts(id : int):
    print(type(id))
    post = find_post(id)
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f"post with id: {id} was not found")
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