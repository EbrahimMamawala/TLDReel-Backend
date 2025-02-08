from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "your_database_name")

client = None  # Global variable for MongoDB client
db = None  # Global variable for database instance

async def init_db():
    global client, db
    if not MONGO_URI:
        raise ValueError("MONGO_URI is not set in the .env file")
    
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    print(f"Connected to MongoDB: {DB_NAME}")
