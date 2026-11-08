# Deploying to Railway

This repo runs FastAPI with Uvicorn and uses Railway Postgres. The API service is `social-media-api`; the database service is `Postgres`.

## 1. Prepare the repo

Deploy from the repository root, where `requirements.txt`, `app/`, `alembic/`, `alembic.ini`, `railpack.json`, and `.python-version` are located. Commit and push your changes to the GitHub branch Railway deploys.

`railpack.json` starts the app:

```json
{
  "$schema": "https://schema.railpack.com",
  "deploy": {
    "startCommand": "python -m uvicorn app.main_v2:app --host 0.0.0.0 --port $PORT"
  }
}
```

`.python-version` pins the Railway build to Python `3.14.8`. Check the build log to confirm the version.

## 2. Create the services

Create a Railway project, connect this GitHub repo, and add a PostgreSQL service to the same environment. Railway should show a connection from `social-media-api` to `Postgres`.

## 3. Set variables

In **`social-media-api` → Variables**, set:

| Variable | Value |
|---|---|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` |
| `SECRET_KEY` | A strong, private random value |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `7200` (five days; change if desired) |

Use the exact Postgres service name in the reference if it differs. The app uses `DATABASE_URL` when set. The separate `DATABASE_USERNAME`, `DATABASE_PASSWORD`, `DATABASE_HOST`, `DATABASE_PORT`, and `DATABASE_NAME` settings are only needed if you aren't using `DATABASE_URL`.

In **`Postgres` → Variables**, keep Railway's generated variables and references:

| Variable | Value |
|---|---|
| `DATABASE_URL` | `postgresql://${{PGUSER}}:${{POSTGRES_PASSWORD}}@${{RAILWAY_PRIVATE_DOMAIN}}:5432/${{PGDATABASE}}` |
| `PGDATA` | `/var/lib/postgresql/data/pgdata` |
| `PGDATABASE` | `${{POSTGRES_DB}}` |
| `PGHOST` | `${{RAILWAY_PRIVATE_DOMAIN}}` |
| `PGPASSWORD` | `${{POSTGRES_PASSWORD}}` |
| `PGPORT` | `5432` |
| `PGUSER` | `${{POSTGRES_USER}}` |
| `POSTGRES_DB` | `railway` |
| `POSTGRES_PASSWORD` | Railway-managed password; don't replace it by editing this variable |
| `POSTGRES_USER` | `postgres` |
| `RAILWAY_DEPLOYMENT_DRAINING_SECONDS` | `60` |
| `SSL_CERT_DAYS` | `820` |

If Railway shows a different generated value for a managed variable, leave its value as Railway provides it. To change the database password, use **Postgres → Config → Connection → Regenerate**; editing `POSTGRES_PASSWORD` alone can leave it out of sync with the running database. Keep secrets out of Git.

After changing variables, apply Railway's staged changes. The API's database settings must reference the Postgres service, not a local database in `.env`.

## 4. Set up migrations

In **`social-media-api` → Settings → Deploy → Pre-deploy Command**, enter:

```sh
alembic upgrade head
```

This applies committed migrations before the API starts.

When you change models during development, generate a migration locally:

```sh
alembic revision --autogenerate -m "Describe the schema change"
```

Review and commit the generated migration. Do not run this command on Railway for each deploy. `alembic upgrade head` applies migrations; it does not generate them.

The current migrations are intended for a fresh database. In particular, adding a required `owner_id` to a populated `posts` table may need a data migration first.

## 5. Deploy and check

Deploy `social-media-api`. Check that the build uses Python 3.14.8, the pre-deploy migration succeeds, and the API starts. Open `/docs` and try a database-backed flow: create a user, log in, then create or list posts.

## 6. Open the API in a browser

To get a public URL, select **`social-media-api` → Settings → Networking → Public Networking → Generate Domain**. Open the generated HTTPS domain:

- `/` returns the API's greeting.
- `/docs` opens the interactive API documentation.
- `/openapi.json` returns the API schema.

Keep Postgres private; the API connects to it over Railway's private network.

Before using a browser-based frontend, replace the wildcard CORS origin in `app/main_v2.py` with the frontend's actual origin.
