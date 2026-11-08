from pydantic_settings import BaseSettings, SettingsConfigDict

# Defines configuration schema, automatically overridden by environment variables and .env file.
class Settings(BaseSettings):
    database_username: str
    database_password: str
    database_host: str
    database_port: str
    database_name: str

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
    )

# Automatically 'scans' the OS and the .env file, then injects actual environment values.
settings = Settings()
