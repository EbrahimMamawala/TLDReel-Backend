import json
import os
from openai import OpenAI  # type: ignore
from moviepy import *  # type: ignore
from pydantic import BaseModel  # type: ignore
from typing import List  # type: ignore
from dotenv import load_dotenv  # type: ignore
from db.crud import create_generated_topics, create_topic, create_quiz, create_roadmap, get_topic

load_dotenv("/backend/app/.env")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


async def summarize_text(text: str) -> str:
    prompt = f"Summarize the following text in brief, keeping only the essential details: {text}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


async def generate_topics(user_input: str, userId: str) -> str:
    MAX_LENGTH = 300
    
    if len(user_input) > MAX_LENGTH:
        print("Input is too long, summarizing first...")
        user_input = await summarize_text(user_input)
    
    prompt = (
        f"Generate a JSON object with keys 'difficult', 'medium', and 'easy', each containing an array of 5 topics, "
        f"related to: {user_input}. Return only valid JSON."
    )
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    try:
        topics = json.loads(response.choices[0].message.content.strip())  # Parse response as JSON
    except json.JSONDecodeError:
        print("Error parsing response as JSON")
        return "{}"
    
    topic_id = await create_topic(user_input, userId)  # Get the MongoDB _id

    await create_generated_topics(
        topic_id=str(topic_id),  # Convert _id to string if needed
        difficulty=topics.get("difficult", []),
        medium=topics.get("medium", []),
        easy=topics.get("easy", [])
    )
    
    print("Topics generated:", topics)
    print("Topic ID:", topic_id)
    return {"topic_id": str(topic_id)}


async def generate_quiz(topic_id: str, question: List[str]) -> dict:
    question_format = {
        "id": 1,
        "text": "What is the capital of France?",
        "options": [
            {"id": "A", "text": "London", "correct": False},
            {"id": "B", "text": "Paris", "correct": True},
            {"id": "C", "text": "Berlin", "correct": False},
            {"id": "D", "text": "Madrid", "correct": False},
        ],
    }
    
    prompt = f"Generate a JSON array of 5 quiz questions on the topics: {question}. Each question should follow this format: {json.dumps(question_format)}"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    quiz_text = response.choices[0].message.content.strip()

    try:
        quiz_json = json.loads(quiz_text)
    except json.JSONDecodeError:
        print("Invalid JSON response received")
        return {}

    print("Quiz generated.")
    return quiz_json



async def generate_roadmap(topic_id: str, user_input: List[str]) -> dict:
    question_format = {
        "webDevelopmentRoadmap": {
            "Frontend": {
                "HTML": {
                    "Basics": [
                        "HTML Syntax",
                        "Elements & Tags",
                        "Attributes"
                    ],
                    "Advanced": [
                        "Semantic HTML",
                        "SEO Best Practices",
                        "Accessibility (ARIA)"
                    ]
                },
                "CSS": {
                    "Basics": [
                        "Selectors & Properties",
                        "Box Model",
                        "Positioning & Layout"
                    ],
                    "Responsive Design": [
                        "Media Queries",
                        "Mobile-first Design"
                    ]
                }
            }
        }
    }

    prompt = (
        f"Generate a JSON object with a roadmap for the following topic: {json.dumps(user_input)}. "
        f"The roadmap should be in a hierarchical format where every parent node has child nodes, "
        f"and each child node has sub-child nodes. The output must strictly follow this structure: "
        f"{json.dumps(question_format, indent=2)}"
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    roadmap_code = response.choices[0].message.content.strip()

    try:
        roadmap_json = json.loads(roadmap_code)  # Convert response to JSON
    except json.JSONDecodeError:
        print("Error decoding roadmap JSON. Returning empty structure.")
        roadmap_json = {}

    print("Roadmap generated.")

    return roadmap_json

