import os
# Use the new OpenAI library interface (if needed, ensure it's updated)
from openai import OpenAI  
from moviepy import *

# Load environment variables from .env
from dotenv import load_dotenv
load_dotenv('.env')


def generate_manim_code(user_input: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = f"Generate an array each of 5 difficult, 5 medium and 5 easy topics nested in a parent array on the following topic: {user_input}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Using gpt-3.5-turbo; update as needed
        messages=[{"role": "user", "content": prompt}]
    )
    manim_code = response.choices[0].message.content.strip()
    print("Manim code generated.")
    return manim_code