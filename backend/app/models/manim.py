import tempfile
import subprocess
import uuid
import os
# Use the new OpenAI library interface (if needed, ensure it's updated)
from openai import OpenAI  
from moviepy import *

# Load environment variables from .env
from dotenv import load_dotenv
load_dotenv('.env')

# Retrieve API keys from the environment
#from app.config import OPENAI_API_KEY, ELEVENLABS_API_KEY
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ---------------------------
# Generate Manim Code using OpenAI GPT‑4
# ---------------------------
def generate_manim_code(scene_text: str) -> str:
    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = f"Generate manim code that produces an animation visualizing: {scene_text}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Using gpt-3.5-turbo; update as needed
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
# Create Final Reel: Process all scenes and stitch them together.
# ---------------------------
def create_final_reel(storyboard: Storyboard) -> str:
    scene_clips = []
    for scene in storyboard.scenes:
        print(f"Processing {scene.id}...")
        # Generate manim code for the scene’s visual.
        manim_code = generate_manim_code(scene.manim_prompt)
        # Render the manim animation video.
        manim_video_file = f"{uuid.uuid4()}_manim.mp4"
        render_manim_video(manim_code, manim_video_file)
        # Compose the scene clip (manim on top, avatar below).
        scene_clip = compose_scene(manim_video_file)
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
    print(storyboard.model_dump_json(indent=2))  # Using model_dump_json for pretty printing with Pydantic v2
    
    print("Creating final reel...")
    reel_path = create_final_reel(storyboard)
    print(f"Final reel available at: {reel_path}")

if __name__ == "__main__":
    main("Quantum Entanglement")