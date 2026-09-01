from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Job Application Automation Platform"
    environment: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()
