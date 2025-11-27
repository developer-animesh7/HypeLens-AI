"""
Complete Pipeline Test
Test: Detect → Crop → Preprocess → CLIP Embed
"""

import torch

# CPU Optimization - MUST be first
torch.set_num_threads(2)
torch.set_num_interop_threads(1)

import sys
import os

# Add ai_visual_search to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "ai_visual_search"))

from detector import GroundingDINOSAM2Detector
from embedder import CLIPEmbedder, crop_image, preprocess_for_clip
from utils import bytes_to_pil, setup_logger
from PIL import Image
import io

logger = setup_logger("test")


def test_complete_pipeline(image_path: str = None):
    """Test complete pipeline with real or sample image"""
    
    logger.info("=" * 60)
    logger.info("TESTING COMPLETE PIPELINE")
    logger.info("=" * 60)
    
    # Step 1: Load test image
    if image_path and os.path.exists(image_path):
        logger.info(f"📷 Loading image: {image_path}")
        with open(image_path, "rb") as f:
            image_bytes = f.read()
    else:
        logger.info("📷 Creating synthetic test image (800x600 RGB)")
        img = Image.new("RGB", (800, 600), color=(200, 150, 100))
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()
    
    # Step 2: Object Detection
    logger.info("\n🎯 STEP 1: Object Detection with GroundingDINO")
    logger.info("-" * 60)
    
    try:
        detector = GroundingDINOSAM2Detector()
        result = detector.detect_objects(
            image_bytes=image_bytes,
            confidence_threshold=0.18,
            max_detections=25
        )
        
        logger.info(f"✅ Detected {len(result['detections'])} objects")
        for i, det in enumerate(result['detections'][:5], 1):
            logger.info(f"   {i}. {det['label']}: {det['confidence']:.2f} | bbox={det['bbox']}")
        
        if len(result['detections']) > 5:
            logger.info(f"   ... and {len(result['detections']) - 5} more")
    
    except Exception as e:
        logger.error(f"❌ Detection failed: {e}")
        return False
    
    # Step 3: Crop first detection
    if result['detections']:
        logger.info("\n✂️  STEP 2: Crop first detected object")
        logger.info("-" * 60)
        
        try:
            image = bytes_to_pil(image_bytes)
            first_det = result['detections'][0]
            bbox = first_det['bbox']
            
            cropped = crop_image(image, bbox)
            logger.info(f"✅ Cropped: {bbox} → {cropped.size}")
        
        except Exception as e:
            logger.error(f"❌ Crop failed: {e}")
            cropped = bytes_to_pil(image_bytes)
    
    else:
        logger.info("\n⚠️  STEP 2: No objects detected, using full image")
        cropped = bytes_to_pil(image_bytes)
    
    # Step 4: Preprocess for CLIP
    logger.info("\n🔧 STEP 3: Preprocess for CLIP (224x224, square pad)")
    logger.info("-" * 60)
    
    try:
        processed, metadata = preprocess_for_clip(cropped)
        logger.info(f"✅ Preprocessed: {cropped.size} → {processed.size}")
        logger.info(f"   Original: {metadata['original_size']}")
        logger.info(f"   Padded: {metadata.get('padded_size', 'N/A')}")
        logger.info(f"   Final: {metadata['final_size']}")
    
    except Exception as e:
        logger.error(f"❌ Preprocessing failed: {e}")
        return False
    
    # Step 5: Generate CLIP embedding
    logger.info("\n🧠 STEP 4: Generate CLIP Embedding (768-dim)")
    logger.info("-" * 60)
    
    try:
        embedder = CLIPEmbedder()
        embedding = embedder.get_embedding(processed)
        
        logger.info(f"✅ Embedding generated: shape={embedding.shape}, dtype={embedding.dtype}")
        logger.info(f"   L2 norm: {(embedding ** 2).sum() ** 0.5:.4f}")
        logger.info(f"   Min/Max: {embedding.min():.4f} / {embedding.max():.4f}")
        logger.info(f"   First 5 values: {embedding[:5]}")
    
    except Exception as e:
        logger.error(f"❌ Embedding failed: {e}")
        return False
    
    # Success
    logger.info("\n" + "=" * 60)
    logger.info("✅ PIPELINE TEST COMPLETE - ALL STEPS PASSED")
    logger.info("=" * 60)
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test complete AI visual search pipeline")
    parser.add_argument("--image", help="Path to test image", default=None)
    args = parser.parse_args()
    
    success = test_complete_pipeline(args.image)
    
    sys.exit(0 if success else 1)
