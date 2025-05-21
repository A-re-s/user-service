from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from config import settings

engine = create_async_engine(settings.db.database_url)

new_session = async_sessionmaker(engine)

class Base(DeclarativeBase):
    pass

async def get_session():
    async with new_session() as session:
        yield session
