
# Social Media API

A backend REST API built with FastAPI and PostgreSQL. It provides user authentication using JWT and supports CRUD operations for managing posts.

## Features

- User registration and login
- JWT-based authentication
- Create, retrieve, update, and delete posts
- PostgreSQL database integration
- Database migrations using Alembic
- Interactive API documentation with Swagger UI

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend development |
| FastAPI | REST API framework |
| PostgreSQL | Database |
| SQLAlchemy | ORM |
| Alembic | Database migrations |
| OAuth2 + JWT | Authentication |
| Uvicorn | ASGI server |

## Local Setup

### Prerequisites

Make sure you have the following installed:

- Python 3.14.8
- PostgreSQL
- Git

### 1. Clone the repository

```bash
git clone https://github.com/LunarLoom4/social-media-api.git
cd social-media-api
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it using the appropriate command for your operating system.

**Windows (PowerShell):**

```powershell
.venv\Scripts\Activate.ps1
```

**Windows (CMD):**

```cmd
.venv\Scripts\activate.bat
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create a PostgreSQL database

Make sure your PostgreSQL server is running before proceeding.

There are two ways to create the database.

**Option A: Using the PostgreSQL command line**

Open a terminal and connect to PostgreSQL:

```bash
psql -U postgres
```

Enter your PostgreSQL password when prompted.

Once connected, execute:

```sql
CREATE DATABASE social_media_api;
```

To verify that the database was created:

```sql
\l
```

Exit the PostgreSQL terminal:

```sql
\q
```

**Option B: Using pgAdmin**

1. Open pgAdmin and connect to your PostgreSQL server.
2. Expand **Servers → PostgreSQL → Databases**.
3. Right-click **Databases** and select **Create → Database**.
4. Enter `social_media_api` as the database name.
5. Select your PostgreSQL user as the owner and click **Save**.

### 5. Configure environment variables

Copy `.env.example` to `.env` in the project root.

**Windows (PowerShell):**

```powershell
Copy-Item .env.example .env
```

**Linux / macOS:**

```bash
cp .env.example .env
```

Open `.env` and update the database credentials according to your local PostgreSQL configuration.

Generate a secret key for JWT authentication:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Replace the `SECRET_KEY` value in `.env` with the generated key.

Do not commit `.env` to the repository. It contains sensitive configuration values.

### 6. Apply database migrations

With PostgreSQL running and `.env` configured, execute:

```bash
alembic upgrade head
```

This applies the existing Alembic migrations and creates the required database tables.

### 7. Start the application

The development server can be started using the included Python script.

**HTTP:**

```bash
python scripts/run_server.py http
```

The API will be available at:

http://127.0.0.1:8000

**HTTPS (optional):**

Local HTTPS can be enabled using [mkcert](https://github.com/FiloSottile/mkcert).

Install mkcert and initialize its local certificate authority:

```bash
mkcert -install
```

From the project root, generate the localhost certificates:

```bash
mkdir certs
mkcert -key-file certs/localhost-key.pem -cert-file certs/localhost.pem localhost 127.0.0.1 ::1
```

Start the server using HTTPS:

```bash
python scripts/run_server.py https
```

The API will now be available at:

https://localhost:8000

## API Documentation

Once the server is running, the interactive API documentation is available at:

- [Swagger UI](http://127.0.0.1:8000/docs) (HTTP)
- [ReDoc](http://127.0.0.1:8000/redoc) (HTTP)

When using HTTPS, replace `http://127.0.0.1:8000` with `https://localhost:8000`.

## Deployment

For deploying the application on Railway, refer to [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md).

It covers the Railway setup, PostgreSQL configuration, environment variables, database migrations, and public domain generation.
