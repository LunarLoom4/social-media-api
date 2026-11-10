from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time

# Creating an instance of the FastAPI class.
app = FastAPI()

# Defining a Pydantic model for the Post data structure.
class Post(BaseModel):
    title: str
    content: str
    published: bool = True

# Setting up a connection to the database.
while True:
    try:
        conn = psycopg2.connect(host = 'localhost', database = 'fastAPI', 
                                user = 'postgres', password = 'easyPassWord4U', cursor_factory = RealDictCursor)
        cursor = conn.cursor()
        print("\nDatabase connection was successful.\n")
        break
    except Exception as error:
        print (f"\nConnecting to database failed with Error:\n{error}")
        time.sleep(3)


# In-memory list of posts.
my_posts = [{"title": "Title of Post 1.", "content": "Content of Post 1.", "id": 1},
            {"title": "Favorite Foods.", "content": "I like Pizza.", "id": 2}]

# Helper function to find a post by its ID
def find_post(id):
    for post in my_posts:
        if post["id"] == id:
            return post

# Helper function to find the index of a post by its ID
def find_index_of_a_post(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i


# Defining the root endpoint that returns a simple greeting message.
@app.get("/")
def root():
    return {"message": "Hello World Harsh!"}

# Defining an endpoint to retrieve all posts.
@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return {"data": posts}

# Defining an endpoint to retrieve a specific post by its ID.
@app.get("/posts/{id}")     # 'id' is a path parameter -- -- Path Parameters are always of string type.
def get_post(id: int):      # Proper Typecasting is required.
    cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f"Post with id {id} was not found.")
    return {"post_detail": post}


# Defining an endpoint to create a new post.
@app.post("/posts", status_code = status.HTTP_201_CREATED)
def create_post(post: Post):
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""", 
                   (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}


# Defining an endpoint to update an existing post by its ID.
@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", 
                   (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f"Post with id {id} does not exist.")
    return {"data": updated_post}


# Defining an endpoint to delete a post by its ID.
@app.delete("/posts/{id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f"Post with id {id} does not exist.")
    return Response(status_code = status.HTTP_204_NO_CONTENT)   # Don't want to send any data back for a 'delete' operation.

