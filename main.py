import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.database import init_db
from backend.routes.auth_routes import router as auth_router
from backend.routes.predict_routes import router as predict_router
from backend.routes.history_routes import router as history_router
from backend.routes.sensor_routes import router as sensor_router

# Initialize database schema and tables
init_db()

app = FastAPI(
    title="AI Heart Disease Detection & Clinical Screening API",
    description="Full-stack AI-powered cardiovascular risk assessment platform utilizing UCI Heart Disease Machine Learning model with clinical feature attribution.",
    version="2.0.0"
)

# Enable CORS for local development and API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include backend API routers
app.include_router(auth_router)
app.include_router(predict_router)
app.include_router(history_router)
app.include_router(sensor_router)

@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "AI Heart Disease Detection API",
        "version": "2.0.0"
    }

# Mount static frontend files
FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "Frontend not found, please check frontend/index.html"}

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        file_path = FRONTEND_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        # Fallback to index.html for SPA client-side routing
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return FileResponse(str(FRONTEND_DIR / "index.html"))
