"""
Hybrid Search Module: CLIP Image-to-Text + Keyword Search
==========================================================
Combines visual similarity (CLIP) with text-based keyword matching (FAISS).
Stores results in PostgreSQL and returns unified JSON.
"""
import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
from io import BytesIO
from PIL import Image
import torch
import open_clip
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.database.db_connection import DatabaseConnection
from backend.ai.exact_match_scorer import ExactMatchScorer
from backend.ai.category_normalizer import get_normalizer


class HybridSearchEngine:
    """
    Hybrid search combining:
    1. CLIP image-to-text embeddings (visual + semantic similarity)
    2. Keyword-based TF-IDF search (text matching)
    """
    
    def __init__(self):
        """Initialize CLIP model and database connection."""
        # UPGRADED: ViT-L/14 for maximum accuracy
        # ViT-L/14: 304M parameters, 768-dim embeddings
        # Provides ~30% better accuracy than ViT-B/32 for product matching
        self.device = torch.device("cpu")
        self.model_name = "ViT-L-14"
        self.pretrained = "openai"
        
        # Load CLIP model and preprocessing
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            self.model_name, 
            pretrained=self.pretrained, 
            device=self.device
        )
        self.model.eval()
        
        # Tokenizer for text encoding
        self.tokenizer = open_clip.get_tokenizer(self.model_name)
        
        # Database connection
        self.db = DatabaseConnection()
        
        # TF-IDF for keyword search (initialized when products are loaded)
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        
        # PHASE 2 OPTIMIZATION: Cache product text embeddings to avoid recomputation
        self._cached_embeddings = None
        self._cached_product_ids = None
        self._cached_products = None
        
    def preload_products_and_embeddings(self):
        """
        Preload products and generate embeddings at startup.
        This eliminates the 10-12 second delay on first search.
        """
        print("  → Preloading products...")
        products = self.load_products_from_db()
        
        if not products:
            print("  ⚠️ No products with embeddings found")
            return
        
        print(f"  → Loaded {len(products)} products")
        print(f"  → Generating text embeddings (one-time process)...")
        
        # Generate text embeddings for all products
        descriptions = [p['description'] for p in products]
        text_embeddings = self.encode_text(descriptions)
        
        # Cache everything
        product_ids = [p.get('global_product_id', str(i)) for i, p in enumerate(products)]
        self._cached_embeddings = text_embeddings
        self._cached_product_ids = product_ids
        self._cached_products = products
        
        # Build TF-IDF index
        print(f"  → Building keyword search index...")
        self.build_keyword_index(products)
        
        print(f"  ✅ Preloading complete! Search will be instant.")
        
    def encode_image(self, image_bytes: bytes) -> np.ndarray:
        """
        Generate CLIP embedding for an uploaded image.
        
        Args:
            image_bytes: Raw image file bytes
            
        Returns:
            Normalized embedding vector (numpy array)
        """
        # Open and preprocess image
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
        
        # Generate embedding
        with torch.no_grad():
            image_features = self.model.encode_image(image_tensor)
            # Normalize for cosine similarity
            normalized = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
        
        return normalized.cpu().numpy().astype("float32")[0]
    
    def encode_text(self, texts: List[str]) -> np.ndarray:
        """
        Generate CLIP embeddings for text descriptions.
        
        Args:
            texts: List of product descriptions
            
        Returns:
            Normalized embedding matrix (numpy array)
        """
        # Tokenize texts
        text_tokens = self.tokenizer(texts).to(self.device)
        
        # Generate embeddings
        with torch.no_grad():
            text_features = self.model.encode_text(text_tokens)
            # Normalize for cosine similarity
            normalized = text_features / text_features.norm(p=2, dim=-1, keepdim=True)
        
        return normalized.cpu().numpy().astype("float32")
    
    def build_keyword_index(self, products: List[Dict[str, Any]]) -> None:
        """
        Build TF-IDF index for keyword-based search.
        
        PHASE 2 OPTIMIZATION: Caches TF-IDF to avoid rebuilding
        
        Args:
            products: List of product dictionaries with 'description' field
        """
        # Check if we already have a valid index for these products
        product_ids = [p.get('global_product_id', str(i)) for i, p in enumerate(products)]
        
        if (self.tfidf_vectorizer is not None and 
            self.tfidf_matrix is not None and
            self._cached_product_ids == product_ids):
            # Index already built for these products - skip!
            return
        
        # Combine name and description for richer keyword matching
        texts = [
            f"{p.get('product_name', '')} {p.get('description', '')} {p.get('brand', '')}"
            for p in products
        ]
        
        # Build TF-IDF matrix
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),  # unigrams and bigrams
            stop_words='english'
        )
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
    
    def keyword_search(self, query_text: str, top_k: int = 20) -> List[Dict[str, Any]]:
        """
        Perform keyword-based search using TF-IDF.
        
        Args:
            query_text: Search query (e.g., "red cotton shirt")
            top_k: Number of results to return
            
        Returns:
            List of results with keyword_score
        """
        if self.tfidf_vectorizer is None:
            return []
        
        # Vectorize query
        query_vec = self.tfidf_vectorizer.transform([query_text])
        
        # Compute cosine similarity
        scores = cosine_similarity(query_vec, self.tfidf_matrix)[0]
        
        # Get top k indices
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only include non-zero matches
                results.append({
                    'index': int(idx),
                    'keyword_score': float(scores[idx])
                })
        
        return results
    
    def load_products_from_db(self) -> List[Dict[str, Any]]:
        """
        Load products from HypeLens PostgreSQL schema.
        
        PHASE 2 UPDATE: Uses new products_global table
        OPTIMIZATION: Only load products with embeddings (searchable products)
        
        Returns:
            List of product dictionaries with global_product_id
        """
        query = """
        SELECT 
            global_product_id,
            name as product_name,
            description,
            brand,
            category,
            image_url,
            specifications
        FROM public.products_global
        WHERE description IS NOT NULL 
          AND TRIM(description) <> ''
          AND embedding_vector IS NOT NULL
        ORDER BY created_at DESC
        """
        
        rows = self.db.execute_query(query)
        
        products = []
        for row in rows:
            products.append({
                'global_product_id': str(row['global_product_id']),
                'product_name': row['product_name'],
                'description': row['description'] or '',
                'brand': row['brand'] or 'Unknown',
                'category': row['category'] or 'General',
                'image_url': row['image_url'],
                'specifications': row.get('specifications', {})
            })
        
        return products
    
    def get_product_listings(self, global_product_id: str) -> List[Dict[str, Any]]:
        """
        Get all store listings for a product (multi-store pricing).
        
        PHASE 2 NEW METHOD: Fetches prices from all stores
        
        Args:
            global_product_id: UUID of the product
            
        Returns:
            List of store listings with prices and affiliate URLs
        """
        query = """
        SELECT 
            listing_id,
            store_name,
            price,
            original_price,
            in_stock,
            product_url,
            seller_name,
            last_scraped_at
        FROM public.listings_scraped
        WHERE global_product_id = :product_id
          AND in_stock = TRUE
        ORDER BY price ASC
        """
        
        rows = self.db.execute_query(query, {'product_id': global_product_id})
        
        listings = []
        for row in rows:
            listings.append({
                'listing_id': row['listing_id'],
                'store_name': row['store_name'],
                'price': float(row['price']) if row['price'] else 0.0,
                'original_price': float(row['original_price']) if row.get('original_price') else None,
                'in_stock': row['in_stock'],
                'product_url': row['product_url'],
                'seller_name': row.get('seller_name'),
                'last_updated': str(row.get('last_scraped_at', ''))
            })
        
        return listings
    
    def load_products_from_json(self, json_path: str) -> List[Dict[str, Any]]:
        """
        Load products from JSON file (fallback/testing).
        
        Args:
            json_path: Path to products.json
            
        Returns:
            List of product dictionaries
        """
        if not os.path.exists(json_path):
            return []
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data.get('products', [])
    
    def clip_search(
        self, 
        image_bytes: bytes, 
        products: List[Dict[str, Any]], 
        top_k: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Perform CLIP-based image-to-text search.
        
        PHASE 2 OPTIMIZATION: Caches product embeddings to avoid recomputing every search
        
        Args:
            image_bytes: Uploaded image bytes
            products: List of product dictionaries
            top_k: Number of results to return
            
        Returns:
            List of results with clip_score
        """
        # Generate image embedding
        image_embedding = self.encode_image(image_bytes)
        
        # PHASE 2: Check if we can reuse cached embeddings
        product_ids = [p.get('global_product_id', str(i)) for i, p in enumerate(products)]
        cache_valid = (
            self._cached_embeddings is not None and
            self._cached_product_ids == product_ids
        )
        
        if cache_valid:
            # Reuse cached embeddings (FAST!)
            text_embeddings = self._cached_embeddings
        else:
            # Generate text embeddings for all products (SLOW - first time only)
            descriptions = [p['description'] for p in products]
            text_embeddings = self.encode_text(descriptions)
            # Cache for next search
            self._cached_embeddings = text_embeddings
            self._cached_product_ids = product_ids
            self._cached_products = products
        
        # Compute cosine similarity (dot product since embeddings are normalized)
        similarities = np.dot(text_embeddings, image_embedding)
        
        # PHASE 2: Optimized top-k selection using argpartition (faster than full sort)
        if len(similarities) > top_k:
            # Use argpartition for O(n) instead of O(n log n)
            top_indices = np.argpartition(similarities, -top_k)[-top_k:]
            # Sort only the top-k elements
            top_indices = top_indices[np.argsort(similarities[top_indices])[::-1]]
        else:
            # If we have fewer products than top_k, just sort all
            top_indices = np.argsort(similarities)[::-1]
        
        results = []
        for idx in top_indices:
            results.append({
                'index': int(idx),
                'clip_score': float(similarities[idx])
            })
        
        return results
    
    def hybrid_search(
        self,
        image_bytes: bytes,
        query_text: Optional[str] = None,
        top_k: int = 10,
        clip_weight: float = 0.75,  # INCREASED: 75% visual matching
        keyword_weight: float = 0.25,  # DECREASED: 25% text matching
        products_source: str = "db"  # "db" or "json"
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining CLIP and keyword search.
        
        PHASE 2 OPTIMIZATION: Caches products to avoid DB queries
        
        Args:
            image_bytes: Uploaded image bytes
            query_text: Optional text query for keyword search
            top_k: Number of final results
            clip_weight: Weight for CLIP score (default 0.75 for better visual matching)
            keyword_weight: Weight for keyword score (default 0.25)
            products_source: "db" to load from PostgreSQL, "json" for products.json
            
        Returns:
            Unified ranked results sorted by normalized_score and price
        """
        import time
        search_start = time.time()
        
        # PHASE 2: Load products with caching
        if self._cached_products is not None and products_source == "db":
            # Reuse cached products (FAST!)
            products = self._cached_products  # FIX: Assign cached products to variable
            print(f"[TIMING] Using cached products ({len(products)} items) - 0.0s")
        else:
            # Load from source
            load_start = time.time()
            if products_source == "db":
                products = self.load_products_from_db()
            else:
                products = self.load_products_from_json("data/products.json")
            
            if not products:
                return []
            
            # Cache for next search
            if products_source == "db":
                self._cached_products = products
            
            load_time = time.time() - load_start
            print(f"[TIMING] Loaded {len(products)} products from DB - {load_time:.2f}s")
        
        # Build keyword index (will skip if already cached)
        index_start = time.time()
        self.build_keyword_index(products)
        index_time = time.time() - index_start
        if index_time > 0.1:
            print(f"[TIMING] Built TF-IDF index - {index_time:.2f}s")
        else:
            print(f"[TIMING] Using cached TF-IDF index - 0.0s")
        
        # Perform CLIP search
        clip_start = time.time()
        clip_results = self.clip_search(image_bytes, products, top_k=min(50, len(products)))
        clip_time = time.time() - clip_start
        print(f"[TIMING] CLIP search - {clip_time:.2f}s")
        
        # Create score dictionary
        scores = {}
        for res in clip_results:
            idx = res['index']
            scores[idx] = {
                'clip_score': res['clip_score'],
                'keyword_score': 0.0
            }
        
        # Perform keyword search if query provided
        if query_text and query_text.strip():
            keyword_start = time.time()
            keyword_results = self.keyword_search(query_text, top_k=min(50, len(products)))
            keyword_time = time.time() - keyword_start
            print(f"[TIMING] Keyword search - {keyword_time:.2f}s")
            
            for res in keyword_results:
                idx = res['index']
                if idx in scores:
                    scores[idx]['keyword_score'] = res['keyword_score']
                else:
                    scores[idx] = {
                        'clip_score': 0.0,
                        'keyword_score': res['keyword_score']
                    }
        
        # Compute normalized scores and build results
        scoring_start = time.time()
        final_results = []
        for idx, score_dict in scores.items():
            normalized_score = (
                clip_weight * score_dict['clip_score'] + 
                keyword_weight * score_dict['keyword_score']
            )
            
            product = products[idx]
            
            # PHASE 2 UPDATE: Use new schema fields
            result_item = {
                'global_product_id': product.get('global_product_id'),  # NEW: UUID
                'name': product['product_name'],
                'platform': product['brand'],  # Keep for backward compatibility
                'brand': product['brand'],  # NEW: Explicit brand field
                'category': product.get('category', 'General'),
                'similarity_score': round(normalized_score, 4),
                'clip_score': round(score_dict['clip_score'], 4),
                'keyword_score': round(score_dict['keyword_score'], 4),
                'image_url': product['image_url'],
                'specifications': product.get('specifications', {})
            }
            
            final_results.append(result_item)
        
        # Sort by similarity_score (desc)
        final_results.sort(key=lambda x: -x['similarity_score'])
        
        # ===================================================================
        # IMPROVED CATEGORY DETECTION & FILTERING
        # ===================================================================
        normalizer = get_normalizer()
        
        # STEP 1: Normalize all product categories to standard format
        for result in final_results:
            raw_category = result.get('category', '')
            result['category'] = normalizer.normalize(raw_category)  # Smartphones, Laptops, etc.
            result['_raw_category'] = raw_category  # Keep original for debugging
        
        print(f"\n[DEBUG] Top 15 results BEFORE category filtering:")
        for idx, r in enumerate(final_results[:15], 1):
            print(f"  {idx:2d}. {r['category']:15s} ({r['similarity_score']:.3f}) - {r['name'][:50]}")
        
        # STEP 2: DETECT QUERY CATEGORY (3 methods with priority)
        query_category = None
        
        # Method 1: Extract from query text (HIGHEST PRIORITY)
        if query_text and query_text.strip():
            query_category = normalizer.detect_from_text(query_text)
            if query_category:
                print(f"[CATEGORY] Detected from query text: {query_category}")
        
        # Method 2: Consensus from top CLIP visual matches (FALLBACK)
        # IMPORTANT: Use more results for better consensus (top 10-15 instead of top 5)
        if not query_category and len(final_results) >= 3:
            query_category = normalizer.detect_from_results(final_results[:15], consensus_threshold=3)
            if query_category:
                print(f"[CATEGORY] Detected from visual consensus (top 15): {query_category}")
        
        # Method 3: Use top visual match (LAST RESORT)
        if not query_category and final_results:
            query_category = final_results[0]['category']
            print(f"[CATEGORY] Using top match category: {query_category}")
        
        # STEP 3: Apply CATEGORY FILTERING with penalties
        if query_category:
            for result in final_results:
                result_category = result['category']
                
                # Check if categories match (normalized comparison)
                if not normalizer.are_same_category(query_category, result_category):
                    # MASSIVE PENALTY: Wrong category (e.g., Cameras when searching Smartphones)
                    # Apply 99% penalty - score drops to 1% (effectively removes from results)
                    original_score = result['similarity_score']
                    result['similarity_score'] = result['similarity_score'] * 0.01  # 99% PENALTY!
                    result['penalty_applied'] = f"WRONG_CATEGORY (was {original_score:.3f})"
                    result['expected_category'] = query_category
                else:
                    # BONUS: Same category - apply exact match scoring + category boost
                    # First, add a baseline category match bonus
                    result['similarity_score'] = min(result['similarity_score'] * 1.15, 0.99)  # +15% boost
                    
                    bonus = 0.0
                    if query_text and query_text.strip():
                        # Brand matching
                        brand = result.get('brand', '')
                        if brand and brand.lower() in query_text.lower():
                            bonus += 0.30  # Brand match: +30%
                        
                        # Name token overlap
                        name_tokens = set(result['name'].lower().split())
                        query_tokens = set(query_text.lower().split())
                        name_overlap = len(name_tokens & query_tokens) / max(len(name_tokens), 1)
                        
                        if name_overlap > 0.5:
                            bonus += 0.25  # Strong name match: +25%
                        elif name_overlap > 0.3:
                            bonus += 0.15  # Partial name match: +15%
                    
                    # Apply bonus (capped at 99%)
                    if bonus > 0:
                        result['similarity_score'] = min(result['similarity_score'] + bonus, 0.99)
                        result['bonus_applied'] = f"+{int(bonus*100)}%"
        
        # STEP 4: Re-sort after category penalties and bonuses
        final_results.sort(key=lambda x: -x['similarity_score'])
        
        total_time = time.time() - search_start
        print(f"[TIMING] Total search time - {total_time:.2f}s")
        print(f"[CATEGORY] Detected category: {query_category}")
        if final_results:
            print(f"[RESULTS] Top match: {final_results[0]['name']} ({final_results[0]['similarity_score']*100:.1f}%)")
        
        # PHASE 2: Add multi-store pricing to top results
        for result in final_results[:top_k]:
            if result.get('global_product_id'):
                listings = self.get_product_listings(result['global_product_id'])
                result['listings'] = listings
                # Add best price for easy access
                if listings:
                    result['price'] = listings[0]['price']  # Already sorted by price ASC
                    result['url'] = listings[0]['product_url']
                    result['available_stores'] = len(listings)
                else:
                    result['price'] = 0.0
                    result['url'] = ''
                    result['available_stores'] = 0
        
        # Return top k
        return final_results[:top_k]
    
    def save_search_result(
        self, 
        image_name: str, 
        results: List[Dict[str, Any]]
    ) -> Optional[int]:
        """
        Save search results to PostgreSQL database.
        
        Args:
            image_name: Name of the uploaded image
            results: Search results (will be stored as JSONB)
            
        Returns:
            ID of the inserted record
        """
        # Insert into database using execute_update for proper commit
        # Then retrieve the ID
        from sqlalchemy import text
        
        with self.db.engine.begin() as conn:
            result = conn.execute(
                text("""
                    INSERT INTO public.clip_search_results (image_name, raw_json_result, created_at)
                    VALUES (:image_name, CAST(:raw_json_result AS jsonb), :created_at)
                    RETURNING id
                """),
                {
                    'image_name': image_name,
                    'raw_json_result': json.dumps(results, ensure_ascii=False),
                    'created_at': datetime.now()
                }
            )
            row = result.fetchone()
            return int(row[0]) if row else None


def search_and_save(
    image_bytes: bytes,
    image_name: str,
    query_text: Optional[str] = None,
    top_k: int = 10,
    products_source: str = "db",
    engine: Optional['HybridSearchEngine'] = None
) -> Dict[str, Any]:
    """
    HypeLens v1.0 Main Entry Point: Hybrid search with multi-store pricing
    
    PHASE 2 UPDATE: Returns exact_match and similar_items sections
    
    Args:
        image_bytes: Raw image file bytes
        image_name: Name of the uploaded image file
        query_text: Optional keyword query
        top_k: Number of results to return
        products_source: "db" or "json"
        engine: Optional preloaded HybridSearchEngine instance (PHASE 2 optimization)
        
    Returns:
        Dictionary with exact_match (with multi-store pricing) and similar_items
    """
    # PHASE 2 FIX: Use provided engine or create new one
    if engine is None:
        engine = HybridSearchEngine()
        engine = HybridSearchEngine()
    
    # Perform hybrid search
    results = engine.hybrid_search(
        image_bytes=image_bytes,
        query_text=query_text,
        top_k=top_k,
        products_source=products_source
    )
    
    # PHASE 2: Separate exact matches (≥70%) from similar items (<70%)
    # STRICTER THRESHOLD: Only truly confident matches get "exact match" label
    EXACT_MATCH_THRESHOLD = 0.70  # Raised from 0.60 to 0.70
    
    exact_match = None
    similar_items = []
    
    for result in results:
        if result['similarity_score'] >= EXACT_MATCH_THRESHOLD:
            # First exact match becomes THE exact match (highest score)
            if exact_match is None:
                exact_match = result
            else:
                # Additional exact matches go to similar_items
                similar_items.append(result)
        else:
            similar_items.append(result)
    
    # Save to database (save all results for history)
    search_id = engine.save_search_result(image_name, results)
    
    return {
        'status': 'success',
        'search_id': search_id,
        'image_name': image_name,
        'query_text': query_text,
        'total_results': len(results),
        'threshold': EXACT_MATCH_THRESHOLD,
        
        # PHASE 2 NEW FORMAT:
        'exact_match': exact_match,  # Single product with listings array
        'similar_items': similar_items,  # Array of similar products
        
        # Backward compatibility (frontend might still use this)
        'results': results
    }


if __name__ == "__main__":
    """
    Example usage / testing
    """
    # Example: Load test image
    test_image_path = "images/test_local2.jpg"
    
    if os.path.exists(test_image_path):
        with open(test_image_path, 'rb') as f:
            image_data = f.read()
        
        # Perform search
        result = search_and_save(
            image_bytes=image_data,
            image_name="test_local2.jpg",
            query_text="test product",
            top_k=5,
            products_source="db"
        )
        
        # Print results
        print(json.dumps(result, indent=2, default=str))
    else:
        print(f"Test image not found: {test_image_path}")
