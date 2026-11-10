# import time
# import psycopg2
# from psycopg2.extras import RealDictCursor

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import engine
from .routers import posts, users, auth, votes


# Creating the database tables based on the defined models.
# Tables will now be created by Alembic Migration using the commands:
# a. 'alembic revision --autogenerate -m "Initial migration"' [Generates table structure defined in models.py file]
# b. 'alembic upgrade head'
# models.Base.metadata.create_all(bind = engine)

# # Setting up a connection to the database.
# while True:
#     try:
#         conn = psycopg2.connect(host = 'localhost', database = 'fastAPI', 
#                                 user = 'postgres', password = 'easyPassWord4U', cursor_factory = RealDictCursor)
#         cursor = conn.cursor()
#         print("\nDatabase connection was successful.\n")
#         break
#     except Exception as error:
#         print (f"\nConnecting to database failed with Error:\n{error}")
#         time.sleep(3)


# Creating an instance of the FastAPI class.
app = FastAPI(title = "FastAPI Backend Project",
              description = "This is a Social Media Backend Project built using FastAPI, SQLAlchemy, and PostgreSQL.",
              version = "1.0.0")

# CORS (Cross-Origin Resource Sharing) is a security feature implemented by 'WEB BROWSERS' to restrict 'WEB PAGES'
#       from making requests to a 'Different Domain' than the one that 'served' the web page.
# => A 'google.com' webpage cannot make a request to 'facebook.com' domain due to CORS policy.
#    It can only make requests to 'google.com' domain and its subdomains.

# Allow all webpages too make requests to this FastAPI backend application.
# --< Change to 'origins = ["https://www.google.com"]' to allow only 'google.com' webpages to make requests to this API.
origins = ["*"]

# Adding CORS Middleware to the FastAPI instance to allow sharing of resources between different origins (domains).
app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,    # Allow all origins (webpages from any domain) to access the resources of this FastAPI application.
    allow_credentials = True,   # Allow all credentials (cookies, authorization headers, etc.) to be included in the cross-origin requests.
    allow_methods = ["*"],      # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.) to be used in the cross-origin requests.
    allow_headers = ["*"],      # Allow all headers to be included in the cross-origin requests.
)

# Include application routers for all 'posts', 'users', 'auth' and 'votes' endpoints
app.include_router(posts.router)
app.include_router(votes.router)
app.include_router(users.router)
app.include_router(auth.router)

# Defining the root endpoint that returns a simple greeting message.
@app.get("/")
def root():
    return {"message": "Hello World Harsh!"}
