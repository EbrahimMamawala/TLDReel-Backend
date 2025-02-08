import os
import uuid
import base64
import requests
import shutil
import tempfile
import logging
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

# MoviePy imports
from moviepy import *

# ElevenLabs imports
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from pydub import AudioSegment

# Load environment variables
load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
# (Assume OPENAI_API_KEY is set in your environment for your endpoints if needed)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
# Storyboard Generation (sample version)
# ---------------------------
def generate_storyboard(topic: str) -> Storyboard:
    # For demo, using fixed sample scenes.
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
    return Storyboard(**sample)

# ---------------------------
# ElevenLabs TTS (MP3 generation)
# ---------------------------
def text_to_speech_file(text: str) -> str:
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    response = client.text_to_speech.convert(
        voice_id="pNInz6obpgDQGcFmaJgB",  # Adam's pre-made voice
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2_5",
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
        ),
    )
    mp3_file = f"{uuid.uuid4()}.mp3"
    with open(mp3_file, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)
    logger.info(f"Audio saved to {mp3_file}")
    return mp3_file

# ---------------------------
# Convert MP3 to WAV using pydub
# ---------------------------
def convert_mp3_to_wav(mp3_file: str) -> str:
    sound = AudioSegment.from_mp3(mp3_file)
    wav_file = mp3_file.replace(".mp3", ".wav")
    sound.export(wav_file, format="wav")
    logger.info(f"Converted {mp3_file} to {wav_file}")
    return wav_file

# ---------------------------
# Generate Avatar Video via Lipsync Endpoint
# ---------------------------
def generate_avatar_video(audio_file: str) -> str:
    # Endpoint URL for avatar video generation (expects a data URI for audio)
    avatar_url = "https://zolpj03o19vuv8-5000.proxy.runpod.net/predict"
    with open(audio_file, "rb") as af:
        audio_data = af.read()
    audio_base64 = base64.b64encode(audio_data).decode("utf-8")
    # Use MIME type for wav file.
    audio_data_uri = f"data:audio/wav;base64,{audio_base64}"
    payload = {
        "reference": "https://raw.githubusercontent.com/adarshxs/temp/refs/heads/main/ladki.jpg",
        "audio": audio_data_uri,
        "animation_mode": "human"
    }
    logger.info("Calling avatar video endpoint with payload.")
    try:
        response = requests.post(avatar_url, json=payload, timeout=30)
        response.raise_for_status()
        avatar_video_file = f"avatar_{uuid.uuid4()}.mp4"
        with open(avatar_video_file, "wb") as f:
            f.write(response.content)
        logger.info(f"Avatar video saved as {avatar_video_file}")
        return avatar_video_file
    except requests.exceptions.RequestException as e:
        logger.error(f"Error in generate_avatar_video: {e}")
        if e.response is not None:
            logger.error(f"Response details: {e.response.text}")
        raise

# ---------------------------
# Generate Manim Video via Endpoint
# ---------------------------
def generate_manim_video(topic: str) -> str:
    # Endpoint URL for Manim video generation
    manim_url = "https://zolpj03o19vuv8-4000.proxy.runpod.net/generate_manim"
    payload = {"prompt": f"Create a Manim animation that explains the basics of {topic}."}
    logger.info("Calling Manim generation endpoint.")
    try:
        response = requests.post(manim_url, json=payload, timeout=300)
        response.raise_for_status()
        manim_video_file = f"manim_{uuid.uuid4()}.mp4"
        with open(manim_video_file, "wb") as f:
            f.write(response.content)
        logger.info(f"Manim video saved as {manim_video_file}")
        return manim_video_file
    except requests.exceptions.RequestException as e:
        logger.error(f"Error in generate_manim_video: {e}")
        if e.response is not None:
            logger.error(f"Response details: {e.response.text}")
        raise

# ---------------------------
# Combine Videos Vertically using MoviePy
# ---------------------------
def combine_videos(upper_video: str, lower_video: str, output_file: str) -> str:
    clip_upper = VideoFileClip(upper_video)
    clip_lower = VideoFileClip(lower_video)
    # Optionally, resize clips so that their widths match.
    final_clip = clips_array([[clip_upper], [clip_lower]])
    final_clip.write_videofile(output_file, codec="libx264")
    return output_file

# ---------------------------
# Create Final Reel Pipeline
# ---------------------------
def create_final_reel(topic: str) -> str:
    # 1. Generate storyboard (we use a sample storyboard for now).
    storyboard = generate_storyboard(topic)
    # For this pipeline, we use the narration of the first scene.
    scene = storyboard.scenes[0]
    logger.info(f"Processing scene: {scene.id}")

    # 2. Generate narration audio.
    mp3_audio = text_to_speech_file(scene.narration)
    # 3. Convert MP3 to WAV.
    wav_audio = convert_mp3_to_wav(mp3_audio)
    # 4. Generate avatar video using the WAV audio.
    avatar_video = generate_avatar_video(wav_audio)
    # 5. Generate Manim animation video via the endpoint.
    manim_video = generate_manim_video(topic)
    # 6. Combine the two videos vertically.
    final_reel = f"final_reel_{uuid.uuid4()}.mp4"
    combined = combine_videos(manim_video, avatar_video, final_reel)
    logger.info(f"Final reel generated at: {combined}")
    return combined

# ---------------------------
# Main Orchestration Function
# ---------------------------
def main(topic_prompt: str):
    print("Generating final reel...")
    final_reel_path = create_final_reel(topic_prompt)
    print(f"Final reel available at: {final_reel_path}")

if __name__ == "__main__":
    main("Quantum Entanglement")