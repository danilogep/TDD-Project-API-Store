from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Defaults locais para que um clone novo importe sem .env: a suite roda
    # com MongoDB em memoria e nunca toca nesses valores. Em producao as tres
    # variaveis vem do ambiente.
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "store"
    MONGODB_DB_NAME_TEST: str = "test_store"


settings = Settings()
