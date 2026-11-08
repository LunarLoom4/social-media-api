from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional, Literal


# Defining a Request-type Pydantic model schema when creating 'users'
class Req_UserCreate(BaseModel):
    email: EmailStr
    password: str
    model_config = ConfigDict(extra = 'forbid')

# Defining a Request-type Pydantic model schema when 'logging in'
class Req_UserLogin(BaseModel):
    email: EmailStr
    password: str

# Defining a Response-type Pydantic model schema when handling 'users'
class Resp_UserBase(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    # Allows Pydantic to read attributes directly from SQLAlchemy model objects
    model_config = ConfigDict(from_attributes = True)


# Defining a Request-type Pydantic model schema when handling 'posts'
class Req_PostBase(BaseModel):
    title: str
    content: str
    published: bool = True
    model_config = ConfigDict(extra = 'forbid')

# Defining a Request-type Pydantic model schema when creating 'posts' (inherited from Req_PostBase)
class Req_PostCreate(Req_PostBase):
    pass

# Defining a Response-type Pydantic model schema when handling 'posts'
class Resp_PostBase(BaseModel):
    id: int
    title: str
    content: str
    published: bool
    created_at: datetime
    owner_id: int
    owner_info: Resp_UserBase

    # Allows Pydantic to read attributes directly from SQLAlchemy model objects
    model_config = ConfigDict(from_attributes = True)

# Defining a wrapper Response-type Pydantic schema over Resp_PostBase to include 'vote' information
class Resp_PostWithVotes(BaseModel):
    Post: Resp_PostBase
    total_votes: int


# Defining a Response-type Pydantic model schema from the 'login' endpoint
class Token(BaseModel):
    access_token: str
    token_type: str

# Defining a Pydantic model schema for the 'data' dictionary passed to the 'create_access_token' function
class TokenData(BaseModel):
    id: Optional[int] = None


# Defining a Request-type Pydantic model schema when creating 'votes'
class Req_VoteCreate(BaseModel):
    post_id: int
    direction: Literal[0, 1]
