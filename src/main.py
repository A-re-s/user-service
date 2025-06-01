from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine

from config import get_settings
from database import Base
from router import main_router


@asynccontextmanager
async def test_db_connection(*args):
    try:
        engine = create_async_engine(get_settings().db.database_url)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield
    except Exception as e:
        print("❌DB connection failed")
        print(e)
    finally:
        await engine.dispose()


app = FastAPI(lifespan=test_db_connection)
app.include_router(main_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
