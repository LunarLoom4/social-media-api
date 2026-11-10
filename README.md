
# Social Media API

A backend REST API built with FastAPI and PostgreSQL. It provides user authentication using JWT and supports CRUD operations for managing posts.

## Features

- User registration and login
- JWT-based authentication
- Create, retrieve, update, and delete posts
- PostgreSQL database integration
- Database migrations using Alembic
- Interactive API documentation with Swagger UI
- Two local development options: Uvicorn directly, or Uvicorn behind NGINX

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
| NGINX | Optional local reverse proxy for HTTPS development |

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

There are two ways to run the API locally. Use Uvicorn directly for a simple setup, or put NGINX in front of Uvicorn for local HTTPS development.

#### Option A: Run Uvicorn directly

This starts Uvicorn on `127.0.0.1:8000`. Use HTTP:

```bash
python scripts/run_server.py http
```

The API will be available at:

http://127.0.0.1:8000

To use HTTPS directly with Uvicorn, first install [mkcert](https://github.com/FiloSottile/mkcert) and initialize its local certificate authority:

From the project root, create the localhost certificates:

```bash
mkcert -install
mkdir certs
mkcert -key-file certs/localhost-key.pem -cert-file certs/localhost.pem localhost 127.0.0.1 ::1
```

Then start Uvicorn with HTTPS:

```bash
python scripts/run_server.py https
```

The API will be available at:

https://localhost:8000

#### Option B: Run behind NGINX

This option starts Uvicorn on `127.0.0.1:8000` using HTTP, then starts NGINX in front of it. NGINX handles the local HTTP-to-HTTPS redirect, TCP Connection, followed by TLS Handshake (presents its certificates to the Browser), and reverse proxying to Uvicorn. The API is available at `https://localhost`, without a port in the URL.

This setup also needs NGINX installed and the localhost certificates generated with mkcert as described above. Make the NGINX executable available on your `PATH`, or pass its location to the script with `--nginx-executable`. For example:

```bash
python scripts/run_local.py
```

Or, if NGINX isn't on your `PATH`:

```bash
python scripts/run_local.py --nginx-executable "C:\nginx\nginx.exe"
```

The script starts and monitors both servers, and stops them when you press `CTRL+C`. NGINX listens on ports 80 and 443, so make sure those ports are available and that your system allows the script to bind to them.

Open `http://localhost` to be redirected to HTTPS, or go straight to:

- [API](https://localhost)
- [Swagger UI](https://localhost/docs)
- [ReDoc](https://localhost/redoc)

The current NGINX configuration proxies requests to a single Uvicorn instance. It does not currently configure rate limiting or load balancing.

## API Documentation

Once a server is running, the interactive API documentation is available at:

- Direct Uvicorn over HTTP: [Swagger UI](http://127.0.0.1:8000/docs) · [ReDoc](http://127.0.0.1:8000/redoc)
- Direct Uvicorn over HTTPS: [Swagger UI](https://localhost:8000/docs) · [ReDoc](https://localhost:8000/redoc)
- NGINX reverse proxy: [Swagger UI](https://localhost/docs) · [ReDoc](https://localhost/redoc)

The HTTPS links use the local certificates generated with mkcert.

## Deployment

For deploying the application on Railway, refer to [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md).

It covers the Railway setup, PostgreSQL configuration, environment variables, database migrations, and public domain generation.
