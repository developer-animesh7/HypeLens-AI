"""
Image preprocessing for CLIP embeddings
224x224, square padding, quality checks
"""

import numpy as np
from PIL import Image, ImageOps
from typing import Tuple
import logging

logger = logging.getLogger(__name__)

TARGET_SIZE = (224, 224)
MIN_SIZE = 50  # Minimum dimension
MAX_SIZE = 2000  # Maximum dimension


def preprocess_for_clip(image: Image.Image) -> Tuple[Image.Image, dict]:
    """
    Preprocess image for CLIP embedding
    
    Steps:
    1. Quality check (size validation)
    2. Square pad to maintain aspect ratio
    3. Resize to 224x224
    4. Convert to RGB
    
    Args:
        image: PIL Image
    
    Returns:
        (processed_image, metadata)
    """
    metadata = {
        "original_size": image.size,
        "original_mode": image.mode
    }
    
    # 1. Quality check
    w, h = image.size
    if w < MIN_SIZE or h < MIN_SIZE:
        raise ValueError(f"Image too small: {w}x{h}. Minimum is {MIN_SIZE}x{MIN_SIZE}")
    
    if w > MAX_SIZE or h > MAX_SIZE:
        logger.warning(f"Image very large: {w}x{h}. Resizing before processing")
        image.thumbnail((MAX_SIZE, MAX_SIZE), Image.Resampling.LANCZOS)
        w, h = image.size
    
    # 2. Convert to RGB
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    # 3. Square pad (maintain aspect ratio)
    max_dim = max(w, h)
    padded = Image.new("RGB", (max_dim, max_dim), (255, 255, 255))
    offset = ((max_dim - w) // 2, (max_dim - h) // 2)
    padded.paste(image, offset)
    
    metadata["padded_size"] = (max_dim, max_dim)
    metadata["padding_offset"] = offset
    
    # 4. Resize to 224x224
    resized = padded.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
    
    metadata["final_size"] = TARGET_SIZE
    
    logger.debug(f"Preprocessed: {image.size} → {TARGET_SIZE}")
    
    return resized, metadata


def crop_image(image: Image.Image, bbox: list) -> Image.Image:
    """
    Crop image using bounding box
    
    Args:
        image: PIL Image
        bbox: [x1, y1, x2, y2] in pixel coordinates
    
    Returns:
        Cropped PIL Image
    """
    x1, y1, x2, y2 = bbox
    
    # Ensure valid bbox
    w, h = image.size
    x1 = max(0, min(x1, w))
    y1 = max(0, min(y1, h))
    x2 = max(0, min(x2, w))
    y2 = max(0, min(y2, h))
    
    if x2 <= x1 or y2 <= y1:
        raise ValueError(f"Invalid bbox: {bbox}")
    
    cropped = image.crop((x1, y1, x2, y2))
    
    return cropped
