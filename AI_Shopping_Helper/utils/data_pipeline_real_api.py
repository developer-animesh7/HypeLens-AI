"""
HypeLens Data Pipeline - Phase 4: REAL Flipkart API Integration
==================================================================

This script uses the ACTUAL Flipkart Affiliate API to fetch products.
API Documentation: https://affiliate.flipkart.com/api-docs

Key Features:
1. Fetches products from real Flipkart Affiliate API (v1.1.0)
2. Generates CLIP embeddings for NEW products only
3. Updates prices for EXISTING products
4. Supports pagination (500 products per API call)
5. Handles categories dynamically

Usage:
    # Fetch products from a specific category
    python data_pipeline_real_api.py --category tyy --limit 1000
    
    # Search for specific products
    python data_pipeline_real_api.py --search "laptop" --limit 50
    
    # List all available categories
    python data_pipeline_real_api.py --list-categories
    
    # Continuous mode (runs every 6 hours)
    python data_pipeline_real_api.py --continuous

Requirements:
    - Flipkart Affiliate ID
    - Flipkart Affiliate Token
    - Add them to config/pipeline_config.env
"""

import argparse
import sys
import time
import logging
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import uuid

# External dependencies
import requests
from PIL import Image
import io
from dotenv import load_dotenv

# Database and AI imports
from sqlalchemy import text
from backend.database.db_connection import DatabaseConnection
from backend.ai.hybrid_search import HybridSearchEngine

# Load environment variables
load_dotenv('config/pipeline_config.env')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'data_pipeline_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)


class FlipkartAPIClient:
    """
    Real Flipkart Affiliate API Client (v1.1.0)
    Documentation: https://affiliate.flipkart.com/api-docs
    """
    
    def __init__(self, affiliate_id: str, affiliate_token: str):
        self.affiliate_id = affiliate_id
        self.affiliate_token = affiliate_token
        self.base_url = "https://affiliate-api.flipkart.net/affiliate"
        self.session = requests.Session()
        self.session.headers.update({
            'Fk-Affiliate-Id': self.affiliate_id,
            'Fk-Affiliate-Token': self.affiliate_token
        })
        logging.info(f"✓ Flipkart API client initialized (Affiliate ID: {affiliate_id[:10]}...)")
    
    def get_categories(self) -> Dict:
        """
        Get all available product categories from Flipkart
        API: GET /api/{trackingId}.json
        """
        try:
            url = f"{self.base_url}/api/{self.affiliate_id}.json"
            logging.info(f"Fetching categories from: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Extract category list
            categories = {}
            if 'apiGroups' in data and 'affiliate' in data['apiGroups']:
                listings = data['apiGroups']['affiliate'].get('apiListings', {})
                
                for cat_key, cat_data in listings.items():
                    # Get v1.1.0 API URL
                    variants = cat_data.get('availableVariants', {})
                    if 'v1.1.0' in variants:
                        categories[cat_key] = {
                            'name': cat_data.get('apiName'),
                            'url': variants['v1.1.0'].get('get'),
                            'delta_url': variants['v1.1.0'].get('deltaGet')
                        }
            
            logging.info(f"✓ Found {len(categories)} categories")
            return categories
            
        except Exception as e:
            logging.error(f"Error fetching categories: {e}")
            return {}
    
    def fetch_products_from_category(self, category_code: str, limit: int = 500) -> List[Dict]:
        """
        Fetch products from a specific category
        
        Args:
            category_code: Category code (e.g., 'tyy' for mobiles, '4io' for laptops)
            limit: Maximum products to fetch (API returns 500 per page)
        
        Returns:
            List of product dictionaries
        """
        try:
            # Get categories to find the URL
            categories = self.get_categories()
            
            if category_code not in categories:
                logging.error(f"Category '{category_code}' not found!")
                logging.info("Available categories:")
                for code, info in list(categories.items())[:10]:
                    logging.info(f"  - {code}: {info['name']}")
                return []
            
            url = categories[category_code]['url']
            logging.info(f"Fetching from category '{category_code}': {categories[category_code]['name']}")
            
            return self._fetch_from_url(url, limit)
            
        except Exception as e:
            logging.error(f"Error fetching products: {e}")
            return []
    
    def _fetch_from_url(self, url: str, limit: int) -> List[Dict]:
        """
        Fetch products from a Flipkart API URL with pagination
        
        Args:
            url: Flipkart API URL
            limit: Maximum products to fetch
        
        Returns:
            List of product dictionaries
        """
        products = []
        page = 1
        
        try:
            while url and len(products) < limit:
                logging.info(f"📡 Fetching page {page}... (Total so far: {len(products)})")
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                # Extract products from API response (v1.1.0 format)
                product_list = data.get('productInfoList', [])
                logging.info(f"   Received {len(product_list)} products from API")
                
                for item in product_list:
                    if len(products) >= limit:
                        break
                    
                    try:
                        product = self._parse_product(item)
                        if product:
                            products.append(product)
                    except Exception as e:
                        logging.warning(f"Failed to parse product: {e}")
                        continue
                
                # Check for next page
                url = data.get('nextUrl')
                page += 1
                
                # Respect API rate limits
                time.sleep(0.5)
                
        except Exception as e:
            logging.error(f"Error in pagination: {e}")
        
        logging.info(f"✓ Total fetched: {len(products)} products")
        return products
    
    def _parse_product(self, item: Dict) -> Optional[Dict]:
        """
        Parse a product from Flipkart API response (v1.1.0 format)
        
        Args:
            item: Product item from API
        
        Returns:
            Normalized product dictionary
        """
        try:
            base_info = item.get('productBaseInfoV1', {})
            shipping_info = item.get('productShippingInfoV1', {})
            
            # Get prices
            selling_price = base_info.get('flipkartSpecialPrice', {}).get('amount', 0)
            mrp = base_info.get('maximumRetailPrice', {}).get('amount', 0)
            
            # Skip if no valid price
            if not selling_price or selling_price <= 0:
                return None
            
            # Extract category
            category = self._extract_category(base_info.get('categoryPath', ''))
            
            # Get best image URL
            image_url = self._get_best_image(base_info.get('imageUrls', {}))
            
            product = {
                'external_id': base_info.get('productId'),
                'name': base_info.get('title', 'Unknown Product'),
                'brand': base_info.get('productBrand', 'Unknown'),
                'category': category,
                'description': base_info.get('productDescription', '')[:500],  # Limit length
                'price': float(selling_price),
                'original_price': float(mrp),
                'discount': float(base_info.get('discountPercentage', 0)),
                'image_url': image_url,
                'product_url': base_info.get('productUrl', ''),
                'in_stock': base_info.get('inStock', False),
                'platform': 'Flipkart'
            }
            
            return product
            
        except Exception as e:
            logging.error(f"Error parsing product: {e}")
            return None
    
    def _extract_category(self, category_path: str) -> str:
        """Extract readable category from categoryPath JSON"""
        try:
            if not category_path:
                return "Electronics"
            
            paths = json.loads(category_path)
            if paths and len(paths) > 0 and len(paths[0]) > 2:
                # Get the last meaningful category (skip FLIPKART_TREE)
                return paths[0][-1].get('node_name', 'Electronics')
        except:
            pass
        return "Electronics"
    
    def _get_best_image(self, image_urls: Dict) -> str:
        """Get the highest quality image URL"""
        # Prefer higher resolution
        for size in ['800x800', '400x400', '200x200', 'unknown']:
            if size in image_urls:
                return image_urls[size]
        
        # Return any available
        if image_urls:
            return next(iter(image_urls.values()))
        
        return ""
    
    def search_products(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search products by keyword
        API: GET /1.0/search.json?query=keyword&resultCount=10
        
        Args:
            query: Search term (e.g., 'laptop', 'samsung phone')
            limit: Max results (API limit is 10)
        
        Returns:
            List of product dictionaries
        """
        try:
            url = f"{self.base_url}/1.0/search.json"
            params = {
                'query': query,
                'resultCount': min(limit, 10)
            }
            
            logging.info(f"🔍 Searching for: '{query}'")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            products = []
            for item in data.get('productInfoList', []):
                product = self._parse_product(item)
                if product:
                    products.append(product)
            
            logging.info(f"✓ Found {len(products)} products")
            return products
            
        except Exception as e:
            logging.error(f"Error searching: {e}")
            return []


class DataPipeline:
    """
    Automated product data pipeline
    Fetches products → Generates embeddings → Updates database
    """
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.db.connect()
        self.conn = self.db.engine.connect()
        
        # Initialize AI search engine for embeddings
        logging.info("Loading CLIP model...")
        self.search_engine = HybridSearchEngine()
        logging.info("✓ CLIP model ready")
        
        # Initialize API client
        affiliate_id = os.getenv('FLIPKART_AFFILIATE_ID')
        affiliate_token = os.getenv('FLIPKART_AFFILIATE_TOKEN')
        
        if not affiliate_id or not affiliate_token:
            raise ValueError(
                "Missing API credentials! "
                "Add FLIPKART_AFFILIATE_ID and FLIPKART_AFFILIATE_TOKEN "
                "to config/pipeline_config.env"
            )
        
        self.flipkart = FlipkartAPIClient(affiliate_id, affiliate_token)
        
        # Stats tracking
        self.stats = {
            'total_processed': 0,
            'new_products': 0,
            'updated_products': 0,
            'embeddings_generated': 0,
            'errors': 0
        }
    
    def run(self, category: str = None, limit: int = 500, search_query: str = None):
        """
        Run the data pipeline
        
        Args:
            category: Flipkart category code (e.g., 'tyy', '4io')
            limit: Maximum products to process
            search_query: Search term (alternative to category)
        """
        start_time = time.time()
        
        logging.info("=" * 70)
        logging.info("🚀 HypeLens Data Pipeline - Starting")
        logging.info("=" * 70)
        
        # Fetch products
        if search_query:
            products = self.flipkart.search_products(search_query, limit)
        elif category:
            products = self.flipkart.fetch_products_from_category(category, limit)
        else:
            logging.error("Must specify either --category or --search!")
            return
        
        if not products:
            logging.warning("No products fetched!")
            return
        
        logging.info(f"\n📦 Processing {len(products)} products...")
        logging.info("-" * 70)
        
        # Process each product
        for i, product in enumerate(products, 1):
            try:
                logging.info(f"\n[{i}/{len(products)}] {product['name']}")
                logging.info(f"   Price: ₹{product['price']:,.2f} | Brand: {product['brand']} | Category: {product['category']}")
                
                # Find or create global product
                global_id = self._find_or_create_global_product(product)
                
                # Update listing
                self._upsert_listing(global_id, product)
                
                self.stats['total_processed'] += 1
                logging.info(f"   ✓ Successfully processed")
                
            except Exception as e:
                logging.error(f"   ✗ Error processing product: {e}")
                self.stats['errors'] += 1
        
        # Print final stats
        elapsed = time.time() - start_time
        self._print_stats(elapsed)
    
    def _find_or_create_global_product(self, product: Dict) -> uuid.UUID:
        """Find existing product or create new one with embedding"""
        try:
            # Check if product exists
            query = text("""
                SELECT pg.global_product_id
                FROM listings_scraped ls
                JOIN products_global pg ON ls.global_product_id = pg.global_product_id
                WHERE ls.external_product_id = :external_id
                AND ls.store_name = :platform
                LIMIT 1
            """)
            
            result = self.conn.execute(
                query,
                {
                    'external_id': product['external_id'],
                    'platform': product['platform']
                }
            ).fetchone()
            
            if result:
                logging.info(f"   ℹ Product exists: {result[0]}")
                self.stats['updated_products'] += 1
                return result[0]
            
            # Create new product with embedding
            logging.info(f"   🆕 New product - generating embedding...")
            
            # Generate embedding
            embedding = None
            if product['image_url']:
                try:
                    embedding = self.search_engine.generate_image_embedding(product['image_url'])
                    self.stats['embeddings_generated'] += 1
                    logging.info(f"   ✓ Embedding generated: {len(embedding)} dimensions")
                except Exception as e:
                    logging.warning(f"   ⚠ Failed to generate embedding: {e}")
            
            # Insert new product
            global_id = uuid.uuid4()
            insert_query = text("""
                INSERT INTO products_global (
                    global_product_id, name, brand, category, description,
                    image_url, embedding_vector, created_at
                )
                VALUES (
                    :id, :name, :brand, :category, :description,
                    :image_url, :embedding, NOW()
                )
            """)
            
            self.conn.execute(
                insert_query,
                {
                    'id': global_id,
                    'name': product['name'],
                    'brand': product['brand'],
                    'category': product['category'],
                    'description': product['description'],
                    'image_url': product['image_url'],
                    'embedding': embedding
                }
            )
            self.conn.commit()
            
            self.stats['new_products'] += 1
            logging.info(f"   ✓ Created product: {global_id}")
            return global_id
            
        except Exception as e:
            logging.error(f"Error in find_or_create: {e}")
            raise
    
    def _upsert_listing(self, global_id: uuid.UUID, product: Dict):
        """Insert or update product listing"""
        try:
            # Check if listing exists
            check_query = text("""
                SELECT listing_id
                FROM listings_scraped
                WHERE external_product_id = :external_id
                AND store_name = :platform
                LIMIT 1
            """)
            
            existing = self.conn.execute(
                check_query,
                {
                    'external_id': product['external_id'],
                    'platform': product['platform']
                }
            ).fetchone()
            
            if existing:
                # Update existing listing
                update_query = text("""
                    UPDATE listings_scraped
                    SET price = :price,
                        original_price = :original_price,
                        discount_percentage = :discount,
                        product_url = :url,
                        in_stock = :in_stock,
                        last_scraped_at = NOW()
                    WHERE listing_id = :listing_id
                """)
                
                self.conn.execute(
                    update_query,
                    {
                        'price': product['price'],
                        'original_price': product['original_price'],
                        'discount': product['discount'],
                        'url': product['product_url'],
                        'in_stock': product['in_stock'],
                        'listing_id': existing[0]
                    }
                )
                logging.info(f"   ✓ Updated listing (ID: {existing[0]})")
            else:
                # Insert new listing
                insert_query = text("""
                    INSERT INTO listings_scraped (
                        global_product_id, store_name, price, original_price,
                        discount_percentage, product_url, in_stock,
                        external_product_id, last_scraped_at
                    )
                    VALUES (
                        :global_id, :platform, :price, :original_price,
                        :discount, :url, :in_stock,
                        :external_id, NOW()
                    )
                """)
                
                self.conn.execute(
                    insert_query,
                    {
                        'global_id': global_id,
                        'platform': product['platform'],
                        'price': product['price'],
                        'original_price': product['original_price'],
                        'discount': product['discount'],
                        'url': product['product_url'],
                        'in_stock': product['in_stock'],
                        'external_id': product['external_id']
                    }
                )
                logging.info(f"   ✓ Created new listing")
            
            self.conn.commit()
            
        except Exception as e:
            logging.error(f"Error in upsert_listing: {e}")
            raise
    
    def _print_stats(self, elapsed: float):
        """Print final statistics"""
        logging.info("\n" + "=" * 70)
        logging.info("📊 PIPELINE RESULTS")
        logging.info("=" * 70)
        logging.info(f"Total processed:        {self.stats['total_processed']}")
        logging.info(f"New products created:   {self.stats['new_products']}")
        logging.info(f"Existing updated:       {self.stats['updated_products']}")
        logging.info(f"Embeddings generated:   {self.stats['embeddings_generated']}")
        logging.info(f"Errors:                 {self.stats['errors']}")
        logging.info("-" * 70)
        logging.info(f"Time elapsed:           {elapsed:.2f} seconds")
        logging.info(f"Products per second:    {self.stats['total_processed']/elapsed:.2f}")
        logging.info("=" * 70)
        logging.info("✅ Pipeline Complete!\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='HypeLens Data Pipeline - Flipkart Product Automation'
    )
    
    parser.add_argument(
        '--category',
        type=str,
        help='Flipkart category code (e.g., "tyy" for mobiles, "4io" for laptops)'
    )
    
    parser.add_argument(
        '--search',
        type=str,
        help='Search query (e.g., "laptop", "samsung phone")'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=500,
        help='Maximum products to fetch (default: 500)'
    )
    
    parser.add_argument(
        '--list-categories',
        action='store_true',
        help='List all available categories and exit'
    )
    
    parser.add_argument(
        '--continuous',
        action='store_true',
        help='Run continuously (every 6 hours)'
    )
    
    args = parser.parse_args()
    
    try:
        # List categories
        if args.list_categories:
            affiliate_id = os.getenv('FLIPKART_AFFILIATE_ID')
            affiliate_token = os.getenv('FLIPKART_AFFILIATE_TOKEN')
            
            if not affiliate_id or not affiliate_token:
                print("❌ Missing API credentials!")
                print("Add to config/pipeline_config.env:")
                print("  FLIPKART_AFFILIATE_ID=your_id")
                print("  FLIPKART_AFFILIATE_TOKEN=your_token")
                return
            
            client = FlipkartAPIClient(affiliate_id, affiliate_token)
            categories = client.get_categories()
            
            print("\n📂 Available Flipkart Categories:")
            print("=" * 70)
            for code, info in sorted(categories.items())[:20]:  # Show first 20
                print(f"  {code:15s} → {info['name']}")
            print(f"\n(Showing 20 of {len(categories)} categories)")
            print("\nUsage:")
            print(f"  python {sys.argv[0]} --category tyy --limit 100")
            return
        
        # Run pipeline
        pipeline = DataPipeline()
        
        if args.continuous:
            logging.info("🔄 Continuous mode enabled (runs every 6 hours)")
            while True:
                pipeline.run(
                    category=args.category,
                    limit=args.limit,
                    search_query=args.search
                )
                logging.info("\n😴 Sleeping for 6 hours...\n")
                time.sleep(6 * 3600)
        else:
            pipeline.run(
                category=args.category,
                limit=args.limit,
                search_query=args.search
            )
    
    except KeyboardInterrupt:
        logging.info("\n\n⚠ Pipeline stopped by user")
    except Exception as e:
        logging.error(f"\n❌ Pipeline error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
