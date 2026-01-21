from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.database.database import engine, Base
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    yield
    # Shutdown: Clean up resources
    print("⏹️ Shutting down")

app = FastAPI(
    title="EduLLMs API",
    description="Educational LLM Chat Backend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Import routers
from app.api.endpoints import router as api_router
from app.api.websocket import router as ws_router

# Include routers
app.include_router(api_router, prefix="/api")
app.include_router(ws_router, prefix="/ws")

@app.get("/")
async def root():
    return {"message": "EduLLMs API is running 🚀"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}