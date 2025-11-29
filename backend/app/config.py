from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "local"
    database_url: str

    secret_key: str = "change_me"  # перезапишем из .env
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(
        env_prefix="",
        extra="ignore",
    )


settings = Settings()
