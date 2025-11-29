"""Init file for detector module"""
from .grounding_dino_sam2_detector import GroundingDINOSAM2Detector
from .prompts import FASHION_PROMPT, BOX_THRESHOLD, TEXT_THRESHOLD, MAX_DETECTIONS

__all__ = [
    "GroundingDINOSAM2Detector",
    "FASHION_PROMPT",
    "BOX_THRESHOLD",
    "TEXT_THRESHOLD",
    "MAX_DETECTIONS",
]
