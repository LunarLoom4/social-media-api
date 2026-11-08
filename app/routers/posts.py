from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, oauth2, utils
from ..database import get_db


# Initialize the router for posts-related endpoints
router = APIRouter(prefix = "/posts", tags = ["Posts"])

# Controls the access of posts to all users or only to the post owners
access_all_posts = True

# Defining an endpoint to get all 'posts'
@router.get("/", response_model = List[schemas.Resp_PostWithVotes])
def get_posts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
    searchStr: str | None = None,
    limit: int = 10,
    offset: int = 0
):
    global access_all_posts

    # Utilize a Left Outer Join and Group By for vote counting
    # '''
    # SELECT posts.*, COUNT(votes.post_id) AS total_votes 
    #    FROM posts LEFT OUTER JOIN votes ON posts.id = votes.post_id GROUP BY posts.id;
    # '''
    post_query = db.query(models.Post, func.count(models.Vote.post_id).label("total_votes")) \
                   .outerjoin(models.Vote, models.Post.id == models.Vote.post_id).group_by(models.Post.id)
    utils.print_query(post_query)

    # ONLY retrieve posts created by the currently logged-in user
    if not access_all_posts:
        post_query = post_query.filter(models.Post.owner_id == current_user.id)
    utils.print_query(post_query)

    # Apply search filter
    if searchStr:
        post_query = post_query.filter(models.Post.title.contains(searchStr))
    utils.print_query(post_query)

    # Apply pagination
    # URL = 'http://127.0.0.1:8000/posts/?searchStr=me%20is&limit=5&offset=1'
    post_query = post_query.limit(limit).offset(offset)
    utils.print_query(post_query)

    # Execute the query
    result = post_query.all()

    return result

# Defining an endpoint to get a specific 'post' by its ID
@router.get("/{id}/", response_model = schemas.Resp_PostWithVotes)
def get_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    global access_all_posts
    
    # Utilize a Left Outer Join and Group By for vote counting
    # '''
    # SELECT posts.*, COUNT(votes.post_id) AS total_votes 
    #    FROM posts LEFT JOIN votes ON posts.id = votes.post_id GROUP BY posts.id;
    # '''
    post_query = db.query(models.Post, func.count(models.Vote.post_id).label("total_votes")) \
                    .outerjoin(models.Vote, models.Post.id == models.Vote.post_id).group_by(models.Post.id)
    utils.print_query(post_query)

    # ONLY retrieve posts created by the currently logged-in user
    if not access_all_posts:
        post_query = post_query.filter(models.Post.owner_id == current_user.id)
    utils.print_query(post_query)

    # Apply the filter to get the specific post by ID
    post_query = post_query.filter(models.Post.id == id)
    utils.print_query(post_query)

    # Execute the query
    result = post_query.first()

    # Raise a 404 error if post does not exist
    if not result:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"Post with id {id} was not found."
        )

    return result

# Defining an endpoint to create a new 'post'
@router.post("/", status_code = status.HTTP_201_CREATED, response_model = schemas.Resp_PostBase)
def create_post(
    post: schemas.Req_PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # Extract the incoming request schema down to a simple dict
    post_dict = post.model_dump()

    # Inject the database user ID directly into the owner_id of the 'Post'
    new_post = models.Post(owner_id = current_user.id, **post_dict)

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

# Defining an endpoint to update an existing 'post' by its ID
@router.put("/{id}/", response_model = schemas.Resp_PostBase)
def update_post(
    id: int,
    updated_post: schemas.Req_PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    # 1. Check if the post even exists
    if post is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"Post with id {id} does not exist."
        )

    # 2. ENFORCE ONWERSHIP
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = f"Users cannot update other users' posts."
        )

    post_query.update(updated_post.model_dump(), synchronize_session = False)
    db.commit()

    return post_query.first()

# Defining an endpoint to delete a 'post' by its ID
@router.delete("/{id}/", status_code = status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    # 1. Check if the post even exists
    if post is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"Post with id {id} does not exist."
        )

    # 2. ENFORCE OWNERSHIP
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = f"Users cannot delete other users' posts."
        )

    post_query.delete(synchronize_session = False)
    db.commit()

    return Response(status_code = status.HTTP_204_NO_CONTENT)
