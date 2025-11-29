from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "local"
    database_url: str

    model_config = SettingsConfigDict(
        env_prefix="",
        extra="ignore",
    )


settings = Settings()
