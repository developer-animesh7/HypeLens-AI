"""Visual Search (CLIP + FAISS) module for HypeLens.

This package exposes FastAPI routes and utilities to:
- Build CLIP embeddings and FAISS index from the product database
- Serve image-to-product search over HTTP
- Optionally fall back to web visual search when local results are empty
"""
