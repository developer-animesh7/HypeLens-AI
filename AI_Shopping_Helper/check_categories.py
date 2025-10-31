"""Check categories in database"""
from backend.database.db_connection import DatabaseConnection

db = DatabaseConnection()
rows = db.execute_query('SELECT DISTINCT category, COUNT(*) as count FROM public.products_global GROUP BY category ORDER BY count DESC')

print('\n' + '='*60)
print('CATEGORIES IN DATABASE')
print('='*60)
for r in rows:
    print(f'  {r["category"]}: {r["count"]} products')
print('='*60)

# Also check a few sample products
print('\nSAMPLE PRODUCTS:')
print('='*60)
samples = db.execute_query('SELECT name, category, brand FROM public.products_global LIMIT 10')
for s in samples:
    print(f'  {s["name"][:50]:50s} | {s["category"]:15s} | {s["brand"]}')
print('='*60 + '\n')
