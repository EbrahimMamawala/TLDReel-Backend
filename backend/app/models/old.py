import os
import uuid
import subprocess
import time
import tempfile
import json
import requests

from pydantic import BaseModel
from typing import List, Optional

from openai import OpenAI
from moviepy import *

# Load environment variables from .env
from dotenv import load_dotenv
load_dotenv('.env')

# Retrieve API keys from the environment
from app.config import OPENAI_API_KEY, ELEVENLABS_API_KEY
# openai.api_key = OPENAI_API_KEY
FAL_KEY = os.environ["OPENAI_API_KEY"]

# Initialize ElevenLabs client
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize fal_client (this uses FAL_KEY from your env automatically)
import fal_client

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

# ---------------------------
# ElevenLabs TTS: Convert text to speech and save as file
# ---------------------------
def text_to_speech_file(text: str) -> str:
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
    save_file_path = f"{uuid.uuid4()}.mp3"
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)
    print(f"Audio saved to {save_file_path}")
    return save_file_path

# ---------------------------
# fal.ai Lipsync: Generate avatar video using lipsync model
# ---------------------------
def generate_avatar_video(audio_file: str) -> str:
    """
    Uploads the audio file and calls the lipsync API.
    Returns the local path of the generated avatar video.
    """
    # Upload the audio file using fal_client
    audio_url = fal_client.upload_file(audio_file)
    print(f"Audio uploaded. URL: {audio_url}")
    
    # Use a predetermined avatar video URL for the source
    source_video_url = "https://raw.githubusercontent.com/TMElyralab/MuseTalk/main/data/video/sun.mp4"
    
    # Submit a request to the lipsync model.
    handler = fal_client.submit(
        "fal-ai/musetalk",
        arguments={
            "source_video_url": source_video_url,
            "audio_url": audio_url
        },
        webhook_url=None  # Synchronous mode; you can use websockets in production
    )
    request_id = handler.request_id
    print(f"Lipsync request submitted with id: {request_id}")
    
    # Poll for status until completed.
    status = fal_client.status("fal-ai/musetalk", request_id, with_logs=True)
    # Instead of status.get("completed"), use attribute access.
    start_time = time.time()
    max_wait = 300  # seconds
    while True:
        # Convert status object to string for a general check:
        status_str = str(status)
        # Check if any log indicates that download has reached 100%
        logs = getattr(status, "logs", [])
        download_complete = any("100.00%" in log.get("message", "") for log in logs)
        if download_complete:
            print("Download complete detected in logs. Breaking polling loop.")
            break
        elapsed = time.time() - start_time
        if elapsed > max_wait:
            print("Timeout reached. Breaking out of polling loop.")
            break

    print("Waiting for avatar video generation... Current status:", status_str)
    time.sleep(5)
    status = fal_client.status("fal-ai/musetalk", request_id, with_logs=True)

    
    result = fal_client.result("fal-ai/musetalk", request_id)
    video_url = result.get("video", {}).get("url")
    print(f"Avatar video URL: {video_url}")
    
    # Download the resulting video file.
    response = requests.get(video_url)
    video_file = f"{uuid.uuid4()}.mp4"
    with open(video_file, "wb") as f:
        f.write(response.content)
    print(f"Avatar video saved to {video_file}")
    return video_file

# ---------------------------
# Generate Manim Code using OpenAI GPT‑4
# ---------------------------

def generate_manim_code(scene_text: str) -> str:
    prompt = f"Generate manim code that produces an animation visualizing: {scene_text}"
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    manim_code = response.choices[0].message.content.strip()

    print("Manim code generated.")
    return manim_code

# ---------------------------
# Render Manim Video: Save manim code to a file and call manim CLI to render it.
# ---------------------------
def render_manim_video(manim_code: str, output_filename: str) -> str:
    temp_dir = tempfile.gettempdir()
    code_filename = os.path.join(temp_dir, f"{uuid.uuid4()}_animation.py")
    with open(code_filename, "w") as f:
        f.write(manim_code)
    # Assume the generated code defines a Scene class called "Scene"
    cmd = ["manim", "-ql", code_filename, "Scene", "-o", output_filename]
    print("Rendering manim animation...")
    subprocess.run(cmd, check=True)
    print(f"Manim animation saved to {output_filename}")
    return output_filename

# ---------------------------
# Compose a Scene: Overlay manim video (upper half) and avatar video (lower half)
# ---------------------------
def compose_scene(manim_video: str, avatar_video: str) -> VideoFileClip:
    final_width, final_height = 1280, 720

    clip_manim = VideoFileClip(manim_video).resize((final_width, final_height // 2))
    clip_avatar = VideoFileClip(avatar_video).resize((final_width, final_height // 2))
    
    duration = min(clip_manim.duration, clip_avatar.duration)
    background = ColorClip(size=(final_width, final_height), color=(0, 0, 0), duration=duration)
    
    clip_manim = clip_manim.set_position(("center", 0))
    clip_avatar = clip_avatar.set_position(("center", final_height // 2))
    
    composite = CompositeVideoClip([background, clip_manim.set_start(0), clip_avatar.set_start(0)])
    composite = composite.set_duration(duration)
    return composite

# ---------------------------
# Create Final Reel: Process all scenes and stitch them together.
# ---------------------------
def create_final_reel(storyboard: Storyboard) -> str:
    scene_clips = []
    for scene in storyboard.scenes:
        print(f"Processing {scene.id}...")
        # Generate narration audio for the scene.
        audio_file = text_to_speech_file(scene.narration)
        # Generate avatar video using the lipsync model.
        avatar_video = generate_avatar_video(audio_file)
        # Generate manim code for the scene’s visual.
        manim_code = generate_manim_code(scene.manim_prompt)
        # Render the manim animation video.
        manim_video_file = f"{uuid.uuid4()}_manim.mp4"
        render_manim_video(manim_code, manim_video_file)
        # Compose the scene clip (manim on top, avatar below).
        scene_clip = compose_scene(manim_video_file, avatar_video)
        scene_clips.append(scene_clip)
    
    final_reel = concatenate_videoclips(scene_clips, method="compose")
    output_reel = "final_reel.mp4"
    final_reel.write_videofile(output_reel, codec="libx264", audio_codec="aac")
    print("Final reel rendering complete.")
    return output_reel

# ---------------------------
# Main orchestration function
# ---------------------------
def main(topic_prompt: str):
    print("Generating storyboard...")
    storyboard = generate_storyboard(topic_prompt)
    print("Storyboard:")
    # Using model_dump_json for pretty printing with Pydantic v2
    print(storyboard.model_dump_json(indent=2))
    
    print("Creating final reel...")
    reel_path = create_final_reel(storyboard)
    print(f"Final reel available at: {reel_path}")

if __name__ == "__main__":
    main("Quantum Entanglement")