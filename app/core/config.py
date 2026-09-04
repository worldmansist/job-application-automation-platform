from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Job Application Automation Platform"
    environment: str = "development"
    database_url: str = "sqlite:///./app.db"
    telegram_bot_token: str = ""
    api_base_url: str = "http://127.0.0.1:8000"

    class Config:
        env_file = ".env"


settings = Settings()
