import os
# Use the new OpenAI library interface (if needed, ensure it's updated)
from openai import OpenAI   # type: ignore
from moviepy import * # type: ignore
from  pydantic import BaseModel # type: ignore
from typing import List, Optional, Dict, Any
# Load environment variables from .env
from dotenv import load_dotenv # type: ignore
load_dotenv('.env')

def generate_quiz(user_input: List[str]) -> Dict[str, Any]:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    question_format = """
    {
        id: 1,
        text: "What is the capital of France?",
        options: [
        { id: "A", text: "London", correct: false },
        { id: "B", text: "Paris", correct: true },
        { id: "C", text: "Berlin", correct: false },
        { id: "D", text: "Madrid", correct: false },
        ],
    }
    """
    prompt = f"Generate a json of 5 quiz questions on the topic: {user_input}. Your response per question should be in the following format: {question_format}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Using gpt-3.5-turbo; update as needed
        messages=[{"role": "user", "content": prompt}]
    )
    quiz = response.choices[0].message.content.strip()
    print("Quiz generated.")
    return quiz
