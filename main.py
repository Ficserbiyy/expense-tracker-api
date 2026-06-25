from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import create_db_and_tables, engine, redis_client
from typing import Final
from asyncio import sleep
from auth import router as auth_router
from expenses import router as expense_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    for attempt in range(10):
        try:
            print(f"Attempt {attempt + 1}")
            await create_db_and_tables()
            print("Connected!")
            break
        except Exception as e:
            print(type(e), e)
            await sleep(2)
    else:
        raise RuntimeError("Database never became available.")

    yield
    await engine.dispose()
    await redis_client.aclose()
    

app: Final = FastAPI(title="Expense Tracker", lifespan=lifespan)
app.include_router(auth_router)
app.include_router(expense_router)



@app.get("/")
async def root():
    return {"message": "Welcome"}