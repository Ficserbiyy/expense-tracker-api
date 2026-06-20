from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from pydantic_settings import BaseSettings, SettingsConfigDict


class UserBase(SQLModel):
    ''' For User creation '''
    email: str = Field(unique=True, index=True)

class User(UserBase, table=True):
    ''' User model '''
    id: int | None = Field(primary_key=True, default=None)
    is_active: bool = True
    hashed_password: str
    description: str | None = None


class Settings(BaseSettings):
    ''' Enviroment Settings '''
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"
    DB_HOST: str = "db" 
    DB_NAME: str = "finance"
    REDIS_URL: str = "redis://redis:6379"
    SECRET_KEY: str = ''
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE: int = 30
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra='ignore',
        case_sensitive=False
    )
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}/{self.DB_NAME}"
    

settings = Settings()
