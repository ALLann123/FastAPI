#!/usr/bin/python3
import cv2
import numpy as np
import pytesseract
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool

#an object
app=FastAPI(title="OCR API")

# Allow the react dev server to call this API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text(image_bytes:bytes)->str:
    """Original script adapted to work with bytes"""
    # Turn  raw bytes into an opencv image
    array=np.frombuffer(image_bytes, dtype=np.uint8)
    image=cv2.imdecode(array, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Could not read the image")

    # convert to greyscale
    gray=cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    #more black and white
    _, threshold=cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # read the text
    return pytesseract.image_to_string(threshold, lang="eng+deu+swa")


@app.get("/")
def health_check():
    return {"status":"ok"}

@app.post("/ocr")
async def ocr(file: UploadFile=File(...)):
    #basic validation to only accept images
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file")

    image_bytes=await file.read()

    try:
        # OCR is slow and blocking, so run it in a worker thread
        text=await run_in_threadpool(extract_text, image_bytes)

    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))

    return {"filename":file.filename, "text":text.strip()}
