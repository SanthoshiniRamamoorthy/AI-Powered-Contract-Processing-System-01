# main.py

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import contract
from app.utils.logger import logger

# Initialize FastAPI app
app = FastAPI(
    title="AI-Powered Contract Processing System",
    description="Automated contract analysis, risk scoring, and summarization using AI",
    version="1.0.0"
)

# Configure CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(contract.router, prefix="/contracts", tags=["Contract Analysis"])

@app.get("/")
async def root():
    """
    Health check endpoint
    """
    return {
        "message": "AI-Powered Contract Processing System is running",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """
    Detailed health check endpoint
    """
    return {
        "status": "healthy",
        "service": "contract-analysis-api",
        "endpoints": {
            "analyze": "/contracts/analyze/"
        }
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 AI Contract Processing System started successfully")
    logger.info("📍 API available at: http://127.0.0.1:8000")
    logger.info("📖 Documentation at: http://127.0.0.1:8000/docs")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 AI Contract Processing System shutting down")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )