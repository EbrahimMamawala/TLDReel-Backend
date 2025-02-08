import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Clerk Authentication Keys
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")  # Your Clerk API secret key
MONGO_URI = os.getenv("MONGO_URI")  # Your MongoDB URI
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")  # Your ElevenLabs API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Your OpenAI API key

# Database Configuration (PostgreSQL/MySQL)
DATABASE_URL = os.getenv("DATABASE_URL")  # Example: "postgresql://user:password@localhost/dbname"

# App Settings
APP_NAME = "TLDReel Backend"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# CORS Settings (Allow frontend requests)
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# Video Storage (AWS/GCP/Local)
STORAGE_PROVIDER = os.getenv("STORAGE_PROVIDER", "local")  # Options: "aws", "gcp", "local"
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
GCP_STORAGE_BUCKET = os.getenv("GCP_STORAGE_BUCKET")
LOCAL_STORAGE_PATH = os.getenv("LOCAL_STORAGE_PATH", "uploads")

