from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import ezdxf

app = FastAPI()

# Ensure directories exist
UPLOAD_DIR = "uploads"
MODIFIED_DIR = "modified"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(MODIFIED_DIR, exist_ok=True)

app.mount("/", StaticFiles(directory="caterfab_dxf_plugin", html=True), name="static")

@app.post("/upload_dxf")
async def upload_dxf(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return {"filename": file.filename, "message": "Upload successful"}

@app.get("/extract_data")
def extract_data(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"error": "File not found"})

    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()
    entities = []
    for e in msp:
        if e.dxftype() in ["LINE", "LWPOLYLINE"]:
            entities.append({
                "type": e.dxftype(),
                "layer": e.dxf.layer
            })
    return {"filename": filename, "entities": entities}

@app.post("/amend_drawing")
def amend_drawing(filename: str = Form(...), new_length: float = Form(...)):
    input_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(input_path):
        return JSONResponse(status_code=404, content={"error": "File not found"})

    doc = ezdxf.readfile(input_path)
    msp = doc.modelspace()
    msp.add_line((0, 0), (new_length, 0))

    output_path = os.path.join(MODIFIED_DIR, f"modified_{filename}")
    doc.saveas(output_path)
    return {
        "message": "Drawing modified",
        "download": f"/download_dxf?filename=modified_{filename}"
    }

@app.get("/download_dxf")
def download_dxf(filename: str):
    file_path = os.path.join(MODIFIED_DIR, filename)
    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"error": "File not found"})
    return FileResponse(path=file_path, media_type='application/dxf', filename=filename)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000, reload=True)

