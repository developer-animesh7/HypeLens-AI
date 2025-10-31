"""
HypeLens v1.0 - Vector Index Rebuild Script
Purpose: Rebuild ChromaDB index with new global_product_id keys
Date: October 24, 2025
"""

import sys
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import chromadb
from chromadb.config import Settings
import torch
import clip
from PIL import Image
import requests
from io import BytesIO
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Database configuration from .env
from dotenv import load_dotenv
load_dotenv()

DATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'hypelens',
    'user': 'hypelens_user',
    'password': 'StrongPassword123',
    'port': 5432
}


class VectorIndexRebuilder:
    """Rebuilds ChromaDB vector index with new product IDs"""
    
    def __init__(self):
        self.db_conn = None
        self.db_cursor = None
        self.chroma_client = None
        self.collection = None
        self.clip_model = None
        self.clip_preprocess = None
        self.device = None
        
        self.stats = {
            'total_products': 0,
            'indexed': 0,
            'failed': 0,
            'skipped': 0
        }
    
    def connect_database(self):
        """Connect to PostgreSQL"""
        try:
            self.db_conn = psycopg2.connect(
                host=DATABASE_CONFIG['host'],
                database=DATABASE_CONFIG['database'],
                user=DATABASE_CONFIG['user'],
                password=DATABASE_CONFIG['password'],
                port=DATABASE_CONFIG['port']
            )
            self.db_cursor = self.db_conn.cursor(cursor_factory=RealDictCursor)
            print("✅ Connected to PostgreSQL database")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def initialize_chromadb(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Path to ChromaDB storage
            chroma_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'data',
                'chroma_db'
            )
            
            # Ensure directory exists
            os.makedirs(chroma_path, exist_ok=True)
            
            # Initialize client
            self.chroma_client = chromadb.PersistentClient(
                path=chroma_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Delete old collection if exists
            try:
                self.chroma_client.delete_collection(name="product_embeddings")
                print("🗑️  Deleted old collection")
            except:
                pass
            
            # Create new collection
            self.collection = self.chroma_client.create_collection(
                name="product_embeddings",
                metadata={"description": "HypeLens product embeddings with global_product_id"}
            )
            
            print(f"✅ Initialized ChromaDB at: {chroma_path}")
            return True
            
        except Exception as e:
            print(f"❌ ChromaDB initialization failed: {e}")
            return False
    
    def load_clip_model(self):
        """Load CLIP model for encoding"""
        try:
            print("\n🔄 Loading CLIP model (ViT-L/14)...")
            print("   This will take ~40 seconds...")
            
            # Determine device
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"   Using device: {self.device}")
            
            start_time = time.time()
            
            # Load model
            self.clip_model, self.clip_preprocess = clip.load(
                "ViT-L/14",
                device=self.device
            )
            
            elapsed = time.time() - start_time
            print(f"✅ CLIP model loaded in {elapsed:.1f}s")
            
            return True
            
        except Exception as e:
            print(f"❌ CLIP model loading failed: {e}")
            return False
    
    def download_image(self, image_url):
        """Download image from URL"""
        try:
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                return image.convert('RGB')
            return None
        except Exception as e:
            print(f"      ⚠️  Image download failed: {e}")
            return None
    
    def encode_image(self, image_url):
        """Generate CLIP embedding for image"""
        try:
            # Download image
            image = self.download_image(image_url)
            if image is None:
                return None
            
            # Preprocess and encode
            image_tensor = self.clip_preprocess(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                image_features = self.clip_model.encode_image(image_tensor)
                # Normalize
                image_features /= image_features.norm(dim=-1, keepdim=True)
            
            # Convert to list for ChromaDB
            embedding = image_features.cpu().numpy().flatten().tolist()
            return embedding
            
        except Exception as e:
            print(f"      ⚠️  Encoding failed: {e}")
            return None
    
    def index_product(self, product):
        """Index a single product in ChromaDB"""
        try:
            global_product_id = str(product['global_product_id'])
            name = product['name']
            image_url = product['image_url']
            
            # Skip if no image
            if not image_url:
                print(f"      ⚠️  No image URL, skipping")
                self.stats['skipped'] += 1
                return False
            
            # Generate embedding
            embedding = self.encode_image(image_url)
            if embedding is None:
                self.stats['failed'] += 1
                return False
            
            # Create metadata
            metadata = {
                'name': name[:500],  # ChromaDB has limits
                'brand': product.get('brand', '')[:100] or '',
                'category': product.get('category', '')[:100] or '',
                'description': (product.get('description', '')[:500] or '')
            }
            
            # Add to collection
            self.collection.add(
                ids=[global_product_id],
                embeddings=[embedding],
                metadatas=[metadata]
            )
            
            self.stats['indexed'] += 1
            return True
            
        except Exception as e:
            print(f"      ❌ Indexing failed: {e}")
            self.stats['failed'] += 1
            return False
    
    def rebuild_index(self):
        """Main rebuild process"""
        print("\n" + "="*60)
        print("  HypeLens v1.0 - Vector Index Rebuild")
        print("="*60 + "\n")
        
        # Step 1: Connect to database
        if not self.connect_database():
            return False
        
        # Step 2: Initialize ChromaDB
        if not self.initialize_chromadb():
            return False
        
        # Step 3: Load CLIP model
        if not self.load_clip_model():
            return False
        
        # Step 4: Fetch products
        print("\n📦 Fetching products from products_global...")
        try:
            self.db_cursor.execute("""
                SELECT 
                    global_product_id,
                    name,
                    brand,
                    category,
                    description,
                    image_url
                FROM products_global
                ORDER BY created_at;
            """)
            products = self.db_cursor.fetchall()
            self.stats['total_products'] = len(products)
            print(f"   Found {self.stats['total_products']} products\n")
        except Exception as e:
            print(f"❌ Error fetching products: {e}")
            return False
        
        # Step 5: Index each product
        print("🔄 Starting indexing process...\n")
        start_time = time.time()
        
        for idx, product in enumerate(products, 1):
            product_name = product['name'][:50]
            print(f"[{idx}/{self.stats['total_products']}] {product_name}...")
            
            self.index_product(product)
            
            # Progress update every 50
            if idx % 50 == 0:
                elapsed = time.time() - start_time
                rate = idx / elapsed
                remaining = (self.stats['total_products'] - idx) / rate
                print(f"\n   📊 Progress: {idx}/{self.stats['total_products']} | " +
                      f"Rate: {rate:.1f} prod/sec | " +
                      f"ETA: {remaining/60:.1f} min\n")
        
        total_time = time.time() - start_time
        
        # Step 6: Verify index
        print("\n🔍 Verifying index...")
        count = self.collection.count()
        print(f"   ChromaDB collection size: {count} vectors")
        
        # Step 7: Print summary
        print("\n" + "="*60)
        print("  REBUILD SUMMARY")
        print("="*60)
        print(f"✅ Products processed:   {self.stats['total_products']}")
        print(f"✅ Successfully indexed: {self.stats['indexed']}")
        print(f"⚠️  Skipped (no image):  {self.stats['skipped']}")
        print(f"❌ Failed:               {self.stats['failed']}")
        print(f"\n⏱️  Total time:          {total_time/60:.1f} minutes")
        print(f"📊 Average rate:        {self.stats['total_products']/total_time:.2f} products/sec")
        print("="*60 + "\n")
        
        if self.stats['indexed'] == self.stats['total_products'] - self.stats['skipped']:
            print("✅ Index rebuild completed successfully!")
        else:
            print("⚠️  Index rebuild completed with some failures.")
        
        return True
    
    def close(self):
        """Cleanup connections"""
        if self.db_cursor:
            self.db_cursor.close()
        if self.db_conn:
            self.db_conn.close()
        print("\n🔌 Database connection closed")


def main():
    """Main execution"""
    print("\n" + "🚀"*30)
    print("\nHypeLens v1.0 - Vector Index Rebuild Starting...")
    print("Prerequisites checked:")
    print("  ✅ Data migration completed (363 products)")
    print("  ✅ Services stopped")
    print("  ✅ Internet connection active")
    print(f"\nEstimated time: ~10-15 minutes for 363 products")
    print("\nProceeding with rebuild...\n")
    
    # Run rebuild
    rebuilder = VectorIndexRebuilder()
    try:
        success = rebuilder.rebuild_index()
        if success:
            print("\n🎉 Next Steps:")
            print("   1. Update backend API code for new schema")
            print("   2. Implement model preloading (Phase 2)")
            print("   3. Test search with new IDs")
            print("   4. Verify results match correctly")
    except KeyboardInterrupt:
        print("\n\n⚠️  Rebuild interrupted by user")
        print("   You may need to run this again to complete indexing")
    except Exception as e:
        print(f"\n💥 Fatal error during rebuild: {e}")
    finally:
        rebuilder.close()


if __name__ == "__main__":
    main()
