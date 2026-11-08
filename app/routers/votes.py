from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

from .. import models, schemas, oauth2
from ..database import get_db


# Initialize the router for posts-related endpoints
router = APIRouter(prefix = "/votes", tags = ["Votes"])

# Defining an endpoint to create a new 'vote'.
@router.post("/", status_code = status.HTTP_201_CREATED)
def create_vote(
    vote: schemas.Req_VoteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # Safeguard against voting for a post that doesn't exist
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"Post with id {vote.post_id} does not exist."
        )

    # Query for the user-post combination in the 'votes' table
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)
    found_vote = vote_query.first()

    if (vote.direction == 1):
        if found_vote:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = f"User with ID {current_user.id} has already voted on post {vote.post_id}."
            )

        new_vote = models.Vote(user_id = current_user.id, post_id = vote.post_id)
        db.add(new_vote)
        db.commit()

        return {"message": f"Successfully added a vote on Post {vote.post_id}."}
    else:
        if not found_vote:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Vote does not exist."
            )

        vote_query.delete(synchronize_session = False)
        db.commit()

        return {"message": f"Successfully deleted the vote."}
