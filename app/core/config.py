from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    PROJECT_NAME: str
    VERSION: str
    API_V1_STR: str
    DEBUG: bool = False

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    @property
    def DATABASE_URL(self) -> str:
        return (f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}")

    KAFKA_HOST: str
    KAFKA_PORT: str
    KAFKA_INTERNAL_PORT: str
    ZOOKEEPER_PORT: str
    KAFKA_MESSAGES_TOPIC: str = "messages"
    KAFKA_TOPIC_PARTITIONS: int = 3

    @property
    def KAFKA_BOOTSTRAP_SERVERS(self) -> List[str]:
        return [f"{self.KAFKA_HOST}:{self.KAFKA_INTERNAL_PORT}"]

    # JWT settings
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        case_sensitive = True
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
