"""
GroundingDINO + SAM2 Detector for Fashion Items
Optimized for CPU inference with 2 threads, singleton pattern
"""

import os
import gc
import logging
from typing import List, Dict, Any, Optional
from io import BytesIO
import numpy as np
from PIL import Image
import torch

from .prompts import FASHION_PROMPT, BOX_THRESHOLD, TEXT_THRESHOLD, MAX_DETECTIONS

logger = logging.getLogger(__name__)

# Model paths
MODEL_DIR = os.path.join("models")
DINO_CONFIG = os.path.join(MODEL_DIR, "GroundingDINO_SwinT_OGC.py")
DINO_CHECKPOINT = os.path.join(MODEL_DIR, "groundingdino_swint_ogc.pth")
SAM2_CONFIG = os.path.join(MODEL_DIR, "sam2_hiera_base.yaml")
SAM2_CHECKPOINT = os.path.join(MODEL_DIR, "sam2_hiera_large.pt")

# Global singleton cache
_dino_model = None
_sam2_predictor = None
_model_lock = False


class GroundingDINOSAM2Detector:
    """Singleton detector for fashion items using Grounding DINO + SAM2"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.text_prompt = FASHION_PROMPT
        self.box_threshold = BOX_THRESHOLD
        self.text_threshold = TEXT_THRESHOLD
        self.max_detections = MAX_DETECTIONS
        
        self._initialized = True
        logger.info("✅ GroundingDINOSAM2Detector initialized (models will load on first use)")
    
    def _load_models(self):
        """Lazy load models on first detection"""
        global _dino_model, _sam2_predictor, _model_lock
        
        if _dino_model is not None:
            return
        
        if _model_lock:
            import time
            for _ in range(100):
                time.sleep(0.1)
                if _dino_model is not None:
                    return
            raise RuntimeError("Model loading timeout")
        
        try:
            _model_lock = True
            
            if _dino_model is None:
                logger.info(f"Loading Grounding DINO from {DINO_CHECKPOINT}")
                from groundingdino.util.inference import load_model
                
                _dino_model = load_model(
                    model_config_path=DINO_CONFIG,
                    model_checkpoint_path=DINO_CHECKPOINT,
                    device="cpu"
                )
                
                _dino_model.eval()
                for param in _dino_model.parameters():
                    param.requires_grad = False
                
                logger.info("✅ Grounding DINO loaded successfully")
            
            # SAM2 disabled for now - using bounding boxes only
            if _sam2_predictor is None:
                logger.info("⚠️  SAM2 skipped - using bounding boxes only")
                _sam2_predictor = "DISABLED"
            
            gc.collect()
            
        except Exception as e:
            logger.error(f"Failed to load models: {e}", exc_info=True)
            _dino_model = None
            _sam2_predictor = None
            raise RuntimeError(f"Model loading failed: {str(e)}")
        
        finally:
            _model_lock = False
    
    def detect_objects(
        self,
        image_bytes: bytes,
        confidence_threshold: Optional[float] = None,
        max_detections: Optional[int] = None,
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Detect fashion objects in image
        
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
        # Load models if needed
        self._load_models()
        
        # Parse image
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        image_np = np.array(image)
        
        # Use custom settings or defaults
        box_threshold = confidence_threshold if confidence_threshold is not None else self.box_threshold
        max_dets = max_detections if max_detections is not None else self.max_detections
        prompt = custom_prompt if custom_prompt is not None else self.text_prompt
        
        # Run GroundingDINO
        try:
            from groundingdino.util.inference import predict
            import torchvision.transforms as T
            
            # Convert numpy to tensor (GroundingDINO expects CHW tensor [0,1])
            transform = T.Compose([T.ToTensor()])
            image_tensor = transform(image_np)
            
            boxes, logits, phrases = predict(
                model=_dino_model,
                image=image_tensor,
                caption=prompt,
                box_threshold=box_threshold,
                text_threshold=self.text_threshold,
                device="cpu"  # Force CPU inference
            )
            
            # Convert boxes from normalized [0,1] to pixel coordinates
            h, w = image_np.shape[:2]
            boxes_np = boxes.cpu().numpy()
            boxes_scaled = boxes_np * np.array([w, h, w, h])
            
            # Format detections
            detections = []
            for i, (box, logit, phrase) in enumerate(zip(boxes_scaled, logits, phrases)):
                if i >= max_dets:
                    break
                
                x1, y1, x2, y2 = box
                detections.append({
                    "bbox": [float(x1), float(y1), float(x2), float(y2)],
                    "label": phrase.strip(),
                    "confidence": float(logit),
                    "class_id": i
                })
            
            logger.info(f"Grounding DINO detected {len(detections)} objects")
            
            return {
                "detections": detections,
                "image_size": [w, h]
            }
            
        except Exception as e:
            logger.error(f"Detection failed: {e}", exc_info=True)
            raise RuntimeError(f"Detection failed: {str(e)}")
