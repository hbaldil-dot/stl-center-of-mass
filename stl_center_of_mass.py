from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from stl import mesh
import tempfile
import os

app = FastAPI(title="STL Center of Mass API")

# Frontend erişimi için CORS izni
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ana sayfa (Root Endpoint)
@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "STL Center of Mass API is running!",
        "docs": "/docs"
    }

# STL Analiz Endpoint'i
@app.post("/analyze")
async def analyze_stl(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".stl"):
        raise HTTPException(status_code=400, detail="Lütfen geçerli bir .stl dosyası yükleyin.")

    # Geçici dosya oluştur ve yüklenen veriyi yaz
    with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        # STL dosyasını analiz et
        your_mesh = mesh.Mesh.from_file(tmp_path)
        volume, cog, inertia = your_mesh.get_mass_properties()

        # Hacim hesabı (mm³ -> cm³)
        volume_cm3 = volume / 1000.0

        return {
            "filename": file.filename,
            "volume_cm3": round(volume_cm3, 3),
            "center_of_mass": {
                "x_mm": round(float(cog[0]), 3),
                "y_mm": round(float(cog[1]), 3),
                "z_mm": round(float(cog[2]), 3)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STL işlenirken hata oluştu: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
