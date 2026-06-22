from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import create_db_and_tables, engine, redis_client
from typing import Final
from auth import router as auth_router
from expenses import router as expense_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield
    await engine.dispose()
    await redis_client.aclose()
    

app: Final = FastAPI(title="Expense Tracker", lifespan=lifespan)
app.include_router(auth_router)
app.include_router(expense_router)



@app.get("/")
async def root():
    return {"message": "Welcome"}