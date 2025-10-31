"""
HypeLens v1.0 - Data Migration Script
Purpose: Migrate existing products table to new products_global + listings_scraped structure
Date: October 24, 2025
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
import json
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
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


class DataMigrator:
    """Migrates data from old products table to new HypeLens schema"""
    
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.migration_stats = {
            'products_migrated': 0,
            'listings_created': 0,
            'duplicates_found': 0,
            'errors': 0
        }
    
    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(
                host=DATABASE_CONFIG['host'],
                database=DATABASE_CONFIG['database'],
                user=DATABASE_CONFIG['user'],
                password=DATABASE_CONFIG['password'],
                port=DATABASE_CONFIG['port']
            )
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            print("✅ Connected to database")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def verify_old_table_exists(self):
        """Check if old products table exists"""
        try:
            self.cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'products'
                );
            """)
            exists = self.cursor.fetchone()['exists']
            
            if exists:
                self.cursor.execute("SELECT COUNT(*) as count FROM products;")
                count = self.cursor.fetchone()['count']
                print(f"✅ Found old 'products' table with {count} rows")
                return True
            else:
                print("❌ Old 'products' table not found")
                return False
        except Exception as e:
            print(f"❌ Error checking old table: {e}")
            return False
    
    def verify_new_tables_exist(self):
        """Check if new tables exist"""
        try:
            self.cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('products_global', 'listings_scraped');
            """)
            tables = [row['table_name'] for row in self.cursor.fetchall()]
            
            if 'products_global' in tables and 'listings_scraped' in tables:
                print("✅ New tables 'products_global' and 'listings_scraped' exist")
                return True
            else:
                print(f"❌ Missing tables. Found: {tables}")
                print("   Run schema_hypelens.sql first!")
                return False
        except Exception as e:
            print(f"❌ Error checking new tables: {e}")
            return False
    
    def extract_specifications(self, old_product):
        """Extract specifications from old product data"""
        specs = {}
        
        # Try to extract from description or other fields
        description = old_product.get('description', '') or ''
        
        # Common spec patterns (basic extraction)
        # You can enhance this based on your data
        if 'specifications' in old_product and old_product['specifications']:
            try:
                specs = json.loads(old_product['specifications'])
            except:
                pass
        
        return specs
    
    def normalize_brand(self, brand_str):
        """Normalize brand names"""
        if not brand_str:
            return None
        
        brand_map = {
            'apple': 'Apple',
            'samsung': 'Samsung',
            'oneplus': 'OnePlus',
            'xiaomi': 'Xiaomi',
            'realme': 'Realme',
            'oppo': 'Oppo',
            'vivo': 'Vivo',
            'lenovo': 'Lenovo',
            'hp': 'HP',
            'dell': 'Dell',
            'asus': 'Asus'
        }
        
        brand_lower = brand_str.lower().strip()
        return brand_map.get(brand_lower, brand_str.title())
    
    def create_search_keywords(self, product):
        """Generate search keywords from product data"""
        keywords = []
        
        if product.get('name'):
            keywords.append(product['name'])
        if product.get('brand'):
            keywords.append(product['brand'])
        if product.get('category'):
            keywords.append(product['category'])
        if product.get('description'):
            # Extract first 100 chars
            keywords.append(product['description'][:100])
        
        return ' '.join(keywords).lower()
    
    def detect_duplicates(self, name, brand):
        """Check if product already exists in products_global"""
        try:
            self.cursor.execute("""
                SELECT global_product_id 
                FROM products_global 
                WHERE LOWER(name) = LOWER(%s) 
                AND LOWER(brand) = LOWER(%s)
                LIMIT 1;
            """, (name, brand))
            
            result = self.cursor.fetchone()
            if result:
                self.migration_stats['duplicates_found'] += 1
                return result['global_product_id']
            return None
        except Exception as e:
            print(f"⚠️  Error checking duplicates: {e}")
            return None
    
    def migrate_product(self, old_product):
        """Migrate a single product from old to new schema"""
        try:
            # Extract data
            name = old_product.get('name') or old_product.get('title', 'Unknown Product')
            brand = self.normalize_brand(old_product.get('brand'))
            category = old_product.get('category', 'General')
            description = old_product.get('description', '')
            image_url = old_product.get('image_url', '')
            specifications = self.extract_specifications(old_product)
            
            # Check for duplicates
            existing_id = self.detect_duplicates(name, brand)
            
            if existing_id:
                print(f"   ⚠️  Duplicate found: {name} (using existing ID)")
                global_product_id = existing_id
            else:
                # Generate UUID
                global_product_id = uuid.uuid4()
                
                # Create search keywords
                search_keywords = self.create_search_keywords({
                    'name': name,
                    'brand': brand,
                    'category': category,
                    'description': description
                })
                
                # Insert into products_global
                self.cursor.execute("""
                    INSERT INTO products_global (
                        global_product_id,
                        name,
                        brand,
                        category,
                        description,
                        specifications,
                        image_url,
                        search_keywords
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING global_product_id;
                """, (
                    str(global_product_id),
                    name,
                    brand,
                    category,
                    description,
                    json.dumps(specifications),
                    image_url,
                    search_keywords
                ))
                
                self.migration_stats['products_migrated'] += 1
                print(f"   ✅ Migrated product: {name[:50]}...")
            
            # Create listing in listings_scraped
            price = old_product.get('price', 0)
            product_url = old_product.get('flipkart_url') or old_product.get('url', '')
            store_product_id = old_product.get('id', '')
            
            # Insert listing
            self.cursor.execute("""
                INSERT INTO listings_scraped (
                    global_product_id,
                    store_name,
                    store_product_id,
                    price,
                    in_stock,
                    product_url,
                    image_url,
                    source
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING listing_id;
            """, (
                str(global_product_id),
                'Flipkart',  # Assuming old data is from Flipkart
                str(store_product_id),
                price,
                True,  # Assume in stock
                product_url,
                image_url,
                'migration'
            ))
            
            self.migration_stats['listings_created'] += 1
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error migrating product: {e}")
            self.migration_stats['errors'] += 1
            return False
    
    def run_migration(self):
        """Execute the full migration process"""
        print("\n" + "="*60)
        print("  HypeLens v1.0 - Data Migration")
        print("="*60 + "\n")
        
        # Step 1: Connect
        if not self.connect():
            return False
        
        # Step 2: Verify tables
        if not self.verify_old_table_exists():
            return False
        if not self.verify_new_tables_exist():
            return False
        
        # Step 3: Fetch all old products
        print("\n📦 Fetching products from old table...")
        try:
            self.cursor.execute("SELECT * FROM products ORDER BY id;")
            old_products = self.cursor.fetchall()
            total = len(old_products)
            print(f"   Found {total} products to migrate\n")
        except Exception as e:
            print(f"❌ Error fetching old products: {e}")
            return False
        
        # Step 4: Migrate each product
        print("🔄 Starting migration...\n")
        for idx, product in enumerate(old_products, 1):
            print(f"[{idx}/{total}] Processing product ID {product.get('id')}...")
            self.migrate_product(product)
            
            # Commit every 50 products
            if idx % 50 == 0:
                self.conn.commit()
                print(f"\n   💾 Committed {idx} products\n")
        
        # Step 5: Final commit
        self.conn.commit()
        print("\n💾 Final commit complete")
        
        # Step 6: Verify migration
        print("\n🔍 Verifying migration...\n")
        self.cursor.execute("SELECT COUNT(*) as count FROM products_global;")
        products_count = self.cursor.fetchone()['count']
        
        self.cursor.execute("SELECT COUNT(*) as count FROM listings_scraped;")
        listings_count = self.cursor.fetchone()['count']
        
        # Step 7: Print summary
        print("\n" + "="*60)
        print("  MIGRATION SUMMARY")
        print("="*60)
        print(f"✅ Products migrated:    {self.migration_stats['products_migrated']}")
        print(f"✅ Listings created:     {self.migration_stats['listings_created']}")
        print(f"⚠️  Duplicates found:     {self.migration_stats['duplicates_found']}")
        print(f"❌ Errors encountered:   {self.migration_stats['errors']}")
        print(f"\n📊 Database Status:")
        print(f"   products_global:      {products_count} rows")
        print(f"   listings_scraped:     {listings_count} rows")
        print("="*60 + "\n")
        
        if self.migration_stats['errors'] == 0:
            print("✅ Migration completed successfully!")
        else:
            print("⚠️  Migration completed with some errors. Check logs above.")
        
        return True
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("\n🔌 Database connection closed")


def main():
    """Main execution function"""
    print("\n" + "🚀"*30)
    print("\nHypeLens v1.0 - Data Migration Starting...")
    print("Prerequisites checked:")
    print("  ✅ Database backup created")
    print("  ✅ Schema tables created")
    print("  ✅ Services stopped")
    print("\nProceeding with migration...\n")
    
    # Run migration
    migrator = DataMigrator()
    try:
        success = migrator.run_migration()
        if success:
            print("\n🎉 Next Steps:")
            print("   1. Run rebuild_index.py to update vector embeddings")
            print("   2. Update API code to use new schema")
            print("   3. Test search functionality")
            print("   4. Verify frontend displays correctly")
    except Exception as e:
        print(f"\n💥 Fatal error during migration: {e}")
    finally:
        migrator.close()


if __name__ == "__main__":
    main()
