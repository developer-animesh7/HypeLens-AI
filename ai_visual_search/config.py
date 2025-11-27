"""
Configuration for AI Visual Search
"""

import os
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
MODEL_DIR = PROJECT_ROOT / "models"

# CPU Optimization
TORCH_THREADS = 2
TORCH_INTEROP_THREADS = 1

# GroundingDINO Settings
DINO_CONFIG_FILE = MODEL_DIR / "GroundingDINO_SwinT_OGC.py"
DINO_CHECKPOINT_FILE = MODEL_DIR / "groundingdino_swint_ogc.pth"
DINO_BOX_THRESHOLD = float(os.getenv("DINO_BOX_THRESHOLD", "0.18"))
DINO_TEXT_THRESHOLD = float(os.getenv("DINO_TEXT_THRESHOLD", "0.18"))
DINO_MAX_DETECTIONS = int(os.getenv("DINO_MAX_DETECTIONS", "25"))

# SAM2 Settings (disabled for now)
SAM2_CONFIG_FILE = MODEL_DIR / "sam2_hiera_base.yaml"
SAM2_CHECKPOINT_FILE = MODEL_DIR / "sam2_hiera_large.pt"
SAM2_ENABLED = False

# CLIP Settings
CLIP_MODEL_NAME = "ViT-L-14"
CLIP_PRETRAINED = "laion2b_s32b_b82k"
CLIP_EMBEDDING_DIM = 768

# Preprocessing
IMAGE_TARGET_SIZE = (224, 224)
IMAGE_MIN_SIZE = 50
IMAGE_MAX_SIZE = 2000

# API Settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "5000"))
API_RELOAD = os.getenv("API_RELOAD", "false").lower() == "true"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
