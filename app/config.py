from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:55432/module12_db"
    model_config = SettingsConfigDict(env_file=("local.env", ".env"))


settings = Settings()
