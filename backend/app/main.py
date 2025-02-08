from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    init_db()  # Initialize the database
    yield
    print("Shutting down...")  # Cleanup tasks if needed

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "FastAPI is running"}
