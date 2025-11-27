"""
Visual Search API Routes
Two endpoints only: detect + embed
"""

from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from typing import Optional
import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from detector.grounding_dino_sam2_detector import GroundingDINOSAM2Detector
from embedder.clip_embedder import CLIPEmbedder
from embedder.preprocess import crop_image
from utils.image_utils import bytes_to_pil
from utils.timer import timer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/visual", tags=["Visual Search"])

# Initialize singletons
detector = GroundingDINOSAM2Detector()
embedder = CLIPEmbedder()


@router.post("/detect-objects")
async def detect_objects(
    file: UploadFile = File(...),
    confidence: Optional[float] = Query(None, description="Confidence threshold (default 0.18)"),
    max_detections: Optional[int] = Query(None, description="Max detections (default 25)")
):
    """
    Detect fashion objects in uploaded image
    
    Returns:
        {
            "detections": [
                {
                    "bbox": [x1, y1, x2, y2],
                    "label": "shirt",
                    "confidence": 0.85,
                    "class_id": 0
                }
            ],
            "image_size": [width, height]
        }
    """
    try:
        # Read image bytes
        image_bytes = await file.read()
        
        # Run detection
        with timer("Object Detection"):
            result = detector.detect_objects(
                image_bytes=image_bytes,
                confidence_threshold=confidence,
                max_detections=max_detections
            )
        
        return result
    
    except Exception as e:
        logger.error(f"Detection failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


@router.post("/embed")
async def embed_image(
    file: UploadFile = File(...),
    bbox: Optional[str] = Query(None, description="Bounding box as 'x1,y1,x2,y2' to crop before embedding")
):
    """
    Generate CLIP embedding for uploaded image (or cropped region)
    
    Args:
        file: Image file
        bbox: Optional bounding box to crop (format: "x1,y1,x2,y2")
    
    Returns:
        {
            "embedding": [768-dim array],
            "dimension": 768,
            "cropped": true/false,
            "bbox": [x1, y1, x2, y2] (if cropped)
        }
    """
    try:
        # Read image bytes
        image_bytes = await file.read()
        image = bytes_to_pil(image_bytes)
        
        # Crop if bbox provided
        cropped = False
        crop_bbox = None
        if bbox:
            try:
                x1, y1, x2, y2 = map(float, bbox.split(','))
                crop_bbox = [x1, y1, x2, y2]
                image = crop_image(image, crop_bbox)
                cropped = True
                logger.info(f"Cropped image with bbox: {crop_bbox}")
            except Exception as e:
                logger.warning(f"Failed to parse bbox '{bbox}': {e}")
        
        # Generate embedding
        with timer("CLIP Embedding"):
            embedding = embedder.get_embedding(image)
        
        return {
            "embedding": embedding.tolist(),
            "dimension": len(embedding),
            "cropped": cropped,
            "bbox": crop_bbox if cropped else None
        }
    
    except Exception as e:
        logger.error(f"Embedding failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")
