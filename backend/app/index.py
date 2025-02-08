from fastapi import FastAPI # type: ignore
from pydantic import BaseModel # type: ignore
from contextlib import asynccontextmanager
import json
from pathlib import Path
#from app.db import init_db
from routes.topic import generate_topics

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    #init_db()  # Initialize the database
    yield
    print("Shutting down...")  # Cleanup tasks if needed

app = FastAPI(lifespan=lifespan)

# Request model
class PromptRequest(BaseModel):
    user_input: str  # The variable coming from the frontend

from fastapi.middleware.cors import CORSMiddleware # type: ignore

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Change this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate/")
async def generate_text(request: PromptRequest):
    topics = generate_topics(request.user_input)

    # Save to file
    with open(DATA_FILE, "w") as f:
        json.dump({"topics": topics}, f)

    return {"message": "Data saved successfully", "topics": topics}

@app.get("/generate/")
async def get_generated_text():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        return data
    return {"message": "No data found"}