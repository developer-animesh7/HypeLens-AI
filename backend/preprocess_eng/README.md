# Multilingual Semantic Search Pipeline

## Overview

An intelligent query understanding and product resolution module optimized for Indian e-commerce. This pipeline processes multilingual user queries and finds relevant products using semantic search.

## Architecture

```
User Input (text/URL/shortened link)
    ↓
Input Handler (expand shortlinks, parse URL)
    ↓
Language Detection (langdetect)
    ↓
Translation to English (deep_translator)
    ↓
Text Normalization (regex: lowercase, currency, remove HTML)
    ↓
Tokenization & Lemmatization (spaCy)
    ↓
Spell Correction (SymSpell)
    ↓
Synonym Mapping (WordNet + custom ecom dict)
    ↓
Feature & Price Extraction (regex + spaCy NER)
    ↓
Embedding Generation (intfloat/e5-base-v2)
    ↓
Vector Search (Pinecone)
    ↓
Product Resolve (PostgreSQL lookup by product_id)
    ↓
JSON Output (to Recommendation System)
```

## Components

### 1. **Input Handler** (`input_handler.py`)
- Expands shortened URLs (bit.ly, tinyurl, etc.)
- Parses e-commerce URLs to extract platform and product IDs
- Supports: Amazon, Flipkart, Myntra, Snapdeal, etc.

### 2. **Language Detector** (`language_detector.py`)
- Detects query language using langdetect
- Supports 10+ Indian languages (Hindi, Bengali, Tamil, Telugu, etc.)
- Falls back to character-based detection if langdetect unavailable

### 3. **Translator** (`translator.py`)
- Translates non-English queries to English using Google Translate API
- Preserves technical terms and product names
- Batch translation support

### 4. **Text Normalizer** (`text_normalizer.py`)
- Converts to lowercase
- Normalizes Indian currency (₹1,500 → 1500 rupees, 2.5 lakh → 250000 rupees)
- Removes HTML tags and special characters
- Cleans punctuation

### 5. **Tokenizer** (`tokenizer.py`)
- spaCy-based tokenization and lemmatization
- POS (Part-of-Speech) tagging
- Noun phrase extraction for product names
- Stopword removal (optional)

### 6. **Spell Corrector** (`spell_corrector.py`)
- SymSpell algorithm for fast spell correction
- Custom dictionary with Indian brands and tech terms
- Compound word correction

### 7. **Synonym Mapper** (`synonym_mapper.py`)
- WordNet-based synonym expansion
- Custom e-commerce synonym dictionary
- Indian slang and common misspellings
- Query expansion for better matching

### 8. **Feature Extractor** (`feature_extractor.py`)
- Extracts product specifications:
  - Storage (GB, TB)
  - RAM (GB)
  - Screen size (inches)
  - Camera (MP)
  - Battery (mAh)
  - Processor (Snapdragon, MediaTek, etc.)
  - Price (₹)
  - Colors, Brands
- spaCy NER for named entity recognition

### 9. **Embedding Generator** (`embedding_generator.py`)
- Uses `intfloat/e5-base-v2` model (768 dimensions)
- Alternative: `all-MiniLM-L6-v2` (384 dimensions, faster)
- Batch processing support
- Cosine similarity calculation

### 10. **Vector Search** (`vector_search.py`)
- Pinecone integration for fast similarity search
- Falls back to PostgreSQL if Pinecone unavailable
- Metadata filtering support
- Upsert and delete operations

### 11. **Product Resolver** (`product_resolver.py`)
- Resolves product IDs to full details from PostgreSQL
- Batch resolution support
- Fallback search by name/category
- PostgreSQL vector similarity search

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Download spaCy model:**
```bash
python -m spacy download en_core_web_sm
```

3. **Download NLTK data** (optional, for WordNet):
```python
import nltk
nltk.download('wordnet')
nltk.download('omw-1.4')
```

## Usage

### Basic Usage

```python
from backend.preprocess_eng import SemanticSearchPipeline

# Initialize pipeline
pipeline = SemanticSearchPipeline(config={
    'model_name': 'e5-base-v2',  # or 'all-minilm'
    'pinecone_api_key': 'your-api-key',  # optional
    'pinecone_env': 'us-east-1',
    'device': 'cpu'  # or 'cuda'
})

# Process a query
results = pipeline.process(
    user_input="सबसे अच्छा smartphone under 20000",  # Hindi query
    top_k=10,
    include_metadata=True
)

# Access results
for product in results['results']:
    print(f"{product['name']} - ₹{product['price']}")
    print(f"Similarity: {product['similarity']:.2f}")

# View pipeline metadata
print(results['metadata'])
```

### Extract Features Only

```python
features = pipeline.extract_features_only(
    "Samsung Galaxy S21 128GB 8GB RAM 64MP Camera 4000mAh"
)
print(features)
# Output: {'storage': '128GB', 'ram': '8GB', 'camera_mp': ['64MP'], ...}
```

### Generate Embedding Only

```python
embedding = pipeline.generate_embedding_only(
    text="wireless bluetooth headphones",
    preprocess=True
)
print(len(embedding))  # 768 or 384 dimensions
```

### URL Processing

```python
# Shortened URL
results = pipeline.process("https://bit.ly/xyz123")

# Full product URL
results = pipeline.process("https://www.amazon.in/dp/B09XYZ/...")

# Text query
results = pipeline.process("best laptop under 50000")
```

## Configuration

```python
config = {
    # Embedding model
    'model_name': 'e5-base-v2',  # or 'all-minilm', 'mpnet-base'
    'device': 'cpu',  # or 'cuda' for GPU
    
    # Pinecone (optional)
    'pinecone_api_key': 'your-key',
    'pinecone_env': 'us-east-1',
    'index_name': 'products',
    
    # Spell correction
    'max_edit_distance': 2,
    
    # Synonym expansion
    'max_synonyms': 3,
}

pipeline = SemanticSearchPipeline(config=config)
```

## Supported Languages

- English
- Hindi (हिंदी)
- Bengali (বাংলা)
- Telugu (తెలుగు)
- Marathi (मराठी)
- Tamil (தமிழ்)
- Gujarati (ગુજરાતી)
- Kannada (ಕನ್ನಡ)
- Malayalam (മലയാളം)
- Punjabi (ਪੰਜਾਬੀ)
- Urdu (اردو)

## Performance

- **Processing Time**: ~200-500ms per query (CPU)
- **Embedding Dimension**: 768 (e5-base-v2) or 384 (all-minilm)
- **Batch Processing**: Supported for embeddings and translations
- **Vector Search**: < 100ms with Pinecone index

## Integration with FastAPI

```python
from fastapi import APIRouter
from backend.preprocess_eng import SemanticSearchPipeline

router = APIRouter()
pipeline = SemanticSearchPipeline()

@router.post("/search")
async def semantic_search(query: str, top_k: int = 10):
    results = pipeline.process(query, top_k=top_k)
    return {
        "success": results['success'],
        "products": results['results'],
        "metadata": results['metadata']
    }
```

## Monitoring & Logging

The pipeline logs all stages to help with debugging and monitoring:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('backend.preprocess_eng')

# Each stage logs:
# - Input/output
# - Processing time
# - Errors and warnings
```

## Extending the Pipeline

### Add Custom Synonyms

```python
pipeline.synonym_mapper.add_custom_synonyms(
    word='amoled',
    synonyms=['super amoled', 'dynamic amoled', 'oled']
)
```

### Add Custom Spell Corrections

```python
# Edit spell_corrector.py and add to _add_custom_words()
custom_words = ['oneplus', 'realme', 'poco', ...]
```

### Use Different Embedding Model

```python
pipeline = SemanticSearchPipeline(config={
    'model_name': 'all-minilm'  # Faster, smaller
    # or 'mpnet-base'  # Better quality
})
```

## Error Handling

The pipeline is designed to gracefully degrade:
- If a component fails, it logs a warning and continues
- Missing dependencies trigger fallback mechanisms
- All errors are captured in the response metadata

```python
results = pipeline.process(query)
if not results['success']:
    print(f"Error: {results.get('error')}")
    print(f"Metadata: {results['metadata']}")
```

## Testing

```python
# Test individual components
from backend.preprocess_eng.language_detector import LanguageDetector

detector = LanguageDetector()
lang, conf = detector.detect("सबसे अच्छा फोन")
print(f"Language: {lang}, Confidence: {conf}")
```

## Contributing

When adding new features:
1. Update the component's docstring
2. Add logging for debugging
3. Handle errors gracefully
4. Update this README
5. Add unit tests

## License

Copyright © 2025 AI Shopping Helper
