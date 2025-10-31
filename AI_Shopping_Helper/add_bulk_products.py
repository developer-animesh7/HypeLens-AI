"""
Bulk Product Generator for HypeLens
====================================
Generates 10,000+ realistic products for testing and development

Categories:
- Smartphones (3000+ products)
- Laptops (2000+ products) 
- Electronics (5000+ products: TVs, Cameras, Headphones, etc.)

Usage:
    python add_bulk_products.py --count 10000
    python add_bulk_products.py --smartphones 3000 --laptops 2000 --electronics 5000
    python add_bulk_products.py --quick  # Fast mode: 1000 products without embeddings
"""

import argparse
import random
import uuid
import sys
import time
from datetime import datetime
from typing import List, Dict, Optional
import logging

from sqlalchemy import text
from backend.database.db_connection import DatabaseConnection
from backend.ai.hybrid_search import HybridSearchEngine

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(f'bulk_products_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)


class ProductGenerator:
    """Generate realistic product data"""
    
    # Smartphone data
    SMARTPHONE_BRANDS = [
        'Samsung', 'Apple', 'OnePlus', 'Xiaomi', 'Realme', 'Oppo', 'Vivo',
        'Google', 'Motorola', 'Nokia', 'Nothing', 'iQOO', 'POCO', 'Infinix',
        'Tecno', 'Lava', 'Micromax', 'Asus', 'Sony', 'Honor'
    ]
    
    SMARTPHONE_MODELS = {
        'Samsung': ['Galaxy S24', 'Galaxy S23', 'Galaxy A54', 'Galaxy A34', 'Galaxy M34', 'Galaxy F54'],
        'Apple': ['iPhone 15', 'iPhone 15 Plus', 'iPhone 15 Pro', 'iPhone 15 Pro Max', 'iPhone 14', 'iPhone SE'],
        'OnePlus': ['OnePlus 12', 'OnePlus 11', 'OnePlus Nord 3', 'OnePlus Nord CE 3', 'OnePlus 10T'],
        'Xiaomi': ['Xiaomi 14', 'Xiaomi 13', 'Redmi Note 13 Pro', 'Redmi 12', 'POCO X6', 'Mi 11X'],
        'Realme': ['Realme 12 Pro', 'Realme 11 Pro', 'Realme Narzo 60', 'Realme C55', 'Realme GT 2'],
        'Google': ['Pixel 8', 'Pixel 8 Pro', 'Pixel 7a', 'Pixel 7', 'Pixel 6a'],
        'Oppo': ['Oppo Reno 11', 'Oppo F23', 'Oppo A78', 'Oppo Find X6', 'Oppo K11'],
        'Vivo': ['Vivo V29', 'Vivo Y100', 'Vivo T2', 'Vivo X90', 'Vivo Y56'],
    }
    
    SMARTPHONE_STORAGE = ['64GB', '128GB', '256GB', '512GB', '1TB']
    SMARTPHONE_RAM = ['4GB', '6GB', '8GB', '12GB', '16GB']
    SMARTPHONE_COLORS = ['Black', 'White', 'Blue', 'Green', 'Purple', 'Gold', 'Silver', 'Red', 'Pink']
    
    # Laptop data
    LAPTOP_BRANDS = [
        'Dell', 'HP', 'Lenovo', 'Asus', 'Acer', 'Apple', 'MSI', 'Razer',
        'Microsoft', 'Samsung', 'LG', 'Alienware', 'Huawei', 'Xiaomi'
    ]
    
    LAPTOP_SERIES = {
        'Dell': ['XPS 13', 'XPS 15', 'Inspiron 15', 'Inspiron 14', 'Latitude 7420', 'Vostro 3420'],
        'HP': ['Pavilion 15', 'Pavilion 14', 'Envy 13', 'Omen 15', 'EliteBook 840', 'ProBook 450'],
        'Lenovo': ['ThinkPad X1', 'ThinkPad T14', 'IdeaPad Slim 3', 'Yoga 9i', 'Legion 5', 'ThinkBook 15'],
        'Asus': ['ZenBook 14', 'VivoBook 15', 'ROG Strix G15', 'TUF Gaming A15', 'ExpertBook B9'],
        'Acer': ['Aspire 5', 'Swift 3', 'Nitro 5', 'Predator Helios 300', 'TravelMate P2'],
        'Apple': ['MacBook Air M2', 'MacBook Air M1', 'MacBook Pro 14"', 'MacBook Pro 16"'],
    }
    
    LAPTOP_PROCESSORS = ['Intel i3 11th Gen', 'Intel i5 12th Gen', 'Intel i7 13th Gen', 'Intel i9 13th Gen',
                          'AMD Ryzen 5 5600H', 'AMD Ryzen 7 5800H', 'AMD Ryzen 9 5900HX', 'Apple M1', 'Apple M2']
    LAPTOP_RAM_OPTIONS = ['8GB', '16GB', '32GB', '64GB']
    LAPTOP_STORAGE = ['256GB SSD', '512GB SSD', '1TB SSD', '2TB SSD']
    
    # Electronics data
    ELECTRONICS_TYPES = {
        'TV': {
            'brands': ['Samsung', 'LG', 'Sony', 'Mi', 'OnePlus', 'TCL', 'Hisense', 'Panasonic'],
            'sizes': ['32 inch', '43 inch', '50 inch', '55 inch', '65 inch', '75 inch'],
            'types': ['4K Ultra HD', 'Full HD', '8K QLED', 'OLED'],
        },
        'Camera': {
            'brands': ['Canon', 'Nikon', 'Sony', 'Fujifilm', 'Panasonic', 'Olympus', 'GoPro'],
            'types': ['DSLR', 'Mirrorless', 'Point & Shoot', 'Action Camera'],
            'megapixels': ['20.1MP', '24.2MP', '26MP', '45MP', '50MP'],
        },
        'Headphones': {
            'brands': ['Sony', 'Bose', 'JBL', 'Sennheiser', 'Audio-Technica', 'Beats', 'OnePlus', 'Samsung'],
            'types': ['Over-Ear', 'On-Ear', 'In-Ear', 'True Wireless', 'Wireless', 'Wired'],
            'features': ['ANC', 'Bass Boost', 'Gaming', 'Sports', 'Studio'],
        },
        'Smartwatch': {
            'brands': ['Apple', 'Samsung', 'Fitbit', 'Garmin', 'Amazfit', 'Noise', 'boAt', 'Fire-Boltt'],
            'features': ['Heart Rate', 'GPS', 'SpO2', 'Sleep Tracking', 'Fitness Tracker'],
        },
        'Tablet': {
            'brands': ['Apple', 'Samsung', 'Lenovo', 'Xiaomi', 'OnePlus', 'Realme', 'Amazon'],
            'sizes': ['7 inch', '8 inch', '10 inch', '11 inch', '12.9 inch'],
            'storage': ['32GB', '64GB', '128GB', '256GB', '512GB'],
        },
    }
    
    # Image URLs (placeholder images from reliable CDNs)
    IMAGE_URLS = {
        'Smartphones': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9',
        'Laptops': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853',
        'Electronics': 'https://images.unsplash.com/photo-1498049794561-7780e7231661',
    }
    
    def generate_smartphone(self) -> Dict:
        """Generate a random smartphone product"""
        brand = random.choice(self.SMARTPHONE_BRANDS)
        models = self.SMARTPHONE_MODELS.get(brand, ['Pro', 'Max', 'Ultra', 'Plus', 'Lite'])
        model = random.choice(models)
        storage = random.choice(self.SMARTPHONE_STORAGE)
        ram = random.choice(self.SMARTPHONE_RAM)
        color = random.choice(self.SMARTPHONE_COLORS)
        
        name = f"{brand} {model} ({storage}, {ram} RAM) {color}"
        
        # Realistic pricing based on brand
        base_prices = {
            'Apple': (70000, 150000),
            'Samsung': (15000, 120000),
            'OnePlus': (25000, 65000),
            'Google': (40000, 90000),
            'Xiaomi': (10000, 50000),
            'Realme': (8000, 40000),
            'Oppo': (12000, 50000),
            'Vivo': (12000, 45000),
        }
        
        price_range = base_prices.get(brand, (8000, 50000))
        price = random.randint(price_range[0], price_range[1])
        discount = random.randint(5, 40)
        original_price = int(price / (1 - discount/100))
        
        description = f"{brand} {model} smartphone with {storage} storage and {ram} RAM. " \
                      f"Available in {color} color. Features include 5G connectivity, " \
                      f"AI-powered camera, fast charging, and premium display."
        
        return {
            'name': name,
            'brand': brand,
            'category': 'Smartphones',
            'description': description,
            'price': float(price),
            'original_price': float(original_price),
            'discount': float(discount),
            'image_url': self.IMAGE_URLS['Smartphones'],
            'platform': 'Generated',
            'in_stock': random.choice([True, True, True, False]),  # 75% in stock
        }
    
    def generate_laptop(self) -> Dict:
        """Generate a random laptop product"""
        brand = random.choice(self.LAPTOP_BRANDS)
        series = self.LAPTOP_SERIES.get(brand, ['Pro', 'Elite', 'Business', 'Gaming'])
        model = random.choice(series)
        processor = random.choice(self.LAPTOP_PROCESSORS)
        ram = random.choice(self.LAPTOP_RAM_OPTIONS)
        storage = random.choice(self.LAPTOP_STORAGE)
        
        name = f"{brand} {model} {processor} {ram} {storage} Laptop"
        
        # Realistic pricing
        base_prices = {
            'Apple': (80000, 300000),
            'Dell': (35000, 180000),
            'HP': (30000, 150000),
            'Lenovo': (28000, 140000),
            'Asus': (30000, 200000),
            'Acer': (25000, 120000),
        }
        
        price_range = base_prices.get(brand, (30000, 100000))
        price = random.randint(price_range[0], price_range[1])
        discount = random.randint(5, 35)
        original_price = int(price / (1 - discount/100))
        
        description = f"{brand} {model} laptop powered by {processor} processor with {ram} RAM " \
                      f"and {storage} storage. Perfect for work, gaming, and entertainment. " \
                      f"Features include backlit keyboard, HD webcam, and long battery life."
        
        return {
            'name': name,
            'brand': brand,
            'category': 'Laptops',
            'description': description,
            'price': float(price),
            'original_price': float(original_price),
            'discount': float(discount),
            'image_url': self.IMAGE_URLS['Laptops'],
            'platform': 'Generated',
            'in_stock': random.choice([True, True, True, False]),
        }
    
    def generate_electronics(self) -> Dict:
        """Generate a random electronics product"""
        device_type = random.choice(list(self.ELECTRONICS_TYPES.keys()))
        device_data = self.ELECTRONICS_TYPES[device_type]
        
        brand = random.choice(device_data['brands'])
        
        if device_type == 'TV':
            size = random.choice(device_data['sizes'])
            tv_type = random.choice(device_data['types'])
            name = f"{brand} {size} {tv_type} Smart TV"
            price = random.randint(15000, 200000)
            description = f"{brand} {size} {tv_type} Smart TV with stunning picture quality, " \
                          f"smart features, and built-in streaming apps."
        
        elif device_type == 'Camera':
            cam_type = random.choice(device_data['types'])
            mp = random.choice(device_data['megapixels'])
            name = f"{brand} {cam_type} Camera {mp}"
            price = random.randint(25000, 350000)
            description = f"{brand} {cam_type} camera with {mp} resolution. " \
                          f"Professional photography made easy with advanced features."
        
        elif device_type == 'Headphones':
            hp_type = random.choice(device_data['types'])
            feature = random.choice(device_data['features'])
            name = f"{brand} {hp_type} Headphones with {feature}"
            price = random.randint(1000, 35000)
            description = f"{brand} {hp_type} headphones featuring {feature}. " \
                          f"Premium audio quality for music lovers."
        
        elif device_type == 'Smartwatch':
            feature = random.choice(device_data['features'])
            name = f"{brand} Smartwatch with {feature}"
            price = random.randint(2000, 80000)
            description = f"{brand} smartwatch with {feature} monitoring. " \
                          f"Stay connected and track your fitness goals."
        
        else:  # Tablet
            size = random.choice(device_data['sizes'])
            storage = random.choice(device_data['storage'])
            name = f"{brand} Tablet {size} {storage}"
            price = random.randint(10000, 150000)
            description = f"{brand} tablet with {size} display and {storage} storage. " \
                          f"Perfect for work, study, and entertainment."
        
        discount = random.randint(5, 40)
        original_price = int(price / (1 - discount/100))
        
        return {
            'name': name,
            'brand': brand,
            'category': 'Electronics',
            'description': description,
            'price': float(price),
            'original_price': float(original_price),
            'discount': float(discount),
            'image_url': self.IMAGE_URLS['Electronics'],
            'platform': 'Generated',
            'in_stock': random.choice([True, True, True, False]),
        }


class BulkProductInserter:
    """Insert products into database with embeddings"""
    
    def __init__(self, generate_embeddings: bool = True):
        self.db = DatabaseConnection()
        self.db.connect()
        self.conn = self.db.engine.connect()
        self.generator = ProductGenerator()
        self.generate_embeddings = generate_embeddings
        
        if generate_embeddings:
            logging.info("🤖 Loading CLIP model for embeddings...")
            self.search_engine = HybridSearchEngine()
            logging.info("✓ CLIP model ready")
        else:
            logging.info("⚡ Fast mode: Skipping embeddings")
            self.search_engine = None
        
        self.stats = {
            'smartphones': 0,
            'laptops': 0,
            'electronics': 0,
            'total': 0,
            'embeddings_generated': 0,
            'errors': 0,
        }
    
    def insert_products(self, 
                       smartphones: int = 0, 
                       laptops: int = 0, 
                       electronics: int = 0):
        """
        Insert bulk products into database
        
        Args:
            smartphones: Number of smartphone products to generate
            laptops: Number of laptop products to generate
            electronics: Number of electronics products to generate
        """
        start_time = time.time()
        total_products = smartphones + laptops + electronics
        
        logging.info("=" * 80)
        logging.info(f"🚀 BULK PRODUCT GENERATOR - Starting")
        logging.info("=" * 80)
        logging.info(f"📊 Target: {total_products:,} products")
        logging.info(f"   - Smartphones: {smartphones:,}")
        logging.info(f"   - Laptops: {laptops:,}")
        logging.info(f"   - Electronics: {electronics:,}")
        logging.info("=" * 80)
        
        # Generate and insert products
        categories = [
            ('Smartphones', smartphones, self.generator.generate_smartphone),
            ('Laptops', laptops, self.generator.generate_laptop),
            ('Electronics', electronics, self.generator.generate_electronics),
        ]
        
        for category_name, count, generator_func in categories:
            if count > 0:
                self._insert_category(category_name, count, generator_func)
        
        # Print stats
        elapsed = time.time() - start_time
        self._print_stats(elapsed)
    
    def _insert_category(self, category_name: str, count: int, generator_func):
        """Insert products for a specific category"""
        logging.info(f"\n{'='*80}")
        logging.info(f"📦 Generating {category_name.upper()}")
        logging.info(f"{'='*80}")
        
        for i in range(1, count + 1):
            try:
                # Generate product
                product = generator_func()
                
                # Create global product
                global_id = uuid.uuid4()
                
                # Generate embedding
                embedding = None
                if self.generate_embeddings and self.search_engine:
                    try:
                        embedding = self.search_engine.generate_image_embedding(product['image_url'])
                        self.stats['embeddings_generated'] += 1
                    except Exception as e:
                        logging.warning(f"   ⚠ Embedding failed: {e}")
                
                # Insert product
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
                        'embedding': embedding,
                    }
                )
                
                # Insert listing
                listing_query = text("""
                    INSERT INTO listings_scraped (
                        global_product_id, store_name, price, original_price,
                        discount_percentage, product_url, in_stock,
                        external_product_id, last_scraped_at
                    )
                    VALUES (
                        :global_id, :platform, :price, :original_price,
                        :discount, :url, :in_stock, :external_id, NOW()
                    )
                """)
                
                self.conn.execute(
                    listing_query,
                    {
                        'global_id': global_id,
                        'platform': product['platform'],
                        'price': product['price'],
                        'original_price': product['original_price'],
                        'discount': product['discount'],
                        'url': f'https://example.com/product/{global_id}',
                        'in_stock': product['in_stock'],
                        'external_id': f'GEN_{global_id}',
                    }
                )
                
                self.conn.commit()
                
                # Update stats
                self.stats['total'] += 1
                if category_name == 'Smartphones':
                    self.stats['smartphones'] += 1
                elif category_name == 'Laptops':
                    self.stats['laptops'] += 1
                else:
                    self.stats['electronics'] += 1
                
                # Progress update
                if i % 50 == 0:
                    progress = (i / count) * 100
                    logging.info(f"   [{i:,}/{count:,}] {progress:.1f}% - {product['name'][:60]}")
                
            except Exception as e:
                logging.error(f"   ✗ Error: {e}")
                self.stats['errors'] += 1
        
        logging.info(f"✅ {category_name}: {count:,} products created")
    
    def _print_stats(self, elapsed: float):
        """Print final statistics"""
        logging.info("\n" + "=" * 80)
        logging.info("📊 FINAL RESULTS")
        logging.info("=" * 80)
        logging.info(f"✅ Smartphones added:      {self.stats['smartphones']:,}")
        logging.info(f"✅ Laptops added:          {self.stats['laptops']:,}")
        logging.info(f"✅ Electronics added:      {self.stats['electronics']:,}")
        logging.info(f"{'='*80}")
        logging.info(f"🎯 TOTAL PRODUCTS:         {self.stats['total']:,}")
        logging.info(f"🤖 Embeddings generated:   {self.stats['embeddings_generated']:,}")
        logging.info(f"❌ Errors:                 {self.stats['errors']:,}")
        logging.info(f"{'='*80}")
        logging.info(f"⏱️  Time elapsed:           {elapsed:.2f} seconds ({elapsed/60:.1f} minutes)")
        logging.info(f"⚡ Products per second:    {self.stats['total']/elapsed:.2f}")
        logging.info("=" * 80)
        logging.info("✅ BULK IMPORT COMPLETE!")
        logging.info("")
        logging.info("🔄 Next steps:")
        logging.info("   1. Restart your backend server")
        logging.info("   2. Test search at http://localhost:3000")
        logging.info("   3. Verify categories are working correctly")
        logging.info("=" * 80)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Bulk Product Generator - Add 10,000+ products to HypeLens'
    )
    
    parser.add_argument(
        '--count',
        type=int,
        help='Total number of products (distributed across categories)'
    )
    
    parser.add_argument(
        '--smartphones',
        type=int,
        default=0,
        help='Number of smartphone products (default: 0)'
    )
    
    parser.add_argument(
        '--laptops',
        type=int,
        default=0,
        help='Number of laptop products (default: 0)'
    )
    
    parser.add_argument(
        '--electronics',
        type=int,
        default=0,
        help='Number of electronics products (default: 0)'
    )
    
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Fast mode: Skip embedding generation (faster but less accurate search)'
    )
    
    args = parser.parse_args()
    
    # Calculate distribution
    if args.count:
        # Distribute evenly
        smartphones = int(args.count * 0.3)  # 30% smartphones
        laptops = int(args.count * 0.2)      # 20% laptops
        electronics = args.count - smartphones - laptops  # 50% electronics
    else:
        smartphones = args.smartphones
        laptops = args.laptops
        electronics = args.electronics
    
    if smartphones + laptops + electronics == 0:
        print("❌ No products specified!")
        print("\nUsage examples:")
        print("  python add_bulk_products.py --count 10000")
        print("  python add_bulk_products.py --smartphones 3000 --laptops 2000 --electronics 5000")
        print("  python add_bulk_products.py --count 1000 --quick  # Fast mode")
        return
    
    try:
        inserter = BulkProductInserter(generate_embeddings=not args.quick)
        inserter.insert_products(
            smartphones=smartphones,
            laptops=laptops,
            electronics=electronics
        )
    except KeyboardInterrupt:
        logging.info("\n\n⚠️  Stopped by user")
    except Exception as e:
        logging.error(f"\n❌ Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
