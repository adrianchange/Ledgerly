from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    secret_key: str = "dev-secret-change-me"
    database_url: str = "sqlite:///./ledgerly.db"
    access_token_expire_minutes: int = 60 * 24 * 7
    bot_api_token: str = "dev-bot-token-change-me"
    cors_origins: str = "http://localhost:4200,http://127.0.0.1:4200"
    algorithm: str = "HS256"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
