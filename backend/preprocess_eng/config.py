"""
Configuration loader for preprocessing engine
Reads from main project .env file
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from main project .env
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'

if env_path.exists():
    load_dotenv(env_path)
else:
    # Try loading from current directory as fallback
    load_dotenv()

# Pinecone Configuration (REQUIRED)
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', 'product-search')
PINECONE_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT', 'us-east-1')

# Embedding Model Configuration
EMBEDDING_MODEL = os.getenv('PREPROCESS_EMBEDDING_MODEL', 'intfloat/e5-base-v2')
EMBEDDING_DIMENSION = int(os.getenv('EMBEDDING_DIMENSION', '768'))

# Pipeline Settings
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

def get_config():
    """Get configuration dictionary"""
    return {
        'pinecone_api_key': PINECONE_API_KEY,
        'pinecone_index_name': PINECONE_INDEX_NAME,
        'pinecone_environment': PINECONE_ENVIRONMENT,
        'embedding_model': EMBEDDING_MODEL,
        'embedding_dimension': EMBEDDING_DIMENSION,
        'log_level': LOG_LEVEL
    }

def validate_config():
    """Validate that required configuration is present"""
    errors = []
    
    if not PINECONE_API_KEY:
        errors.append("PINECONE_API_KEY is required in .env file")
    
    if errors:
        raise ValueError(f"Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
    
    return True
