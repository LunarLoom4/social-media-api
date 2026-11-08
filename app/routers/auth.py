from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import models, schemas, utils, oauth2
from ..database import get_db


# Initialize the router for authentication-related endpoints
router = APIRouter(tags = ["Authentication"])

# It's a post request cause we want to send data from the user to the backend.
# Dependency class to collect the 'username' and 'password' as form data.
@router.post("/login/", response_model = schemas.Token)
def login(
    user_cred: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == user_cred.username).first()

    # Throw a 404 error if the user's input email does not exist in the database record logs
    if not user:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = f"User with username '{user_cred.username}' does not exist in the database."
        )

    # Compare incoming raw password hash against securely salted database string values
    if not utils.verify_password(user_cred.password, user.password):
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = f"Wrong password entered for user '{user_cred.username}'."
        )

    # Create a JWToken
    access_token = oauth2.create_access_token(data = {"user_id": user.id})

    # Return the JWToken
    return {"access_token": access_token, "token_type": "bearer"}
