from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from db.models import Topic, Quiz, Roadmap, GeneratedTopic, Score
import os
from dotenv import load_dotenv

load_dotenv(".env")
MONGO_URI = os.getenv("MONGO_URI")  # Default if None


client = AsyncIOMotorClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
db = client.get_database("yantra-hack")

async def init_db():
    await init_beanie(database=db, document_models=[Topic, Quiz, Roadmap, GeneratedTopic, Score])
    print("hello world")
