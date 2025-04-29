from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv
from os import getenv

load_dotenv()

db_name = getenv("DB_NAME")
db_user = getenv("DB_USER")
db_password = getenv("DB_PASSWORD")
db_host = getenv("DB_HOST", "localhost")
db_port = getenv("DB_PORT", "5432")

engine = create_async_engine(
    f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}",
        )

new_session = async_sessionmaker(engine)

async def get_session():
    async with new_session() as session:
        yield session
