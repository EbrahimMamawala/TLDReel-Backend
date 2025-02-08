import os
# Use the new OpenAI library interface (if needed, ensure it's updated)
from openai import OpenAI   # type: ignore
from moviepy import * # type: ignore
from  pydantic import BaseModel # type: ignore
from typing import List, Optional, Dict, Any
# Load environment variables from .env
from dotenv import load_dotenv # type: ignore
load_dotenv('.env')

def generate_roadmap_code(user_input: List[str]) -> Dict[str, Any]:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = f"Generate a json object with a roadmap for the following topic: {user_input}. The roadmap should be in the format of every parent node having a list of child nodes, and each child node having a list of sub-child nodes and so on."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Using gpt-3.5-turbo; update as needed
        messages=[{"role": "user", "content": prompt}]
    )
    roadmap_code = response.choices[0].message.content.strip()
    print("Roadmap generated.")
    return roadmap_code