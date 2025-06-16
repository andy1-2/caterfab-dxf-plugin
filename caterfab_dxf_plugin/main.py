from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil

app = FastAPI(
    title="Caterfab DXF Plugin API",
    description="API for uploading, extracting, and modifying DXF files for Caterfab",
    version="1.0.0"
)

# Allow CORS for frontend or plugin tools
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (like openapi.yaml)
app.mount("/static", StaticFiles(directory="static"), name="static")

UPLOAD_DIR = "uploads"
MODIFIED_DIR = "modified"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(MODIFIED_DIR, exist_ok=True)

@app.post("/upload_dxf")
async def upload_dxf(file: UploadFile = File(...)):
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": "Upload successful", "filename": file.filename}

@app.get("/extract_data")
async def extract_data(filename: str):
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    # Simulate data extraction (replace with real logic)
    return {"entities": ["LINE", "CIRCLE", "FRAME"], "filename": filename}

@app.post("/amend_drawing")
async def amend_drawing(filename: str = Form(...), new_length: float = Form(...)):
    in_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(in_path):
        raise HTTPException(status_code=404, detail="Original file not found")

    out_path = os.path.join(MODIFIED_DIR, f"modified_{filename}")
    # Simulate modification (copy original for now)
    shutil.copy(in_path, out_path)

    return {"message": "Drawing modified", "download_url": f"/download_dxf?filename=modified_{filename}"}

@app.get("/download_dxf")
async def download_dxf(filename: str):
    file_path = os.path.join(MODIFIED_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="application/dxf", filename=filename)


