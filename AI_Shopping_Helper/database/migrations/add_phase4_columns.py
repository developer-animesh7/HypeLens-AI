"""
Add external_product_id column to listings_scraped table
This is needed for Phase 4 automation pipeline
"""

from backend.database.db_connection import DatabaseConnection
from sqlalchemy import text

def add_external_product_id_column():
    """Add external_product_id column to support Phase 4"""
    
    print("\n📝 Adding external_product_id column to listings_scraped...")
    
    db = DatabaseConnection()
    
    try:
        with db.engine.begin() as conn:
            # Add column
            conn.execute(text("""
                ALTER TABLE listings_scraped 
                ADD COLUMN IF NOT EXISTS external_product_id VARCHAR(255)
            """))
            
            print("   ✓ Column 'external_product_id' added")
            
            # Add index for faster lookups
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_listings_external_id 
                ON listings_scraped(external_product_id)
            """))
            
            print("   ✓ Index 'idx_listings_external_id' created")
            
            # Update description field to TEXT if not already
            conn.execute(text("""
                ALTER TABLE products_global 
                ALTER COLUMN description TYPE TEXT
            """))
            
            print("   ✓ Description column type updated")
            
            # Add embedding_vector column if doesn't exist
            conn.execute(text("""
                ALTER TABLE products_global 
                ADD COLUMN IF NOT EXISTS embedding_vector FLOAT[]
            """))
            
            print("   ✓ Embedding vector column added")
            
            print("\n✅ Database schema updated for Phase 4!")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    add_external_product_id_column()
