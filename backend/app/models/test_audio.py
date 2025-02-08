from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
import os

load_dotenv()
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# Convert the generator to bytes
audio_bytes = b''.join(client.text_to_speech.convert(
    text="The first move is what sets everything in motion. I had idly for breakfast today.",
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_multilingual_v2",
    output_format="mp3_44100_128"
))

# Save the audio to a file
with open("output.mp3", "wb") as f:
    f.write(audio_bytes)
print("Audio saved to output.mp3")