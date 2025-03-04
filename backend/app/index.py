from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import List
from contextlib import asynccontextmanager
from db.database import init_db
from db.crud import get_generatedTopics, get_quizzes, get_topics, get_roadmaps, create_quiz, create_topic, create_roadmap, store_points, get_points
from crud.functions import generate_quiz, generate_roadmap, generate_topics
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ml.generate_video import create_final_reel

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    await init_db()
    print("Database initialized")
    yield
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

class PromptRequest(BaseModel):
    user_input: str
    userId: str

class QuizRequest(BaseModel): 
    topic_id: str
    question_data: List[str]

class RoadmapRequest(BaseModel):
    topic_id: str
    user_input: List[str]

class GeneratedTopicRequest(BaseModel):
    topic_id: str

class VideoRequest(BaseModel):
    topic_prompt: str

class QuizSubmitRequest(BaseModel):
    userId: str
    points: int

@app.post("/generate") #Generates list of topics based on user input
async def generate_topic(request: PromptRequest):
    return await generate_topics(request.user_input, request.userId)

@app.get("/generate") #Gets all topic names from the database
async def get_generated_topics(user_id: str = Header(...)):
    if not user_id:
        raise HTTPException(status_code=400, detail="User-ID header missing")
    return await get_topics(user_id)

@app.get("/generated_topics/{topic_id}") #Gets all generated topics list from the database for a given topic
async def get_generated_topics(topic_id: str):
    return await get_generatedTopics(topic_id)

@app.post("/quizzes")
async def generate_quiz_api(request: QuizRequest):
    return await generate_quiz(request.topic_id, request.question_data)

@app.get("/quizzes/{topic_id}")
async def get_generated_quizzes(topic_id: str):
    return await get_quizzes(topic_id)

@app.post("/submit-score")
async def store_score(request: QuizSubmitRequest):
    return await store_points(request.userId, request.points)

@app.get("/get-score")
async def get_score(user_id: str = Header(...)):
    if not user_id:
        raise HTTPException(status_code=400, detail="User-ID header missing")
    return await get_points(user_id)

@app.post("/roadmaps")
async def generate_roadmap_api(request: RoadmapRequest):
    return await generate_roadmap(request.topic_id, request.user_input)

@app.get("/roadmaps")
async def get_generated_roadmaps():
    return await get_roadmaps()

@app.post("/videos")
async def get_generated_videos(request: VideoRequest):
    try:
        final_reel_path = create_final_reel(request.topic_prompt)
        return {"status": "success", "video_path": final_reel_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}   
    
