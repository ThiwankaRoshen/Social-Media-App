from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time

while True:
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="fastAPIPractice",
            user="postgres",
            password="Boys2020.",
            cursor_factory=RealDictCursor,
        )
        curser = conn.cursor()
        print("Database connection successfull!")
        break
    except Exception as e:
        print("Connection Error")
        print("error", e)
        time.sleep(2)


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


app = FastAPI()


@app.get("/posts")
def root():
    curser.execute("""SELECT * FROM posts;""")
    posts = curser.fetchall()
    return {"data": posts}


@app.get("/posts/{id}")
def get_post(id: int):
    id_str = str(id)
    curser.execute(
        """SELECT * FROM posts WHERE id=%s;""",
        (id_str),
    )
    post = curser.fetchone()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Index not found."
        )
    return {"data": post}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def send(payload: Post):
    curser.execute(
        """INSERT INTO posts(title, content, published) VALUES (%s, %s, %s) RETURNING *;""",
        (payload.title, payload.content, payload.published),
    )
    post_created = curser.fetchone()
    conn.commit()
    return {"message": post_created}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    curser.execute(
        """DELETE FROM posts WHERE id=%s RETURNING *;""",
        (str(id))
    )
    post = curser.fetchone()
    conn.commit()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No post found in that ID"
        )
    

@app.put("/posts/{id}")
def update_post(id: int, updated_post: Post):
    curser.execute(
        """UPDATE posts SET title=%s, content=%s, published=%s WHERE id=%s RETURNING *;""",
        (updated_post.title, updated_post.content, updated_post.published, str(id))
    )
    post_updated = curser.fetchone()
    conn.commit()
    if not post_updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No post found in that ID"
        )
    return{
        "data":post_updated
    }