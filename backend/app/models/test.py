import requests
import uuid
import base64

from pydantic import BaseModel
from typing import List, Optional

import os
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Initialize ElevenLabs client
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

# ---------------------------
# Pydantic models for storyboard
# ---------------------------
class Scene(BaseModel):
    id: str
    narration: str
    manim_prompt: str
    optional_image_prompt: Optional[str] = None

class Storyboard(BaseModel):
    scenes: List[Scene]

# ---------------------------
# Storyboard Generation using OpenAI GPT‑4
# ---------------------------
def generate_storyboard(topic: str) -> Storyboard:
    """
    Generate a storyboard JSON via GPT‑4.
    (For demonstration, we return a fixed sample.)
    """
    sample = {
        "scenes": [
            {
                "id": "scene1",
                "narration": f"Introduction to {topic}. Explaining the basics.",
                "manim_prompt": f"Create an animation that visually explains the basic principles of {topic}.",
                "optional_image_prompt": None
            },
            {
                "id": "scene2",
                "narration": f"Deep dive into {topic}. Discussing detailed aspects.",
                "manim_prompt": f"Generate an animation showing the dynamic behavior of {topic}.",
                "optional_image_prompt": None
            },
            {
                "id": "scene3",
                "narration": f"Conclusion on {topic}. Summarize the key takeaways.",
                "manim_prompt": f"Create a summary animation for {topic}.",
                "optional_image_prompt": None
            }
        ]
    }
    storyboard = Storyboard(**sample)
    return storyboard

def text_to_speech_file(text: str) -> str:
    elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    response = elevenlabs_client.text_to_speech.convert(
        voice_id="pNInz6obpgDQGcFmaJgB",  # Adam pre-made voice
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2_5",  # turbo model for low latency
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
        ),
    )
    save_file_path = f"{uuid.uuid4()}.wav"
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)
    print(f"Audio saved to {save_file_path}")
    return save_file_path


def generate_avatar_video(audio_file: str) -> str:
    # Replace with your public URL from Runpod.
    url = "https://zolpj03o19vuv8-5000.proxy.runpod.net/predict"

    payload = {
        # Use a known valid image URL for testing.
        "reference": "https://raw.githubusercontent.com/adarshxs/temp/refs/heads/main/ladki.jpg",
        "audio": "https://github.com/Adwitiya2104/TLDR/blob/master/backend/app/models/audio_file.wav",
        "animation_mode": "human"
        # Include any additional keys required by your ArgumentConfig.
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        print(response.headers)
        response.raise_for_status()
        # If the response is a video file, save it.
        with open("output.mp4", "wb") as f:
            f.write(response.content)
        print("Success! Video saved as output.mp4")
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        if e.response is not None:
            print("Response details:", e.response.text)

def create_final_reel(storyboard: Storyboard) -> str:
    for scene in storyboard.scenes:
        print(f"Processing {scene.id}...")
        # Generate narration audio for the scene.
        audio_file = text_to_speech_file(scene.narration)
        # Generate avatar video using the new lipsync function.
        avatar_video = generate_avatar_video(audio_file)
        return avatar_video
    

# ---------------------------
# Main orchestration function
# ---------------------------
def main(topic_prompt: str):
    print("Generating storyboard...")
    storyboard = generate_storyboard(topic_prompt)
    print("Storyboard:")
    print(storyboard.model_dump_json(indent=2))  # Using model_dump_json for pretty printing with Pydantic v2
    
    print("Creating final reel...")
    reel_path = create_final_reel(storyboard)
    print(f"Final reel available at: {reel_path}")

if __name__ == "__main__":
    main("Quantum Entanglement")