"""
Product Recommendation Engine using Sentence Transformers and ChromaDB
"""

import logging
import os
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import sqlite3
import json
import numpy as np

logger = logging.getLogger(__name__)

class ProductRecommendationEngine:
    """
    AI-powered product recommendation engine that uses semantic similarity
    to find related products based on their descriptions.
    """
    
    def __init__(self, 
                 model_name: str = "all-MiniLM-L6-v2",
                 chroma_db_path: str = "data/chroma_db",
                 sqlite_db_path: str = "data/shopping_assistant.db"):
        """
        Initialize the recommendation engine
        
        Args:
            model_name: HuggingFace model name for generating embeddings
            chroma_db_path: Path to store ChromaDB vector database
            sqlite_db_path: Path to SQLite database with product data
        """
        # Instance configuration
        self.model_name = model_name
        self.chroma_db_path = chroma_db_path
        self.sqlite_db_path = sqlite_db_path
        self.model = None
        self.chroma_client = None
        self.collection = None

        # Ensure chroma directory exists
        try:
            os.makedirs(self.chroma_db_path, exist_ok=True)
        except Exception:
            # If creation fails, continue; initialize_vector_db will handle errors
            pass

    
        
    def initialize_model(self):
        """Load the sentence transformer model"""
        try:
            logger.info(f"Loading sentence transformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise e
    
    def initialize_vector_db(self):
        """Initialize vector DB: try ChromaDB if enabled, else fall back to SQLite."""
        try:
            if self.use_chroma:
                try:
                    import importlib
                    importlib.import_module("chromadb")  # Lazy probe; no hard dependency
                except Exception as ie:
                    logger.warning(f"ChromaDB not available ({ie}); falling back to SQLite for embeddings")
                    self.use_chroma = False

            if self.use_chroma:
                logger.info("Initializing ChromaDB...")
                import chromadb  # type: ignore  # validated via importlib above
                self.chroma_client = chromadb.PersistentClient(path=self.chroma_db_path)
                # Create or get collection
                self.collection = self.chroma_client.get_or_create_collection(
                    name="product_embeddings",
                    metadata={"description": "Product embeddings for recommendation system"}
                )
                logger.info("ChromaDB initialized successfully")
                return

            # Ensure SQLite table for embeddings exists
            logger.info("Using SQLite for embeddings")
            conn = sqlite3.connect(self.sqlite_db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS product_embeddings (
                    product_id INTEGER PRIMARY KEY,
                    embedding TEXT NOT NULL
                )
            ''')
            conn.commit()
            conn.close()
            logger.info("SQLite embeddings table ready")
        except Exception as e:
            logger.error(f"Error initializing vector DB: {e}")
            raise e
    
    def get_products_from_db(self) -> List[Dict[str, Any]]:
        """Fetch all products from SQLite database"""
        try:
            conn = sqlite3.connect(self.sqlite_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, description, category, price, rating, platform, url, image_url
                FROM products 
                WHERE description IS NOT NULL AND description != ''
            """)
            
            products = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            logger.info(f"Retrieved {len(products)} products from database")
            return products
            
        except Exception as e:
            logger.error(f"Error fetching products from database: {e}")
            raise e
    
    def generate_embeddings_for_all_products(self):
        """
        Generate embeddings for all products and store them in ChromaDB
        This is typically run once or when new products are added.
        """
        if not self.model:
            self.initialize_model()
        if not self.collection:
            self.initialize_vector_db()
        
        try:
            logger.info("Starting embedding generation for all products...")
            
            # Get all products
            products = self.get_products_from_db()
            
            if not products:
                logger.warning("No products found with descriptions")
                return
            
            # Prepare data for embedding
            descriptions = []
            product_ids = []
            metadatas = []
            
            for product in products:
                # Combine name and description for better context
                text_to_embed = f"{product['name']} - {product['description']}"
                descriptions.append(text_to_embed)
                product_ids.append(str(product['id']))
                metadatas.append({
                    'name': product['name'],
                    'category': product['category'],
                    'price': product['price'],
                    'rating': product['rating'],
                    'platform': product['platform']
                })
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(descriptions)} products...")
            embeddings = self.model.encode(descriptions, show_progress_bar=True)
            
            # Store embeddings in chosen backend
            if self.use_chroma:
                # Clear existing data and add new embeddings
                try:
                    existing_data = self.collection.get()
                    if existing_data.get('ids'):
                        self.collection.delete(ids=existing_data['ids'])
                except Exception as e:
                    logger.warning(f"Could not clear existing data: {e}")

                self.collection.add(
                    embeddings=embeddings.tolist(),
                    documents=descriptions,
                    metadatas=metadatas,
                    ids=product_ids
                )
            else:
                # Save embeddings into SQLite as JSON arrays
                conn = sqlite3.connect(self.sqlite_db_path)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM product_embeddings')
                for pid, emb in zip(product_ids, embeddings):
                    cursor.execute(
                        'INSERT OR REPLACE INTO product_embeddings(product_id, embedding) VALUES(?, ?)',
                        (int(pid), json.dumps(emb.tolist()))
                    )
                conn.commit()
                conn.close()
            
            logger.info(f"Successfully generated and stored embeddings for {len(products)} products")
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise e
    
    def get_recommendations(self, product_id: int, num_recommendations: int = 5) -> List[Dict[str, Any]]:
        """
        Get product recommendations based on similarity to the given product
        
        Args:
            product_id: ID of the product to find recommendations for
            num_recommendations: Number of recommendations to return
            
        Returns:
            List of recommended products with similarity scores
        """
        if not self.model:
            self.initialize_model()
        if not self.collection:
            self.initialize_vector_db()
        
        try:
            # Get the target product from SQLite
            conn = sqlite3.connect(self.sqlite_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, description, category, price, rating, platform, url, image_url
                FROM products 
                WHERE id = ? AND description IS NOT NULL AND description != ''
            """, (product_id,))
            
            target_product = cursor.fetchone()
            conn.close()
            
            if not target_product:
                logger.warning(f"Product {product_id} not found or has no description")
                return []
            
            # Generate embedding for the target product
            target_text = f"{target_product['name']} - {target_product['description']}"
            target_embedding = self.model.encode([target_text])
            
            recommendations = []
            if self.use_chroma:
                # Query ChromaDB for similar products
                results = self.collection.query(
                    query_embeddings=target_embedding.tolist(),
                    n_results=num_recommendations + 1,  # +1 because we'll exclude the target product
                    include=['metadatas', 'distances', 'documents']
                )

                # Process results
                for product_id_str, metadata, distance, document in zip(
                    results['ids'][0], 
                    results['metadatas'][0], 
                    results['distances'][0],
                    results['documents'][0]
                ):
                    if int(product_id_str) == product_id:
                        continue
                    similarity_score = 1 / (1 + distance)
                    recommendation = {
                        'id': int(product_id_str),
                        'name': metadata['name'],
                        'category': metadata['category'],
                        'price': metadata['price'],
                        'rating': metadata['rating'],
                        'platform': metadata['platform'],
                        'similarity_score': round(similarity_score, 4),
                        'description_preview': document[:100] + "..." if len(document) > 100 else document
                    }
                    recommendations.append(recommendation)
                    if len(recommendations) >= num_recommendations:
                        break
            else:
                # Load embeddings from SQLite and compute cosine similarity in-memory using numpy
                conn = sqlite3.connect(self.sqlite_db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT product_id, embedding FROM product_embeddings')
                rows = cursor.fetchall()
                conn.close()

                if not rows:
                    logger.warning("No embeddings found in SQLite. Run generate_embeddings first.")
                    return []

                db_ids = []
                db_embeddings = []
                for rid, emb_json in rows:
                    db_ids.append(int(rid))
                    db_embeddings.append(np.array(json.loads(emb_json), dtype=float))

                db_embeddings = np.vstack(db_embeddings)  # shape (N, dim)
                target_vec = np.array(target_embedding[0], dtype=float)

                # Compute cosine similarities
                def cosine_sim(a, b):
                    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10)

                sims = np.dot(db_embeddings, target_vec) / (np.linalg.norm(db_embeddings, axis=1) * (np.linalg.norm(target_vec) + 1e-10))

                # Pair ids with sims, exclude target
                pairs = [(pid, float(sim)) for pid, sim in zip(db_ids, sims) if pid != product_id]
                pairs.sort(key=lambda x: x[1], reverse=True)

                # Fetch product metadata for top results
                top = pairs[:num_recommendations]
                conn = sqlite3.connect(self.sqlite_db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                for pid, sim in top:
                    cursor.execute('SELECT id, name, category, price, rating, platform, description FROM products WHERE id = ?', (pid,))
                    row = cursor.fetchone()
                    if not row:
                        continue
                    document = row['description'] or ''
                    recommendation = {
                        'id': int(row['id']),
                        'name': row['name'],
                        'category': row['category'],
                        'price': row['price'],
                        'rating': row['rating'],
                        'platform': row['platform'],
                        'similarity_score': round(sim, 4),
                        'description_preview': document[:100] + '...' if len(document) > 100 else document
                    }
                    recommendations.append(recommendation)
                conn.close()
            
            logger.info(f"Generated {len(recommendations)} recommendations for product {product_id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations for product {product_id}: {e}")
            raise e
    
    def add_product_embedding(self, product_id: int):
        """
        Add embedding for a single new product
        This is used when a new product is added to the database
        """
        if not self.model:
            self.initialize_model()
        if not self.collection:
            self.initialize_vector_db()
        
        try:
            # Get the product from SQLite
            conn = sqlite3.connect(self.sqlite_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, description, category, price, rating, platform, url, image_url
                FROM products 
                WHERE id = ? AND description IS NOT NULL AND description != ''
            """, (product_id,))
            
            product = cursor.fetchone()
            conn.close()
            
            if not product:
                logger.warning(f"Product {product_id} not found or has no description")
                return
            
            # Generate embedding
            text_to_embed = f"{product['name']} - {product['description']}"
            embedding = self.model.encode([text_to_embed])
            
            if self.use_chroma and self.collection is not None:
                # Add to ChromaDB
                self.collection.add(
                    embeddings=embedding.tolist(),
                    documents=[text_to_embed],
                    metadatas=[{
                        'name': product['name'],
                        'category': product['category'],
                        'price': product['price'],
                        'rating': product['rating'],
                        'platform': product['platform']
                    }],
                    ids=[str(product_id)]
                )
            else:
                # Store embedding in SQLite
                conn = sqlite3.connect(self.sqlite_db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS product_embeddings (
                        product_id INTEGER PRIMARY KEY,
                        embedding TEXT NOT NULL
                    )
                ''')
                cursor.execute(
                    'INSERT OR REPLACE INTO product_embeddings(product_id, embedding) VALUES(?, ?)',
                    (int(product_id), json.dumps(embedding[0].tolist()))
                )
                conn.commit()
                conn.close()
            
            logger.info(f"Added embedding for product {product_id}")
            
        except Exception as e:
            logger.error(f"Error adding embedding for product {product_id}: {e}")
            raise e


# Global instance: allow overriding the model via EMBEDDING_MODEL env var
_default_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
recommendation_engine = ProductRecommendationEngine(model_name=_default_model)
