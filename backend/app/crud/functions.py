import os
from openai import OpenAI   # type: ignore
from moviepy import * # type: ignore
from  pydantic import BaseModel # type: ignore
from typing import List # type: ignore

from dotenv import load_dotenv # type: ignore

load_dotenv('backend\\app\\.env')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")



def summarize_text(text: str) -> str:
    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = f"Summarize the following text in brief, keeping only the essential details: {text}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Adjust as needed
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def generate_topics(user_input: str) -> str:
    MAX_LENGTH = 300
    
    if len(user_input) > MAX_LENGTH:
        print("Input is too long, summarizing first...")
        user_input = summarize_text(user_input)
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = f"Generate an array each of 5 difficult, 5 medium, and 5 easy topics nested in a parent JSON object on the following topic: {user_input}. Do not mention any headers such as difficult topics, easy topics, or topic name, just the generated topics itself."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Adjust as needed
        messages=[{"role": "user", "content": prompt}]
    )
    topics = response.choices[0].message.content.strip()
    print("Topics generated.")
    return topics




def generate_quiz(user_input: List[str]) -> str:
    client = OpenAI(api_key=OPENAI_API_KEY)
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
    prompt = f"Generate a json of 5 quiz questions on the topics: {user_input}. Your response per question should be in the following format: {question_format}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Using gpt-3.5-turbo; update as needed
        messages=[{"role": "user", "content": prompt}]
    )
    quiz = response.choices[0].message.content.strip()
    print("Quiz generated.")
    return quiz




def generate_roadmap_code(user_input: List[str]) -> str:
    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = f"Generate a json object with a roadmap for the following topic: {user_input}. The roadmap should be in the format of every parent node having a list of child nodes, and each child node having a list of sub-child nodes and so on."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Using gpt-3.5-turbo; update as needed
        messages=[{"role": "user", "content": prompt}]
    )
    roadmap_code = response.choices[0].message.content.strip()
    print("Roadmap generated.")
    return roadmap_code