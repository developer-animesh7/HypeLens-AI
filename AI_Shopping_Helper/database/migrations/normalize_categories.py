"""
Database Category Normalization Migration
==========================================
Normalizes all product categories to standard format
Fixes: smartphone -> Smartphones, laptop -> Laptops, etc.
"""
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from backend.database.db_connection import DatabaseConnection
from backend.ai.category_normalizer import get_normalizer


def normalize_database_categories():
    """Normalize all product categories in database"""
    db = DatabaseConnection()
    normalizer = get_normalizer()
    
    print("\n" + "="*80)
    print("🔧 NORMALIZING DATABASE CATEGORIES")
    print("="*80)
    
    # Get all unique categories
    query = "SELECT DISTINCT category FROM public.products_global WHERE category IS NOT NULL"
    rows = db.execute_query(query)
    
    print(f"\nFound {len(rows)} unique categories:")
    print("-" * 80)
    
    category_mapping = {}
    for row in rows:
        raw_category = row['category']
        normalized_category = normalizer.normalize(raw_category)
        category_mapping[raw_category] = normalized_category
        
        status = "✅ OK" if raw_category == normalized_category else "🔄 NEEDS UPDATE"
        print(f"  {status:12s} '{raw_category:25s}' → '{normalized_category}'")
    
    # Count products that need updating
    needs_update = {k: v for k, v in category_mapping.items() if k != v}
    
    if not needs_update:
        print("\n✅ All categories are already normalized!")
        print("="*80 + "\n")
        return
    
    print(f"\n{len(needs_update)} categories need normalization")
    print("-" * 80)
    
    # Ask for confirmation
    response = input("\n⚠️  Proceed with normalization? (yes/no): ").strip().lower()
    if response != 'yes':
        print("❌ Normalization cancelled")
        print("="*80 + "\n")
        return
    
    # Update database
    print("\nUpdating database...")
    print("-" * 80)
    
    total_updated = 0
    for raw_category, normalized_category in needs_update.items():
        update_query = """
        UPDATE public.products_global
        SET category = :normalized
        WHERE category = :raw
        """
        
        rows_affected = db.execute_update(
            update_query,
            {'normalized': normalized_category, 'raw': raw_category}
        )
        
        total_updated += rows_affected
        print(f"  Updated {rows_affected:3d} products: '{raw_category}' → '{normalized_category}'")
    
    print(f"\n✅ Successfully normalized {total_updated} products!")
    
    # Verify results
    print("\nVerifying results...")
    print("-" * 80)
    
    verify_query = """
    SELECT category, COUNT(*) as count 
    FROM public.products_global 
    WHERE category IS NOT NULL
    GROUP BY category 
    ORDER BY count DESC
    """
    
    verify_rows = db.execute_query(verify_query)
    
    print("\nCurrent categories in database:")
    for row in verify_rows:
        print(f"  {row['category']:25s}: {row['count']:3d} products")
    
    print("\n" + "="*80)
    print("✅ CATEGORY NORMALIZATION COMPLETE!")
    print("="*80 + "\n")


if __name__ == "__main__":
    normalize_database_categories()
