"""Init file for embedder module"""
from .clip_embedder import CLIPEmbedder, EMBEDDING_DIM
from .preprocess import preprocess_for_clip, crop_image, TARGET_SIZE

__all__ = [
    "CLIPEmbedder",
    "EMBEDDING_DIM",
    "preprocess_for_clip",
    "crop_image",
    "TARGET_SIZE",
]
