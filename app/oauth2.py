from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
from datetime import datetime, timezone, timedelta

from . import models, schemas
from .database import get_db
from .config import settings


# Extracts JWT string from the 'Authorization: Bearer <token>' header of the request
# The 'tokenUrl' points the interactive Swagger docs (/docs) to our 'login' endpoint for authentication.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "/login/")

# Important hard-coded variables for creation of a JWToken
SECRET_KEY = settings.secret_key
ALGORITHM  = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


# Create a JSON Web Token (JWT)
def create_access_token(data: dict) -> str:
    data_to_encode = data.copy()

    # Calculates the future expiration time starting from the instant the code here runs
    expiration_time = datetime.now(timezone.utc) + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)

    # Updates the expiration time inside the payload to be passed in the JWT
    data_to_encode.update({"exp": expiration_time})

    # Encode the payload using the SECRET KEY and the ALGORITHM and create a JWT
    encoded_jwt = jwt.encode(data_to_encode, SECRET_KEY, algorithm = ALGORITHM)

    return encoded_jwt

# Verify that the access token has not been tampered with and has not expired
def verify_access_token(token: str) -> schemas.TokenData:
    # --- ZONE 1: CRYPTOGRAPHIC DECODING (Inside try/except) ---
    try:
        # Decodes payload while automatically validating signature and 'exp' claim
        payload = jwt.decode(token, SECRET_KEY, algorithms = ALGORITHM)

    # Catches valid signatures, whose expiration timestamps have officially elapsed in system time
    except ExpiredSignatureError:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Token has expired. Please log in again.",
            headers = {"WWW-Authenticate": "Bearer"}
        )

    # Broad backup exception, handling broken cryptographic signatures or corrupted payload text configurations
    except JWTError:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Token signature verification failed. Malformed or tampered token.",
            headers = {"WWW-Authenticate": "Bearer"}
        )

    # --- ZONE 2: PAYLOAD DATA VALIDATION (Outside try/except) ---
    # Extracts user ID payload key
    user_id: str = payload.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = f"Token payload validation failed. 'user_id' key is missing.",
            headers = {"WWW-Authenticate": "Bearer"}
        )

    # Packages the validated ID into the Pydantic data schema structure
    return schemas.TokenData(id = user_id)

# 1. 'oauth2_scheme' collects the JWToken from the Request-Header.
# 2. 'verify_access_token()' verifies the token.
def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    token_data = verify_access_token(token)

    # Get the user with the 'id' in the JWToken
    curr_user = db.query(models.User).filter(models.User.id == token_data.id).first()

    # Safety Net: Block requests if the token matches a user that no longer exists
    if not curr_user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "User belonging to this token no longer exists.",
            headers = {"WWW-Authenticate": "Bearer"}
        )

    return curr_user
