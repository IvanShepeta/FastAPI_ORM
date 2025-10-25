from fastapi import FastAPI, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
import models
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True

@app.get("/")
async def root():
    return {'message': "Hello World"}


@app.get("/posts")
async def get_post(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}

@app.post("/posts")
async def create_posts(post:Post, db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {'data': new_post}

@app.get("/posts/{id}")
async def get_posts(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    return {"data": post}

@app.put("/posts/{id}")
async def update_posts(id: int,updated_post: Post, db: Session = Depends(get_db)):
    post_q = db.query(models.Post).filter(models.Post.id == id)
    if post_q.first() is None:
        raise HTTPException(404, detail=f"post with id: {id} not exist")
    post_q.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    db.refresh(post_q)
    return {"data": post_q.first()}


@app.delete("/posts/{id}")
async def delete_posts(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() is None:
        raise HTTPException(404, detail=f"post with id: {id} not exist")
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=204)
