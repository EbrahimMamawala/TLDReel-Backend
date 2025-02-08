import requests

# Replace with your public URL from Runpod.
url = "https://zolpj03o19vuv8-5000.proxy.runpod.net/predict"

payload = {
    # Use a known valid image URL for testing.
    "reference": "https://raw.githubusercontent.com/adarshxs/temp/refs/heads/main/ladki.jpg",
    "audio": "https://huggingface.co/datasets/adarshxs/temp-2/resolve/main/joyvasa_002.wav",
    "animation_mode": "human"
    # Include any additional keys required by your ArgumentConfig.
}

try:
    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    # If the response is a video file, save it.
    with open("output.mp4", "wb") as f:
        f.write(response.content)
    print("Success! Video saved as output.mp4")
except requests.exceptions.RequestException as e:
    print("Error:", e)
    if e.response is not None:
        print("Response details:", e.response.text)