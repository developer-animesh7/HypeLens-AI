-- HypeLens v1.0 Database Schema
-- PostgreSQL Schema for Price Aggregation Architecture
-- Date: October 24, 2025

-- ============================================================================
-- TABLE 1: products_global
-- Purpose: Store unique products (deduplicated across all stores)
-- Key: global_product_id (UUID) - links to vector embeddings and listings
-- ============================================================================

CREATE TABLE IF NOT EXISTS products_global (
    -- Primary Key
    global_product_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Core Product Information
    name VARCHAR(500) NOT NULL,
    brand VARCHAR(100),
    category VARCHAR(100),
    description TEXT,
    
    -- Technical Specifications (flexible JSON structure)
    specifications JSONB DEFAULT '{}',
    -- Example: {"processor": "M2", "ram": "8GB", "storage": "256GB"}
    
    -- Image URL (from first discovered listing)
    image_url TEXT,
    
    -- Search Optimization
    search_keywords TEXT, -- For TF-IDF search
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Analytics
    total_searches INTEGER DEFAULT 0,
    last_searched_at TIMESTAMP
);

-- Indexes for Performance
CREATE INDEX idx_products_brand ON products_global(brand);
CREATE INDEX idx_products_category ON products_global(category);
CREATE INDEX idx_products_name ON products_global USING gin(to_tsvector('english', name));
CREATE INDEX idx_products_search_keywords ON products_global USING gin(to_tsvector('english', search_keywords));
CREATE INDEX idx_products_specs ON products_global USING gin(specifications);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_products_global_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_products_global
    BEFORE UPDATE ON products_global
    FOR EACH ROW
    EXECUTE FUNCTION update_products_global_timestamp();

-- ============================================================================
-- TABLE 2: listings_scraped
-- Purpose: Store prices and URLs from multiple stores for each product
-- Key: listing_id - links to global_product_id
-- ============================================================================

CREATE TABLE IF NOT EXISTS listings_scraped (
    -- Primary Key
    listing_id SERIAL PRIMARY KEY,
    
    -- Foreign Key to products_global
    global_product_id UUID NOT NULL REFERENCES products_global(global_product_id) ON DELETE CASCADE,
    
    -- Store Information
    store_name VARCHAR(50) NOT NULL, -- "Flipkart", "Amazon", "Croma", etc.
    store_product_id VARCHAR(255), -- Store's internal product ID
    
    -- Pricing Information
    price DECIMAL(10, 2) NOT NULL,
    original_price DECIMAL(10, 2), -- Before discount
    discount_percentage INTEGER, -- Calculated: ((original - price) / original) * 100
    
    -- Availability
    in_stock BOOLEAN DEFAULT true,
    stock_quantity INTEGER, -- If available from API
    
    -- URLs
    product_url TEXT NOT NULL, -- Affiliate URL
    image_url TEXT, -- Store-specific image (backup if global missing)
    
    -- Shipping
    shipping_cost DECIMAL(10, 2) DEFAULT 0.00,
    estimated_delivery_days INTEGER,
    
    -- Seller Information (for marketplaces like Amazon)
    seller_name VARCHAR(255),
    seller_rating DECIMAL(3, 2), -- 0.00 to 5.00
    
    -- Metadata
    last_scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_price_change_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Data Source
    source VARCHAR(50) DEFAULT 'manual', -- "api", "manual", "scraper"
    scraper_version VARCHAR(20),
    
    -- Analytics
    click_count INTEGER DEFAULT 0,
    conversion_count INTEGER DEFAULT 0
);

-- Indexes for Performance
CREATE INDEX idx_listings_global_product_id ON listings_scraped(global_product_id);
CREATE INDEX idx_listings_store_name ON listings_scraped(store_name);
CREATE INDEX idx_listings_price ON listings_scraped(price);
CREATE INDEX idx_listings_in_stock ON listings_scraped(in_stock);
CREATE INDEX idx_listings_last_scraped ON listings_scraped(last_scraped_at);

-- Composite Index for Common Query: "Get all listings for product X that are in stock"
CREATE INDEX idx_listings_product_stock ON listings_scraped(global_product_id, in_stock, price);

-- Unique Constraint: One product cannot have duplicate listings from same store
CREATE UNIQUE INDEX idx_unique_product_store ON listings_scraped(global_product_id, store_name, store_product_id);

-- ============================================================================
-- TABLE 3: price_history (Future Feature - Price Tracking)
-- Purpose: Track historical prices for price drop alerts
-- ============================================================================

CREATE TABLE IF NOT EXISTS price_history (
    history_id SERIAL PRIMARY KEY,
    listing_id INTEGER NOT NULL REFERENCES listings_scraped(listing_id) ON DELETE CASCADE,
    price DECIMAL(10, 2) NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Index for time-series queries
    INDEX idx_price_history_listing (listing_id, recorded_at)
);

-- ============================================================================
-- VIEW: products_with_best_price
-- Purpose: Quick access to products with their lowest available price
-- ============================================================================

CREATE OR REPLACE VIEW products_with_best_price AS
SELECT 
    p.global_product_id,
    p.name,
    p.brand,
    p.category,
    p.image_url,
    p.specifications,
    MIN(l.price) as best_price,
    COUNT(l.listing_id) as total_listings,
    COUNT(CASE WHEN l.in_stock THEN 1 END) as available_stores
FROM 
    products_global p
LEFT JOIN 
    listings_scraped l ON p.global_product_id = l.global_product_id
WHERE 
    l.in_stock = true
GROUP BY 
    p.global_product_id, p.name, p.brand, p.category, p.image_url, p.specifications;

-- ============================================================================
-- FUNCTION: get_product_with_listings
-- Purpose: Retrieve a product and all its store listings (for API responses)
-- ============================================================================

CREATE OR REPLACE FUNCTION get_product_with_listings(product_id UUID)
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'product', row_to_json(p.*),
        'listings', (
            SELECT json_agg(row_to_json(l.*))
            FROM listings_scraped l
            WHERE l.global_product_id = p.global_product_id
            AND l.in_stock = true
            ORDER BY l.price ASC
        )
    ) INTO result
    FROM products_global p
    WHERE p.global_product_id = product_id;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- FUNCTION: update_price_if_changed
-- Purpose: Update listing price and log to price_history if different
-- ============================================================================

CREATE OR REPLACE FUNCTION update_price_if_changed(
    p_listing_id INTEGER,
    p_new_price DECIMAL(10, 2)
)
RETURNS BOOLEAN AS $$
DECLARE
    old_price DECIMAL(10, 2);
    price_changed BOOLEAN := false;
BEGIN
    -- Get current price
    SELECT price INTO old_price
    FROM listings_scraped
    WHERE listing_id = p_listing_id;
    
    -- Check if price changed
    IF old_price IS NULL OR old_price != p_new_price THEN
        -- Update listing
        UPDATE listings_scraped
        SET 
            price = p_new_price,
            last_price_change_at = CURRENT_TIMESTAMP,
            last_scraped_at = CURRENT_TIMESTAMP
        WHERE listing_id = p_listing_id;
        
        -- Log to price history
        INSERT INTO price_history (listing_id, price)
        VALUES (p_listing_id, p_new_price);
        
        price_changed := true;
    ELSE
        -- Just update last_scraped_at
        UPDATE listings_scraped
        SET last_scraped_at = CURRENT_TIMESTAMP
        WHERE listing_id = p_listing_id;
    END IF;
    
    RETURN price_changed;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SAMPLE DATA INSERTION (for testing)
-- ============================================================================

-- Insert a sample product
INSERT INTO products_global (
    global_product_id,
    name,
    brand,
    category,
    description,
    specifications,
    image_url
) VALUES (
    '550e8400-e29b-41d4-a716-446655440000', -- Sample UUID
    'Apple MacBook Air M2',
    'Apple',
    'Laptop',
    'The new MacBook Air with M2 chip delivers incredible performance in a remarkably thin design.',
    '{"processor": "Apple M2", "ram": "8GB", "storage": "256GB SSD", "display": "13.6-inch Liquid Retina"}'::JSONB,
    'https://example.com/macbook-m2.jpg'
);

-- Insert multiple listings for the same product
INSERT INTO listings_scraped (
    global_product_id,
    store_name,
    store_product_id,
    price,
    original_price,
    in_stock,
    product_url
) VALUES 
(
    '550e8400-e29b-41d4-a716-446655440000',
    'Flipkart',
    'FLIP-MAC-M2-001',
    99990.00,
    109990.00,
    true,
    'https://flipkart.com/macbook-air-m2?affid=YOUR_ID'
),
(
    '550e8400-e29b-41d4-a716-446655440000',
    'Amazon',
    'B09V3GZD4K',
    98999.00,
    109990.00,
    true,
    'https://amazon.in/dp/B09V3GZD4K?tag=YOUR_TAG'
),
(
    '550e8400-e29b-41d4-a716-446655440000',
    'Croma',
    'CROMA-APPLE-M2-256',
    102000.00,
    109990.00,
    true,
    'https://croma.com/macbook-air-m2'
);

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check table structure
-- SELECT table_name, column_name, data_type 
-- FROM information_schema.columns 
-- WHERE table_schema = 'public' 
-- AND table_name IN ('products_global', 'listings_scraped')
-- ORDER BY table_name, ordinal_position;

-- Count products and listings
-- SELECT 
--     (SELECT COUNT(*) FROM products_global) as total_products,
--     (SELECT COUNT(*) FROM listings_scraped) as total_listings,
--     (SELECT COUNT(DISTINCT global_product_id) FROM listings_scraped) as products_with_listings;

-- Test the view
-- SELECT * FROM products_with_best_price LIMIT 5;

-- Test the function
-- SELECT get_product_with_listings('550e8400-e29b-41d4-a716-446655440000');

-- ============================================================================
-- NOTES FOR MIGRATION
-- ============================================================================

/*
1. This schema is designed for PostgreSQL 12+
2. Requires uuid-ossp extension for UUID generation (usually enabled by default)
3. All indexes are optimized for read-heavy workloads (typical for e-commerce)
4. Foreign key constraints ensure data integrity
5. JSONB columns allow flexible specification storage without schema changes
6. Views and functions simplify API queries

MIGRATION CHECKLIST:
☐ Run this script on development database first
☐ Verify sample data insertion works
☐ Test all indexes are created
☐ Verify foreign keys work
☐ Test view and function queries
☐ Run migrate_data.py to port existing data
☐ Rebuild vector index with new global_product_id keys
☐ Update API code to use new schema
☐ Test search performance
☐ Backup old table before dropping
*/
