#!/usr/bin/python3
from datetime import datetime, timezone
from pathlib import Path
import re
from uuid import uuid4

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

# ---------------------------------------------------------------
# Settings
# ---------------------------------------------------------------
BASE_DIR = Path(__file__).parent
RECORDINGS_DIR = BASE_DIR / "recordings"   # audio files are saved here
RECORDINGS_DIR.mkdir(exist_ok=True)        # create the folder if it's missing

MAX_BYTES = 25 * 1024 * 1024               # refuse files bigger than 25 MB

# Browsers record in different formats (Chrome/Firefox: webm, Safari: mp4).
# audio type  ->  file extension we save it with
ALLOWED_TYPES = {
    "audio/webm": "webm",
    "audio/ogg": "ogg",
    "audio/mp4": "m4a",
    "audio/mpeg": "mp3",
    "audio/wav": "wav",
    "audio/x-wav": "wav",
}
# file extension  ->  audio type we tell the browser when playing it back
EXTENSION_TO_TYPE = {
    "webm": "audio/webm",
    "ogg": "audio/ogg",
    "m4a": "audio/mp4",
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
}

# Our ids look like 20261007-143015-a1b2c3 (date, time, random part).
# Checking ids against this pattern stops people from asking for
# files like "../../secrets" (a "path traversal" attack).
ID_PATTERN = re.compile(r"^\d{8}-\d{6}-[0-9a-f]{6}$")

# ---------------------------------------------------------------
# Create the app
# ---------------------------------------------------------------
app = FastAPI(title="Voice Recorder API")

# CORS: lets the React dev server (a different "origin") call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------
# What we send back to the browser
# ---------------------------------------------------------------
class Recording(BaseModel):
    id: str
    filename: str
    size_bytes: int
    created_at: datetime


# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------
def describe(path: Path) -> Recording:
    """Build a Recording from a file on disk."""
    # The first 15 characters of the name are the date and time (in UTC)
    created = datetime.strptime(path.stem[:15], "%Y%m%d-%H%M%S")
    return Recording(
        id=path.stem,
        filename=path.name,
        size_bytes=path.stat().st_size,
        created_at=created.replace(tzinfo=timezone.utc),
    )


def find_file(recording_id: str) -> Path:
    """Find the file for an id, or answer 404 (not found)."""
    if ID_PATTERN.match(recording_id):
        for path in RECORDINGS_DIR.glob(f"{recording_id}.*"):
            return path
    raise HTTPException(status_code=404, detail="Recording not found")


# ---------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------
# test endpoint (the React app doesn't need it, but it's handy)
@app.get("/")
def home():
    return {"message": "Voice Recorder API", "saved": len(list_recordings())}


# Save a new recording
@app.post("/recordings", response_model=Recording, status_code=201)
async def upload_recording(file: UploadFile):
    # 1. Check the type. The browser says "audio/webm;codecs=opus",
    #    so we cut off everything after the ";"
    audio_type = (file.content_type or "").split(";")[0].strip().lower()
    if audio_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail=f"Unsupported file type: {audio_type or 'unknown'}")

    # 2. Make our own safe file name. We never use the name the browser sent.
    now = datetime.now(timezone.utc)
    recording_id = f"{now:%Y%m%d-%H%M%S}-{uuid4().hex[:6]}"
    path = RECORDINGS_DIR / f"{recording_id}.{ALLOWED_TYPES[audio_type]}"

    # 3. Save it in 1 MB pieces, stopping if it gets too big
    size = 0
    too_big = False
    with open(path, "wb") as out:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_BYTES:
                too_big = True
                break
            out.write(chunk)

    if too_big or size == 0:
        path.unlink()  # remove the half-written file
        if too_big:
            raise HTTPException(status_code=413, detail="Recording is too large (25 MB max)")
        raise HTTPException(status_code=400, detail="The recording is empty")

    return describe(path)


# List every saved recording, newest first
@app.get("/recordings", response_model=list[Recording])
def list_recordings():
    files = [
        path
        for path in RECORDINGS_DIR.iterdir()
        if ID_PATTERN.match(path.stem) and path.suffix[1:] in EXTENSION_TO_TYPE
    ]
    # The names start with the date, so sorting the names sorts by time
    return [describe(path) for path in sorted(files, reverse=True)]


# Play (or download) one recording
@app.get("/recordings/{recording_id}/audio")
def get_audio(recording_id: str, download: bool = False):
    path = find_file(recording_id)
    return FileResponse(
        path,
        media_type=EXTENSION_TO_TYPE[path.suffix[1:]],
        filename=path.name,
        # "inline" = play in the page, "attachment" = save to disk
        content_disposition_type="attachment" if download else "inline",
    )


# Delete one recording
@app.delete("/recordings/{recording_id}")
def delete_recording(recording_id: str):
    find_file(recording_id).unlink()
    return {"deleted": recording_id}


# start our server
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)