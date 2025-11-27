"""Image utilities for visual search"""

import io
from PIL import Image
from typing import Union
import logging

logger = logging.getLogger(__name__)


def bytes_to_pil(image_bytes: bytes) -> Image.Image:
    """Convert bytes to PIL Image"""
    return Image.open(io.BytesIO(image_bytes)).convert("RGB")


def pil_to_bytes(image: Image.Image, format: str = "PNG") -> bytes:
    """Convert PIL Image to bytes"""
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    return buffer.getvalue()


def validate_image(image_bytes: bytes) -> bool:
    """Validate if bytes represent a valid image"""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()
        return True
    except Exception as e:
        logger.warning(f"Invalid image: {e}")
        return False


def resize_image(image: Image.Image, max_size: int = 800) -> Image.Image:
    """Resize image maintaining aspect ratio"""
    w, h = image.size
    
    if w <= max_size and h <= max_size:
        return image
    
    if w > h:
        new_w = max_size
        new_h = int(h * max_size / w)
    else:
        new_h = max_size
        new_w = int(w * max_size / h)
    
    return image.resize((new_w, new_h), Image.Resampling.LANCZOS)
