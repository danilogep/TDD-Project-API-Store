from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    MONGODB_URL: str
    MONGODB_DB_NAME: str
    MONGODB_DB_NAME_TEST: str = "test_store"


settings = Settings()
