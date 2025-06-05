from unittest import skip
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy import func
from typing import List, Optional
from fastapi import FastAPI , Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

router = APIRouter(
    prefix = "/sqlalchemy",
    tags = ['Posts']
)

#code to get all posts through (sqlalchemy)
#@router.get("/", response_model = List[schemas.Post])
@router.get("/", response_model = List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db) , \
              current_user :int = Depends(oauth2.get_current_user), limit: int = 10 ,skip :int = 0, search: Optional[str] = ""):
    print(limit)
    #posts = db.query(models.Post).filter(models.Post.content.contains(search)).limit(limit).all()

    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes"))\
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter = True)\
        .group_by(models.Post.id)\
        .filter(models.Post.content.contains(search)).limit(limit).offset(skip).all()
    
    
    #if you want all posts under one owner_id
    #posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all()
    #return results
    return posts

#code to insert one post using sqlalchemy
@router.post("/", status_code = status.HTTP_201_CREATED, response_model = schemas.Post)
def create_posts(post : schemas.PostCreate, db: Session = Depends(get_db),  \
                 current_user :int = Depends(oauth2.get_current_user)):
    #new_post = models.Post(title = post.title, content = post.content, published = post.published)
    #print(current_user.email)
    print(current_user.id)
    #current_user.id
    new_post = models.Post(owner_id = current_user.id,**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

#code to get one post using sqlalchemy
@router.get("/{id}", response_model = schemas.PostOut)
def get_posts(id : int,  db: Session = Depends(get_db), current_user :int = Depends(oauth2.get_current_user)):
    #post = db.query(models.Post).filter(models.Post.id == id).first()
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes"))\
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter = True)\
       .group_by(models.Post.id).filter(models.Post.id == id).first()
    
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f"post with id: {id} was not found")
    
    #if you wish to have one post after login:
    #if post.owner_id != current_user.id:
    #    raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, \
    #                        detail ="Not authorised to perform requested action!")
    
    return post

#code to delete one record using sqlalchemy
@router.delete("/{id}", status_code= status.HTTP_204_NO_CONTENT)
def delete_posts(id: int, db: Session = Depends(get_db), current_user :int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    
    post = post_query.first()

    if post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail= f"Post with id: {id} does not exist")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "Not authorised to perform this action!")
    post_query.delete(synchronize_session = False)
    db.commit()
    return Response(status_code = status.HTTP_204_NO_CONTENT)

# code to update one record using sqlalchemy
@router.put("/{id}", response_model = schemas.Post)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db), current_user :int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    updated_post = post_query.first()
    
    if updated_post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail= f"Post with id: {id} does not exist")
    if updated_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "Not authorised to perform this action!")

    post_query.update(post.dict(), synchronize_session = False)
    db.commit()
    return post_query.first()
