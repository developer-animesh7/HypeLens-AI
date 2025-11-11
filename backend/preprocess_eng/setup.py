#!/usr/bin/env python3
"""
Setup script for the Semantic Search Pipeline
Downloads required models and data
"""

import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def install_spacy_model():
    """Download spaCy English model"""
    logger.info("📥 Downloading spaCy model (en_core_web_sm)...")
    try:
        subprocess.run([
            sys.executable, "-m", "spacy", "download", "en_core_web_sm"
        ], check=True)
        logger.info("✅ spaCy model installed")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to download spaCy model: {e}")


def download_nltk_data():
    """Download NLTK WordNet data"""
    logger.info("📥 Downloading NLTK data (WordNet)...")
    try:
        import nltk
        nltk.download('wordnet', quiet=True)
        nltk.download('omw-1.4', quiet=True)  # Open Multilingual WordNet
        logger.info("✅ NLTK data downloaded")
    except Exception as e:
        logger.error(f"❌ Failed to download NLTK data: {e}")


def test_imports():
    """Test if all required packages can be imported"""
    logger.info("🔍 Testing imports...")
    
    packages = [
        'langdetect',
        'deep_translator',
        'spacy',
        'nltk',
        'symspellpy',
        'sentence_transformers'
    ]
    
    failed = []
    for package in packages:
        try:
            __import__(package)
            logger.info(f"  ✅ {package}")
        except ImportError:
            logger.warning(f"  ❌ {package} not installed")
            failed.append(package)
    
    if failed:
        logger.warning(f"\n⚠️  Missing packages: {', '.join(failed)}")
        logger.info("Install with: pip install -r requirements.txt")
    else:
        logger.info("\n✅ All packages installed!")


def main():
    """Run setup"""
    print("\n" + "="*60)
    print("SEMANTIC SEARCH PIPELINE - Setup")
    print("="*60 + "\n")
    
    # Test imports first
    test_imports()
    
    print()
    
    # Download spaCy model
    install_spacy_model()
    
    print()
    
    # Download NLTK data
    download_nltk_data()
    
    print("\n" + "="*60)
    print("✅ Setup complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Configure Pinecone API key (optional)")
    print("2. Run example: python backend/preprocess_eng/example_usage.py")
    print("3. Integrate with your FastAPI app")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
