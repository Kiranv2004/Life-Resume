from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017/liferesume"
    jwt_secret: str = "change_me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24
    github_client_id: str = ""
    github_client_secret: str = ""
    github_redirect_uri: str = "http://localhost:5173/connect"
    cors_origins: str = "http://localhost:5173"
    celery_task_always_eager: bool = True

    class Config:
        env_file = str(Path(__file__).resolve().parents[3] / ".env")
        extra = "ignore"


settings = Settings()
