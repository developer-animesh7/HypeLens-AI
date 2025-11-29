"""
CLIP embedding generator using OpenCLIP
ViT-L/14 model with laion2b weights (768-dim embeddings)
"""

import torch
import open_clip
from PIL import Image
import numpy as np
from typing import Union, List
import logging

from .preprocess import preprocess_for_clip

logger = logging.getLogger(__name__)

# CLIP Model Configuration
CLIP_MODEL = "ViT-L-14"
CLIP_PRETRAINED = "laion2b_s32b_b82k"
EMBEDDING_DIM = 768

# Global singleton cache
_clip_model = None
_clip_preprocess = None
_clip_tokenizer = None
_model_lock = False


class CLIPEmbedder:
    """Singleton CLIP embedder for generating 768-dim embeddings"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        logger.info("✅ CLIPEmbedder initialized (model will load on first use)")
    
    def _load_model(self):
        """Lazy load CLIP model on first embedding generation"""
        global _clip_model, _clip_preprocess, _clip_tokenizer, _model_lock
        
        if _clip_model is not None:
            return
        
        if _model_lock:
            import time
            for _ in range(100):
                time.sleep(0.1)
                if _clip_model is not None:
                    return
            raise RuntimeError("CLIP model loading timeout")
        
        try:
            _model_lock = True
            
            if _clip_model is None:
                logger.info(f"Loading CLIP model: {CLIP_MODEL} with {CLIP_PRETRAINED}")
                
                model, _, preprocess = open_clip.create_model_and_transforms(
                    CLIP_MODEL,
                    pretrained=CLIP_PRETRAINED,
                    device="cpu"
                )
                
                model.eval()
                for param in model.parameters():
                    param.requires_grad = False
                
                tokenizer = open_clip.get_tokenizer(CLIP_MODEL)
                
                _clip_model = model
                _clip_preprocess = preprocess
                _clip_tokenizer = tokenizer
                
                logger.info(f"✅ CLIP model loaded successfully ({EMBEDDING_DIM}-dim embeddings)")
        
        except Exception as e:
            logger.error(f"Failed to load CLIP model: {e}", exc_info=True)
            _clip_model = None
            _clip_preprocess = None
            _clip_tokenizer = None
            raise RuntimeError(f"CLIP model loading failed: {str(e)}")
        
        finally:
            _model_lock = False
    
    def get_embedding(self, image: Union[Image.Image, bytes]) -> np.ndarray:
        """
        Generate CLIP embedding for image
        
        Args:
            image: PIL Image or image bytes
        
        Returns:
            numpy array of shape (768,) with L2-normalized embedding
        """
        # Load model if needed
        self._load_model()
        
        # Parse image if bytes
        if isinstance(image, bytes):
            from io import BytesIO
            image = Image.open(BytesIO(image)).convert("RGB")
        
        # Preprocess image (224x224, square pad)
        processed_image, metadata = preprocess_for_clip(image)
        
        # Apply CLIP preprocessing (normalization, tensor conversion)
        image_tensor = _clip_preprocess(processed_image).unsqueeze(0)
        
        # Generate embedding
        with torch.no_grad():
            embedding = _clip_model.encode_image(image_tensor)
            
            # L2 normalize
            embedding = embedding / embedding.norm(dim=-1, keepdim=True)
            
            # Convert to numpy
            embedding_np = embedding.cpu().numpy().squeeze()
        
        logger.debug(f"Generated embedding: shape={embedding_np.shape}, norm={np.linalg.norm(embedding_np):.4f}")
        
        return embedding_np
    
    def get_text_embedding(self, text: str) -> np.ndarray:
        """
        Generate CLIP embedding for text
        
        Args:
            text: Text string
        
        Returns:
            numpy array of shape (768,) with L2-normalized embedding
        """
        # Load model if needed
        self._load_model()
        
        # Tokenize text
        text_tokens = _clip_tokenizer([text])
        
        # Generate embedding
        with torch.no_grad():
            embedding = _clip_model.encode_text(text_tokens)
            
            # L2 normalize
            embedding = embedding / embedding.norm(dim=-1, keepdim=True)
            
            # Convert to numpy
            embedding_np = embedding.cpu().numpy().squeeze()
        
        logger.debug(f"Generated text embedding: shape={embedding_np.shape}, norm={np.linalg.norm(embedding_np):.4f}")
        
        return embedding_np
