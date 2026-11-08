from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# SQLALCHEMY_DATABASE_URL = '<drivername>://<username>:<password>@<ip-address>/hostname>/<database_name>'
SQLALCHEMY_DATABASE_URL = URL.create(
    drivername = "postgresql",
    username = settings.database_username,
    password = settings.database_password,
    host = settings.database_host,
    port = settings.database_port,
    database = settings.database_name
)

# Creating the database engine
# Used to manage connections to the database and execute SQL statements
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Creating a sessionmaker object that will be used to create database sessions
SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)

# Dependency function to get a database session.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Creating the base class for the models
# Used to define the structure of the database tables and map them to Python classes
Base = declarative_base()
