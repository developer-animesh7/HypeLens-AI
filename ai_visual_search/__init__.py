"""
AI Visual Search Package
Minimal backend for fashion object detection and CLIP embeddings
"""

__version__ = "1.0.0"
__author__ = "HypeLens AI"

from .detector import GroundingDINOSAM2Detector, FASHION_PROMPT
from .embedder import CLIPEmbedder, EMBEDDING_DIM
from .config import *

__all__ = [
    "GroundingDINOSAM2Detector",
    "CLIPEmbedder",
    "FASHION_PROMPT",
    "EMBEDDING_DIM",
]
