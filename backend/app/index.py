from fastapi import FastAPI # type: ignore
from pydantic import BaseModel # type: ignore
from contextlib import asynccontextmanager
import json
from pathlib import Path
from app.db import init_db
from app.db.database import get_db
from app.db.crud import get_quizzes, get_topics, get_roadmaps, create_topic, create_quiz, create_roadmap
from sqlalchemy.orm import Session # type: ignore
from crud.functions import generate_topics


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    init_db()  # Initialize the database
    yield
    print("Shutting down...")  # Cleanup tasks if needed

app = FastAPI(lifespan=lifespan)

# Request model
class PromptRequest(BaseModel):
    id : str
    user_input: str  # The variable coming from the frontend

class QuizRequest(BaseModel): 
    id : str
    user_input: str

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

@app.get("/quizzes/{topic_id}")
async def get_generated_quizzes(topic_id: str, db: Session = Depends(get_db)):
    return get_quizzes(db, topic_id)