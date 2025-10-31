# pgAdmin 4 - Useful SQL Queries for HypeLens Database

## How to Connect to Your Database in pgAdmin 4

1. **Open pgAdmin 4**
2. **Right-click on "Servers"** → Create → Server
3. **Enter connection details:**
   - **Name**: HypeLens (or any name you want)
   - **Connection tab**:
     - Host: `localhost`
     - Port: `5432`
     - Database: `hypelens_db`
     - Username: `postgres`
     - Password: `your_password`
4. **Click Save**

---

## Quick Queries to Run in pgAdmin Query Tool

### 1. View All Products (Basic Info)
```sql
SELECT 
    global_product_id,
    name,
    brand,
    category,
    created_at
FROM products_global
ORDER BY created_at DESC
LIMIT 50;
```

### 2. View All Listings with Prices
```sql
SELECT 
    l.listing_id,
    p.name as product_name,
    p.brand,
    l.store_name,
    l.price,
    l.product_url,
    l.in_stock,
    l.last_scraped_at
FROM listings_scraped l
JOIN products_global p ON l.global_product_id = p.global_product_id
ORDER BY l.last_scraped_at DESC
LIMIT 50;
```

### 3. Count Products by Store
```sql
SELECT 
    store_name,
    COUNT(*) as total_products
FROM listings_scraped
GROUP BY store_name
ORDER BY total_products DESC;
```

### 4. Count Products by Category
```sql
SELECT 
    category,
    COUNT(*) as total_products
FROM products_global
WHERE category IS NOT NULL
GROUP BY category
ORDER BY total_products DESC;
```

### 5. Price Statistics
```sql
SELECT 
    MIN(price) as min_price,
    MAX(price) as max_price,
    AVG(price) as avg_price,
    COUNT(*) as total_listings
FROM listings_scraped
WHERE price > 0;
```

### 6. Search for Specific Products (e.g., MacBook)
```sql
SELECT 
    p.name,
    p.brand,
    p.category,
    l.store_name,
    l.price,
    l.product_url
FROM products_global p
LEFT JOIN listings_scraped l ON p.global_product_id = l.global_product_id
WHERE 
    LOWER(p.name) LIKE '%macbook%'
    OR LOWER(p.brand) LIKE '%macbook%'
ORDER BY l.price ASC;
```

### 7. Products Added in Last 24 Hours
```sql
SELECT 
    p.name,
    p.brand,
    p.category,
    l.store_name,
    l.price,
    p.created_at
FROM products_global p
LEFT JOIN listings_scraped l ON p.global_product_id = l.global_product_id
WHERE p.created_at > NOW() - INTERVAL '24 hours'
ORDER BY p.created_at DESC;
```

### 8. Products Available on Multiple Stores (Price Comparison)
```sql
SELECT 
    p.name,
    p.brand,
    COUNT(DISTINCT l.store_name) as store_count,
    MIN(l.price) as cheapest_price,
    MAX(l.price) as highest_price,
    MAX(l.price) - MIN(l.price) as price_difference
FROM products_global p
JOIN listings_scraped l ON p.global_product_id = l.global_product_id
WHERE l.price > 0
GROUP BY p.global_product_id, p.name, p.brand
HAVING COUNT(DISTINCT l.store_name) > 1
ORDER BY price_difference DESC
LIMIT 20;
```

### 9. Products with AI Embeddings
```sql
SELECT 
    name,
    brand,
    category,
    CASE 
        WHEN embedding_vector IS NOT NULL THEN 'Yes'
        ELSE 'No'
    END as has_embedding,
    created_at
FROM products_global
ORDER BY created_at DESC
LIMIT 50;
```

### 10. View Phase 4 Products (with external_product_id)
```sql
SELECT 
    p.name,
    p.brand,
    l.store_name,
    l.external_product_id,
    l.price,
    l.last_scraped_at
FROM listings_scraped l
JOIN products_global p ON l.global_product_id = p.global_product_id
WHERE l.external_product_id IS NOT NULL
ORDER BY l.last_scraped_at DESC;
```

### 11. Database Size and Statistics
```sql
-- Total products
SELECT COUNT(*) as total_products FROM products_global;

-- Total listings
SELECT COUNT(*) as total_listings FROM listings_scraped;

-- Products with embeddings
SELECT 
    COUNT(*) as total,
    COUNT(embedding_vector) as with_embedding,
    ROUND(COUNT(embedding_vector) * 100.0 / COUNT(*), 2) as percentage
FROM products_global;
```

### 12. Most Expensive Products
```sql
SELECT 
    p.name,
    p.brand,
    l.store_name,
    l.price,
    l.product_url
FROM products_global p
JOIN listings_scraped l ON p.global_product_id = l.global_product_id
WHERE l.price > 0
ORDER BY l.price DESC
LIMIT 20;
```

### 13. Cheapest Products
```sql
SELECT 
    p.name,
    p.brand,
    l.store_name,
    l.price,
    l.product_url
FROM products_global p
JOIN listings_scraped l ON p.global_product_id = l.global_product_id
WHERE l.price > 0
ORDER BY l.price ASC
LIMIT 20;
```

### 14. Products by Price Range
```sql
-- Laptops between ₹50,000 and ₹100,000
SELECT 
    p.name,
    p.brand,
    l.store_name,
    l.price,
    l.product_url
FROM products_global p
JOIN listings_scraped l ON p.global_product_id = l.global_product_id
WHERE 
    LOWER(p.category) LIKE '%laptop%'
    AND l.price BETWEEN 50000 AND 100000
ORDER BY l.price ASC;
```

### 15. View Complete Product Details
```sql
SELECT 
    p.global_product_id,
    p.name,
    p.brand,
    p.category,
    p.description,
    p.image_url,
    p.created_at,
    l.listing_id,
    l.store_name,
    l.price,
    l.original_price,
    l.discount_percentage,
    l.product_url,
    l.in_stock,
    l.external_product_id,
    l.last_scraped_at
FROM products_global p
LEFT JOIN listings_scraped l ON p.global_product_id = l.global_product_id
ORDER BY p.created_at DESC
LIMIT 10;
```

---

## How to Run These Queries in pgAdmin 4

1. **Open pgAdmin 4** and connect to your database
2. **Navigate**: HypeLens → Databases → hypelens_db
3. **Click on "Query Tool"** icon (looks like a play button in toolbar)
4. **Copy any query** from above and paste it
5. **Press F5** or click the "Execute" button (▶️)
6. **View results** in the Data Output panel below

---

## Useful Views You Can Create

### Create a View for Easy Product Browsing
```sql
CREATE VIEW vw_products_with_prices AS
SELECT 
    p.global_product_id,
    p.name,
    p.brand,
    p.category,
    p.image_url,
    l.store_name,
    l.price,
    l.original_price,
    l.discount_percentage,
    l.product_url,
    l.in_stock,
    l.last_scraped_at
FROM products_global p
LEFT JOIN listings_scraped l ON p.global_product_id = l.global_product_id;
```

After creating the view, you can query it easily:
```sql
SELECT * FROM vw_products_with_prices 
WHERE LOWER(name) LIKE '%laptop%'
ORDER BY price ASC;
```

---

## Tips for pgAdmin 4

1. **Export Results to CSV:**
   - After running a query, click the "Download" button in the results panel
   - Choose CSV format

2. **Save Favorite Queries:**
   - Click "File" → "Save As" in Query Tool
   - Name it (e.g., "All Products.sql")

3. **Auto-refresh:**
   - Click the refresh icon to update table data
   - Right-click on table → "View/Edit Data" → "All Rows"

4. **Filter Results:**
   - Click column headers to sort
   - Use the filter icon to add WHERE conditions visually

5. **View Table Structure:**
   - Right-click on table (e.g., `products_global`)
   - Click "Properties" to see columns, types, constraints

---

## Common Database Locations

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `products_global` | Master product catalog | `global_product_id`, `name`, `brand`, `category`, `embedding_vector` |
| `listings_scraped` | Store-specific listings | `listing_id`, `global_product_id`, `store_name`, `price`, `external_product_id` |

---

## Example: Find Best Deals

```sql
-- Find products with biggest discounts
SELECT 
    p.name,
    p.brand,
    l.store_name,
    l.original_price,
    l.price as current_price,
    l.discount_percentage,
    l.original_price - l.price as savings,
    l.product_url
FROM products_global p
JOIN listings_scraped l ON p.global_product_id = l.global_product_id
WHERE 
    l.discount_percentage > 0
    AND l.price > 0
ORDER BY l.discount_percentage DESC
LIMIT 30;
```

---

## Need Help?

If you see any errors in pgAdmin:
- Check your connection settings (host, port, username, password)
- Make sure PostgreSQL service is running
- Verify database name is `hypelens_db`

If queries return no results:
- Run `SELECT COUNT(*) FROM products_global;` to check if data exists
- Check if table names are correct (case-sensitive on some systems)
