from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models import Topic, Quiz, Roadmap
import os
from dotenv import load_dotenv

load_dotenv("backend/app/.env")
MONGO_URI = os.getenv("MONGO_URI")

client = AsyncIOMotorClient(MONGO_URI)
db = client.get_database("mydatabase")

async def init_db():
    await init_beanie(database=db, document_models=[Topic, Quiz, Roadmap])