from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from contextlib import asynccontextmanager
from app.db.database import init_db
from app.db.crud import get_quizzes, get_topics, get_roadmaps, create_quiz, create_topic, create_roadmap

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    await init_db()
    yield
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

class PromptRequest(BaseModel):
    name: str
    user_input: str

class QuizRequest(BaseModel): 
    topic_id: str
    question_data: List[str]

class RoadmapRequest(BaseModel):
    topic_id: str
    user_input: List[str]

@app.post("/topics/")
async def generate_topic(request: PromptRequest):
    return await create_topic(request.name, request.user_input)

@app.get("/topics/")
async def get_generated_topics():
    return await get_topics()

@app.post("/quizzes/")
async def generate_quiz_api(request: QuizRequest):
    return await create_quiz(request.topic_id, request.question_data)

@app.get("/quizzes/{topic_id}")
async def get_generated_quizzes(topic_id: str):
    return await get_quizzes(topic_id)

@app.post("/roadmaps/")
async def generate_roadmap_api(request: RoadmapRequest):
    return await create_roadmap(request.topic_id, request.user_input)

@app.get("/roadmaps/")
async def get_generated_roadmaps():
    return await get_roadmaps()
