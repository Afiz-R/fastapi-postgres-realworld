"""
This module contains the settings for the application. Env vars are defined here or in a .env file.
"""

from odmantic.fastapi import AIOEngineDependency
from pydantic import BaseSettings
from pydantic.types import SecretStr
from sqlalchemy import URL, create_engine


class _Settings(BaseSettings):
    SECRET_KEY: SecretStr = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
    ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    MONGO_URI: str | None = None
    POSTGRES_URI: URL = URL.create(
        drivername='postgresql+psycopg', username='versus', password='versus', host='postgres-db', port=5432, database='versus'
    )


# Make this a singleton to avoid reloading it from the env everytime
SETTINGS = _Settings()

EngineD = AIOEngineDependency(mongo_uri=SETTINGS.MONGO_URI)
SQLEngine = create_engine(url=SETTINGS.POSTGRES_URI)
