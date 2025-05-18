import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis",)
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 5432))
    DB_NAME: str = os.getenv("DB_NAME")
    KAFKA_BOOTSTRAP: str = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")

settings = Settings
