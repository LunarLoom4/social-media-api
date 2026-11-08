from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, utils, oauth2
from ..database import get_db


# Initialize the router for users-related endpoints
router = APIRouter(prefix = "/users", tags = ["Users"])

# Defining an endpoint to get a specific 'user' by their ID.
@router.get('/{id}/', response_model = schemas.Resp_UserBase)
def get_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"User with id {id} does not exist."
        )
    return user

# Defining an endpoint to create a new 'user'.
@router.post("/", status_code = status.HTTP_201_CREATED, response_model = schemas.Resp_UserBase)
def create_user(
    user: schemas.Req_UserCreate,
    db: Session = Depends(get_db)
):
    # Hash the password
    hashed_password = utils.hash_password(user.password)
    user.password = hashed_password

    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
