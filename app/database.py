from sqlalchemy.engine import URL, make_url
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# SQLALCHEMY_DATABASE_URL = '<drivername>://<username>:<password>@<ip-address>/hostname>/<database_name>'

# The database connection URL is constructed based on the provided settings.
# a. If a full DATABASE_URL is provided, it is used directly.
# b. Otherwise, individual components (username, password, host, port, database name) are used to construct the URL.
if settings.database_url and settings.database_url.strip():
    SQLALCHEMY_DATABASE_URL = make_url(settings.database_url)
    if not SQLALCHEMY_DATABASE_URL.host:
        raise ValueError("DATABASE_URL must include a database host.")
else:
    database_username = settings.database_username
    database_password = settings.database_password
    database_host = settings.database_host
    database_port = settings.database_port
    database_name = settings.database_name

    # Validation to ensure that all necessary components are provided.
    if (
        database_username is None    or not database_username.strip()
        or database_password is None or not database_password.strip()
        or database_host is None     or not database_host.strip()
        or database_port is None
        or database_name is None     or not database_name.strip()
    ):
        raise ValueError(
            "Set DATABASE_URL or all five database settings: "
            "DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT, and DATABASE_NAME."
        )

    # Port Number is within a valid range.
    if not 1 <= database_port <= 65535:
        raise ValueError("DATABASE_PORT must be between 1 and 65535.")

    SQLALCHEMY_DATABASE_URL = URL.create(
        drivername = "postgresql",
        username = database_username,
        password = database_password,
        host = database_host,
        port = database_port,
        database = database_name
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
