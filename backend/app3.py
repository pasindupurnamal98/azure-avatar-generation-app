import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse

import traceback

app = FastAPI()

AZURE_AVATAR_ENDPOINT = "https://eastus2.api.cognitive.microsoft.com/avatars/generate"
AZURE_API_KEY = "8792702cb8b545d0859dc0183a425cd3"
VIDEO_STORAGE_PATH = "videos"  # local or blob path

class AvatarRequest(BaseModel):
    script_text: str
    voice: str
    avatar: str

@app.post("/generate-avatar")
def generate_avatar(req: AvatarRequest):
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_API_KEY,
        "Content-Type": "application/json"
    }
    body = {
        "script": req.script_text,
        "voice": req.voice,
        "avatar": req.avatar,
        "outputFormat": "mp4"
    }

    response = requests.post(AZURE_AVATAR_ENDPOINT, headers=headers, json=body)
    
    if response.status_code == 200:
        video_url = response.json().get("videoUrl")
        video_filename = f"{req.avatar}_{req.voice}.mp4"
        local_path = os.path.join(VIDEO_STORAGE_PATH, video_filename)

        # Download the video file
        video_response = requests.get(video_url)
        with open(local_path, "wb") as f:
            f.write(video_response.content)

        return {"download_url": f"/download-video/{video_filename}"}
    else:
        raise HTTPException(status_code=500, detail=response.text)

@app.get("/download-video/{filename}")
def download_video(filename: str):
    filepath = os.path.join(VIDEO_STORAGE_PATH, filename)
    if os.path.exists(filepath):
        return FileResponse(filepath, media_type="video/mp4", filename=filename)
    else:
        raise HTTPException(status_code=404, detail="Video not found")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)