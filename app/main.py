from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.config import settings
from app.database.connection import get_db, init_database
from app.api.routes import router as api_router
from app.api.auth import router as auth_router
import os

# Initialize database on startup
init_database()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Sistema de Data Science para recolección y análisis de información docente"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(api_router, prefix=settings.api_prefix)
app.include_router(auth_router, prefix="/auth")

@app.get("/", response_class=HTMLResponse)
async def serve_form():
    """Serve the public form"""
    try:
        with open("static/form.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Formulario no encontrado</h1><p>El archivo del formulario no está disponible.</p>",
            status_code=404
        )

@app.get("/test", response_class=HTMLResponse)
async def serve_test_form():
    """Serve the test form for development"""
    try:
        with open("test_form.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Formulario de prueba no encontrado</h1>",
            status_code=404
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development"
    )