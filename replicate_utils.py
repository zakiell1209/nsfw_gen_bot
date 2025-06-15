import os
import replicate

REPLICATE_TOKEN = os.getenv("REPLICATE_TOKEN")
if not REPLICATE_TOKEN:
    raise RuntimeError("REPLICATE_TOKEN не установлен")
client = replicate.Client(api_token=REPLICATE_TOKEN)

def generate_image(prompt: str, model: str) -> str:
    version = {
        "anime": "aitechtree/nsfw-novel-generation:latest",
        "realism": "aitechtree/nsfw-novel-generation:latest"
    }[model]
    output = client.run(version, input={"prompt": prompt})
    return output[0]

def generate_video(prompt: str) -> str:
    version = "cjwbw/video-to-video:latest"
    output = client.run(version, input={"prompt": prompt})
    return output[0]