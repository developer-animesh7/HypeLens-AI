"""
AI Visual Search API
Minimal backend for: Detect → Crop → Preprocess → CLIP Embed

No FAISS, no database, no frontend, no admin
"""

import torch

# CPU Optimization - MUST be before any torch operations
torch.set_num_threads(2)
torch.set_num_interop_threads(1)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from api.visual_routes import router
from utils.logger import setup_logger
from config import API_HOST, API_PORT, API_RELOAD, LOG_LEVEL

# Setup logging
logger = setup_logger("ai_visual_search", level=getattr(logging, LOG_LEVEL))

# Create FastAPI app
app = FastAPI(
    title="AI Visual Search API",
    description="Fashion object detection + CLIP embeddings",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI Visual Search",
        "version": "1.0.0",
        "endpoints": {
            "detect": "/api/visual/detect-objects",
            "embed": "/api/visual/embed"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    logger.info("🔥 Starting AI Visual Search API...")
    logger.info(f"📍 Endpoints:")
    logger.info(f"   POST /api/visual/detect-objects - Detect fashion objects")
    logger.info(f"   POST /api/visual/embed - Generate CLIP embeddings")
    
    uvicorn.run(
        app,  # Pass app object directly, not string
        host=API_HOST,
        port=API_PORT,
        reload=False  # Disable reload to prevent torch thread errors
    )
