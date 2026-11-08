from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from .database import Base

# Post Model ['posts' Table]
class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, nullable = False, primary_key = True)
    title = Column(String, nullable = False)
    content = Column(String, nullable = False)
    published = Column(Boolean, nullable = False, server_default = 'TRUE')
    created_at = Column(TIMESTAMP(timezone = True), nullable = False, server_default = text('now()'))

    owner_id = Column(Integer, ForeignKey("users.id", ondelete = "CASCADE"), nullable = False)
    owner_info = relationship("User")

# User Model ['users' Table]
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, nullable = False, primary_key = True)
    email = Column(String, nullable = False, unique = True)
    password = Column(String, nullable = False)
    created_at = Column(TIMESTAMP(timezone = True), nullable = False, server_default = text('now()'))

# Vote Model ['votes' Table]
class Vote(Base):
    __tablename__ = "votes"

    user_id = Column(Integer, ForeignKey("users.id", ondelete = "CASCADE"), primary_key = True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete = "CASCADE"), primary_key = True)
