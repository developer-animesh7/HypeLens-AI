# Backend Architecture - Clear Separation of Concerns

## Folder Structure Overview

```
backend/
├── preprocess_eng/          # ✅ PREPROCESSING ONLY (Steps 1-5)
│   ├── input_handler.py     # Step 1: Input normalization
│   ├── spell_corrector.py   # Step 2: Spell correction
│   ├── tokenizer.py         # Step 3: Tokenization + Script + Language detection
│   ├── code_mix_detector.py # Step 4: Code-mix detection
│   ├── transliteration.py   # Step 5: Transliteration/Translation
│   ├── transliteration_client.py
│   ├── synonym_mapper.py    # Step 6: Synonym expansion
│   ├── feature_extractor.py # Step 7: Feature extraction
│   ├── pipeline.py          # Orchestrates Steps 1-7
│   ├── config.py            # Configuration loader
│   └── test/                # Unit tests for preprocessing
│
├── search_eng/              # ✅ DATABASE SEARCH (Steps 8-11)
│   ├── embedding_generator.py   # Step 8: Generate embeddings (e5-base-v2)
│   ├── vector_search.py         # Step 9: Pinecone vector search
│   ├── product_resolver.py      # Step 10: PostgreSQL product fetch
│   └── unified_search.py        # Step 11: Unified system (orchestrates 8-10)
│
├── api/                     # ✅ API ROUTES (Frontend interface)
│   └── routes.py            # FastAPI endpoints
│
├── database/                # ✅ DATABASE OPERATIONS
│   ├── db_connection.py     # PostgreSQL connection
│   └── product_db.py        # Product CRUD operations
│
├── scraping/                # ✅ WEB SCRAPING
│   └── product_scraper.py   # Amazon, Flipkart, Myntra scrapers
│
├── ai_scoring/              # ✅ QUALITY SCORING
│   └── quality_scorer.py    # Category-specific quality scoring
│
└── utils/                   # ✅ UTILITIES
    ├── image_processor.py   # Image processing
    └── helpers.py           # Helper functions
```

---

## 🎯 Key Principle: Separation of Concerns

### 1. Preprocessing Engine (`preprocess_eng/`)
**Purpose**: Transform raw user input into clean, structured data

**Responsibilities**:
- ✅ Steps 1-5: Core preprocessing (normalization → tokenization → transliteration)
- ✅ Steps 6-7: Feature extraction and synonym expansion
- ✅ Language detection, spell correction, script detection
- ✅ NO database operations
- ✅ NO embedding generation
- ✅ NO vector search

**Key Files**:
- `pipeline.py` - Orchestrates preprocessing stages
- `tokenizer.py` - Step 3 (Rust tokenization, fastText LID)
- `code_mix_detector.py` - Step 4 (Flipkart Fast Lane)
- `transliteration.py` - Step 5 (IndicXlit Docker service)

---

### 2. Search Engine (`search_eng/`)
**Purpose**: Find products using embeddings and vector search

**Responsibilities**:
- ✅ Step 8: Generate embeddings (intfloat/e5-base-v2)
- ✅ Step 9: Vector search in Pinecone
- ✅ Step 10: Fetch product details from PostgreSQL
- ✅ Step 11: Unified search orchestration
- ✅ Integration with preprocessing pipeline
- ✅ Return products + embeddings to frontend

**Key Files**:
- `unified_search.py` - Main entry point for product search
- `embedding_generator.py` - e5-base-v2 model
- `vector_search.py` - Pinecone client
- `product_resolver.py` - PostgreSQL queries

---

## 🔄 Complete Data Flow

```
Frontend (Next.js)
    ↓
API Routes (/api/find-product)
    ↓
UnifiedSearchSystem (search_eng/unified_search.py)
    ↓
    ├─→ Input Handler (preprocess_eng/)
    │   ├─ Step 1: Normalize input
    │   ├─ Step 2: Spell correction
    │   ├─ Step 3: Tokenization + Language detection
    │   ├─ Step 4: Code-mix detection
    │   ├─ Step 5: Transliteration (if needed)
    │   ├─ Step 6: Synonym expansion
    │   └─ Step 7: Feature extraction
    │
    └─→ Search Pipeline (search_eng/)
        ├─ Step 8: Generate embedding (e5-base-v2)
        ├─ Step 9: Vector search (Pinecone)
        └─ Step 10: Fetch product (PostgreSQL)
    ↓
Response to Frontend (Product + Embedding + Metadata)
```

---

## 📝 Import Guidelines

### ✅ CORRECT Imports

**In `search_eng/` files:**
```python
# Import preprocessing pipeline
from backend.preprocess_eng.pipeline import get_optimized_pipeline
from backend.preprocess_eng.config import get_config

# Import database
from backend.database.product_db import ProductDatabase
```

**In `preprocess_eng/` files:**
```python
# Preprocessing modules can import each other
from .tokenizer import Tokenizer
from .spell_corrector import SpellCorrector
from .transliteration import get_step5_pipeline
```

**In `api/routes.py`:**
```python
# Import unified search (search engine)
from backend.search_eng.unified_search import get_unified_search_system

# Import preprocessing config
from backend.preprocess_eng.config import get_config, validate_config
from backend.preprocess_eng.pipeline import get_optimized_pipeline
```

### ❌ INCORRECT Imports (NEVER DO THIS)

**In `preprocess_eng/` files:**
```python
# ❌ WRONG - Preprocessing should NOT import search
from backend.search_eng.vector_search import VectorSearch

# ❌ WRONG - Preprocessing should NOT import database
from backend.database.product_db import ProductDatabase
```

---

## 🧪 Testing Structure

```
backend/
├── preprocess_eng/test/
│   ├── test_steps1_5_interactive.py    # Tests Steps 1-5 only
│   ├── validate_compliance.py          # Validates preprocessing
│   └── demo_system.py                  # Demo preprocessing
│
└── search_eng/test/
    └── test_unified_search.py          # Tests complete search flow
```

---

## 🚀 Server Startup (app.py)

```python
from backend.preprocess_eng.pipeline import get_optimized_pipeline
from backend.preprocess_eng.config import get_config

# Pre-load ALL models at startup
pipeline = get_optimized_pipeline(config)

# Store in app state for routes
app.state.semantic_pipeline = pipeline
```

---

## 🎯 Summary

| Component | Location | Responsibility |
|-----------|----------|----------------|
| **Steps 1-7** | `preprocess_eng/` | Text preprocessing ONLY |
| **Steps 8-10** | `search_eng/` | Embedding + Vector search + DB fetch |
| **Unified System** | `search_eng/unified_search.py` | Orchestrates entire flow |
| **API Routes** | `api/routes.py` | Frontend interface |
| **Database** | `database/` | PostgreSQL operations |
| **Scraping** | `scraping/` | Web scraping |

---

## ✅ Correct Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                       │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  API Routes (routes.py)                       │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│         UnifiedSearchSystem (search_eng/)                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Preprocessing Pipeline (preprocess_eng/)             │   │
│  │  ├─ Step 1: Input normalization                       │   │
│  │  ├─ Step 2: Spell correction                          │   │
│  │  ├─ Step 3: Tokenization (Rust) + Language detection  │   │
│  │  ├─ Step 4: Code-mix detection                        │   │
│  │  ├─ Step 5: Transliteration (IndicXlit Docker)        │   │
│  │  ├─ Step 6: Synonym expansion                         │   │
│  │  └─ Step 7: Feature extraction                        │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ↓                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Search Pipeline (search_eng/)                        │   │
│  │  ├─ Step 8: Embedding generation (e5-base-v2)         │   │
│  │  ├─ Step 9: Vector search (Pinecone)                  │   │
│  │  └─ Step 10: Product resolution (PostgreSQL)          │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ↓
                  Product + Embedding + Metadata
```

This architecture ensures:
- ✅ Clear separation of preprocessing and search
- ✅ Easy testing (each module independent)
- ✅ Maintainable code (single responsibility)
- ✅ Scalable design (can swap components easily)
