from sqlmodel import SQLModel
from config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import Final
from redis.asyncio import from_url

engine: Final = create_async_engine(settings.DATABASE_URL, echo=True)
redis_client: Final = from_url(settings.REDIS_URL, decode_responses=True)


async_session_factory: Final = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_session():
    async with async_session_factory() as session:
        yield session
           
        
async def create_db_and_tables():
    ''' Create database tables based on SQLModel schemas. '''
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)