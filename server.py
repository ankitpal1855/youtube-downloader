# start the server - uvicorn server:app --host 0.0.0.0 --port 8000
# start the server with live reload - uvicorn server:app --reload --host 0.0.0.0 --port 8000
# start hosting the frontend (index.html) python -m http.server 5500
# visit - localhost:5500
import os
import uuid
import datetime
import shutil
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from yt_dlp import YoutubeDL
from main import download_mp3, download_video
import time
from starlette.background import BackgroundTask


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def clear_folder():
    for f in os.listdir(DOWNLOAD_DIR):
        try:
            os.remove(os.path.join(DOWNLOAD_DIR, f))
        except:
            pass


def generate_filename(ext):
    now = datetime.datetime.now().strftime("%d%m%Y%H%M%S")
    return f"{now}.{ext}"


class DownloadReq(BaseModel):
    url: str
    quality: str


class MetaReq(BaseModel):
    url: str


@app.post("/meta")
async def fetch_meta(data: MetaReq):
    url = data.url
    try:
        ydl_opts = {"quiet": True, "skip_download": True}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        return {
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
        }

    except Exception as e:
        return {"error": str(e)}


@app.post("/download")
async def download_file(data: DownloadReq):
    url = data.url
    quality = data.quality

    clear_folder()

    ext = "mp3" if quality == "mp3" else "mp4"
    filename = generate_filename(ext)
    full_path = os.path.join(DOWNLOAD_DIR, filename)

    cwd = os.getcwd()
    os.chdir(DOWNLOAD_DIR)

    try:
        if quality == "mp3":
            download_mp3(url, outtmpl=filename)
        else:
            download_video(url, quality, outtmpl=filename)

        if not os.path.exists(filename):
            raise Exception("Downloaded file not found!")

    except Exception as e:
        os.chdir(cwd)
        return {"error": str(e)}

    os.chdir(cwd)

    def stream_file():
        with open(full_path, "rb") as f:
            while chunk := f.read(1024 * 1024):
                yield chunk

    # 🔥 DELETE FILE AFTER 5 MINUTES
    def delayed_delete(path):
        try:
            print(f"⏳ Waiting 5 minutes before deleting: {path}")
            time.sleep(300)  # 300 seconds = 5 minutes
            os.remove(path)
            print(f"🗑 Deleted: {path}")
        except Exception as e:
            print("Delete error:", e)

    return StreamingResponse(
        stream_file(),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
        background=BackgroundTask(delayed_delete, full_path)
    )
