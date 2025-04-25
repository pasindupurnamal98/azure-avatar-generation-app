import os
import json
import uuid
import time
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
from typing import Optional

# Configuration
SPEECH_ENDPOINT = os.getenv('SPEECH_ENDPOINT', "https://eastus2.api.cognitive.microsoft.com")
SUBSCRIPTION_KEY = os.getenv("SUBSCRIPTION_KEY", "8792702cb8b545d0859dc0183a425cd3")
API_VERSION = "2024-04-15-preview"
VIDEO_STORAGE_PATH = "videos"

# FastAPI setup
app = FastAPI()


class AvatarRequest(BaseModel):
    script_text: str
    voice: str
    avatar: str
    style: str
    # backgroundImage: str



def authenticate_headers():
    return {
        "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY,
        "Content-Type": "application/json"
    }


def create_payload(script_text: str, voice: str, avatar: str, style: str,):
    return {
        "synthesisConfig": {
            "voice": voice
        },
        "inputKind": "plainText",
        "inputs": [
            {"content": script_text}
        ],
        "avatarConfig": {
            "customized": False,
            "talkingAvatarCharacter": avatar,
            # "talkingAvatarStyle": "casual",
            "talkingAvatarStyle": style,
            "videoFormat": "mp4",
            "videoCodec": "h264",
            "subtitleType": "soft_embedded",
            "backgroundColor": "#FFFFFFFF"
            # "backgroundImage": backgroundImage
        }
    }


@app.post("/generate-avatar")
def generate_avatar(req: AvatarRequest):
    job_id = str(uuid.uuid4())
    url = f"{SPEECH_ENDPOINT}/avatar/batchsyntheses/{job_id}?api-version={API_VERSION}"

    headers = authenticate_headers()
    payload = create_payload(req.script_text, req.voice, req.avatar,req.style)

    response = requests.put(url, headers=headers, data=json.dumps(payload))
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    # Poll for status
    status_url = f"{SPEECH_ENDPOINT}/avatar/batchsyntheses/{job_id}?api-version={API_VERSION}"
    for _ in range(30):
        time.sleep(5)
        status_response = requests.get(status_url, headers=headers)
        status_json = status_response.json()
        if status_json.get("status") == "Succeeded":
            video_url = status_json["outputs"]["result"]
            break
        elif status_json.get("status") == "Failed":
            raise HTTPException(status_code=500, detail="Avatar job failed")
    else:
        raise HTTPException(status_code=504, detail="Avatar generation timed out")

    # Download video
    os.makedirs(VIDEO_STORAGE_PATH, exist_ok=True)
    video_filename = f"{job_id}.mp4"
    video_path = os.path.join(VIDEO_STORAGE_PATH, video_filename)
    video_response = requests.get(video_url)
    with open(video_path, "wb") as f:
        f.write(video_response.content)

    return {"download_url": f"/download-video/{video_filename}"}


@app.get("/download-video/{filename}")
def download_video(filename: str):
    path = os.path.join(VIDEO_STORAGE_PATH, filename)
    if os.path.exists(path):
        return FileResponse(path, media_type="video/mp4", filename=filename)
    raise HTTPException(status_code=404, detail="Video not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app4:app", host="0.0.0.0", port=8000, reload=True)

