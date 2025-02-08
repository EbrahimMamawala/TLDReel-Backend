from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager
#from app.db import init_db
from models.flowchart import generate_manim_code

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

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Change this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate/")
async def generate_text(request: PromptRequest):
    return generate_manim_code(request.user_input)
