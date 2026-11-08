from pydantic_settings import BaseSettings, SettingsConfigDict

# Defines configuration schema, automatically overridden by environment variables and .env file.
class Settings(BaseSettings):
    database_url: str | None = None
    database_username: str | None = None
    database_password: str | None = None
    database_host: str | None = None
    database_port: int | None = None
    database_name: str | None = None

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
    )

# Automatically 'scans' the OS and the .env file, then injects actual environment values.
settings = Settings()
