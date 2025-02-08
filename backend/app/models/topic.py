import os
# Use the new OpenAI library interface (if needed, ensure it's updated)
from openai import OpenAI   # type: ignore
from moviepy import * # type: ignore
from  pydantic import BaseModel # type: ignore
from typing import List, Optional, Dict, Any
# Load environment variables from .env
from dotenv import load_dotenv # type: ignore
load_dotenv('.env')

def generate_topics(user_input: List[str]) -> Dict[str, Any]:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = f"Generate an array each of 5 difficult, 5 medium and 5 easy topics nested in a parent json object on the following topic: {user_input}. Do not mention any headers such as difficult topics or easy topics or topic name, just the generated topics itself"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Using gpt-3.5-turbo; update as needed
        messages=[{"role": "user", "content": prompt}]
    )
    topics = response.choices[0].message.content.strip()
    print("Topics generated.")
    return topics