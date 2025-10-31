# 🚀 Phase 4: Automation Engine - Setup Guide

**HypeLens Data Pipeline - Automated Product Ingestion at Scale**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Getting API Keys](#getting-api-keys)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Usage Examples](#usage-examples)
7. [Scheduling & Automation](#scheduling--automation)
8. [Monitoring](#monitoring)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

Phase 4 creates the **Automation Engine** that automatically:

- ✅ Fetches products from Flipkart/Amazon/Myntra APIs
- ✅ Generates CLIP ViT-L/14 embeddings (768-dimensional vectors)
- ✅ Adds new products to `products_global` table
- ✅ Updates prices in `listings_scraped` table
- ✅ Maintains vector index for instant search
- ✅ Handles millions of products efficiently

**This is the SCALER that makes HypeLens production-ready!**

---

## 📦 Prerequisites

### Python Dependencies

```bash
# Already installed (from requirements.txt):
- sqlalchemy
- psycopg2-binary
- pillow
- requests
- torch
- open_clip_torch
```

### Database Schema

Ensure your database has these tables (already created):

```sql
-- products_global: Global product catalog
CREATE TABLE products_global (
    global_product_id UUID PRIMARY KEY,
    product_name VARCHAR(500),
    brand VARCHAR(200),
    category VARCHAR(100),
    primary_image_url TEXT,
    description TEXT,
    embedding_vector FLOAT[],  -- 768-dim CLIP embedding
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- listings_scraped: Store-specific listings
CREATE TABLE listings_scraped (
    listing_id SERIAL PRIMARY KEY,
    global_product_id UUID REFERENCES products_global(global_product_id),
    store_name VARCHAR(100),  -- 'flipkart', 'amazon', 'myntra'
    external_product_id VARCHAR(200),
    price DECIMAL(10, 2),
    product_url TEXT,
    availability VARCHAR(50),
    last_scraped TIMESTAMP
);
```

✅ **You already have this schema!**

---

## 🔑 Getting API Keys

### 1. Flipkart Affiliate API

**Steps:**

1. Visit: https://affiliate.flipkart.com/
2. Sign up for Flipkart Affiliate Program
3. Go to **API** section in dashboard
4. Generate **Affiliate ID** and **Affiliate Token**
5. Copy credentials to `config/pipeline_config.env`

**Access Level:**
- Free tier: 500 requests/hour
- Paid tier: Unlimited requests

**API Documentation:**
- https://affiliate.flipkart.com/api-docs

### 2. Amazon Product Advertising API (PA-API 5.0)

**Steps:**

1. Visit: https://affiliate.amazon.in/
2. Sign up for Amazon Associates Program
3. Get approved (usually takes 1-3 days)
4. Go to **Product Advertising API** section
5. Generate **Access Key**, **Secret Key**, and **Partner Tag**
6. Copy credentials to `config/pipeline_config.env`

**Requirements:**
- Need 3 sales within 180 days to maintain API access
- Free tier: 8,640 requests/day (10/hour)
- Paid tier: Up to 864,000 requests/day

**API Documentation:**
- https://webservices.amazon.com/paapi5/documentation/

### 3. Myntra API

**Status:** ❌ No Public API Available

**Alternative:** Use web scraping (already implemented in `backend/scraping/product_scraper.py`)

---

## 🛠️ Installation

### Step 1: Update Configuration

```bash
cd "C:\AI Finder App SU\AI_Shopping_Helper"

# Edit config file
notepad config\pipeline_config.env
```

**Add your API keys:**

```env
# Flipkart
FLIPKART_AFFILIATE_ID=your_actual_affiliate_id
FLIPKART_AFFILIATE_TOKEN=your_actual_token

# Amazon
AMAZON_ACCESS_KEY=your_access_key
AMAZON_SECRET_KEY=your_secret_key
AMAZON_PARTNER_TAG=your_partner_tag
```

### Step 2: Verify Dependencies

```powershell
# Check if all packages are installed
.\venv\Scripts\python.exe -c "import torch, open_clip, PIL, requests, sqlalchemy; print('✓ All dependencies installed')"
```

### Step 3: Test Database Connection

```powershell
# Run database smoke test
.\venv\Scripts\python.exe scripts\db_smoke_test.py
```

---

## ⚙️ Configuration

### Environment Variables

The pipeline reads from `config/pipeline_config.env`:

```env
# API Keys
FLIPKART_AFFILIATE_ID=your_id
FLIPKART_AFFILIATE_TOKEN=your_token

# Pipeline Settings
PIPELINE_BATCH_SIZE=100          # Process 100 products at a time
PIPELINE_MAX_RETRIES=3           # Retry failed API calls 3 times
PIPELINE_TIMEOUT_SECONDS=30      # Timeout for API requests

# Logging
LOG_LEVEL=INFO                   # DEBUG, INFO, WARNING, ERROR
LOG_FILE=data_pipeline.log       # Log file location
```

### Command-Line Options

```bash
python data_pipeline.py --help
```

**Available options:**

```
--platform         Platform to fetch from (flipkart, amazon, myntra, all)
--category         Product category (laptops, smartphones, clothing, all)
--limit            Maximum products to fetch (default: 1000)
--all-platforms    Fetch from all available platforms
--continuous       Run every 6 hours (daemon mode)
--flipkart-key     Flipkart Affiliate ID
--flipkart-token   Flipkart Affiliate Token
--amazon-key       Amazon Access Key
--amazon-secret    Amazon Secret Key
```

---

## 📖 Usage Examples

### Example 1: Fetch 1000 Laptops from Flipkart

```powershell
.\venv\Scripts\python.exe data_pipeline.py `
  --platform flipkart `
  --category laptops `
  --limit 1000 `
  --flipkart-key "YOUR_KEY" `
  --flipkart-token "YOUR_TOKEN"
```

**Output:**
```
======================================================================
🚀 HypeLens Data Pipeline - Phase 4: Automation Engine
======================================================================
Platform: flipkart
Category: laptops
Limit: 1000
----------------------------------------------------------------------

📦 Processing FLIPKART products...
✓ Fetched 1000 products from Flipkart (laptops)
   🆕 New product: Dell Inspiron 15 Intel Core i5...
   ✓ Created global product: 3fa85f64-5717-4562-b3fc-2c963f66afa6
   ✓ Inserted listing for Dell Inspiron 15...
   Progress: 100/1000 products processed...
   Progress: 200/1000 products processed...
   ...

======================================================================
📊 PIPELINE STATISTICS
======================================================================
Total products fetched:     1000
New global products:        847
Embeddings generated:       847
Listings updated/created:   1000
Errors:                     12
Skipped:                    3
----------------------------------------------------------------------
Time elapsed:               245.67 seconds
Products per second:        4.07
======================================================================
```

### Example 2: Fetch All Categories from Amazon

```powershell
.\venv\Scripts\python.exe data_pipeline.py `
  --platform amazon `
  --category all `
  --limit 5000 `
  --amazon-key "YOUR_ACCESS_KEY" `
  --amazon-secret "YOUR_SECRET_KEY"
```

### Example 3: Fetch from All Platforms

```powershell
.\venv\Scripts\python.exe data_pipeline.py `
  --all-platforms `
  --category smartphones `
  --limit 2000
```

### Example 4: Continuous Mode (Daemon)

```powershell
# Runs every 6 hours automatically
.\venv\Scripts\python.exe data_pipeline.py `
  --platform flipkart `
  --category all `
  --continuous
```

**Use Case:** Keep your database updated with latest prices and products automatically.

---

## ⏰ Scheduling & Automation

### Option 1: Windows Task Scheduler

**Create a scheduled task:**

1. Open **Task Scheduler**
2. Click **Create Basic Task**
3. Name: "HypeLens Data Pipeline"
4. Trigger: **Daily** at **3:00 AM**
5. Action: **Start a program**
   - Program: `C:\AI Finder App SU\AI_Shopping_Helper\venv\Scripts\python.exe`
   - Arguments: `data_pipeline.py --platform all --category all --limit 5000`
   - Start in: `C:\AI Finder App SU\AI_Shopping_Helper`

### Option 2: PowerShell Script

**Create `run_pipeline_scheduled.ps1`:**

```powershell
# Run every 6 hours
while ($true) {
    Write-Host "🚀 Starting HypeLens Data Pipeline..." -ForegroundColor Cyan
    
    & ".\venv\Scripts\python.exe" data_pipeline.py `
        --platform flipkart `
        --category all `
        --limit 5000
    
    Write-Host "✓ Pipeline complete. Sleeping for 6 hours..." -ForegroundColor Green
    Start-Sleep -Seconds (6 * 3600)
}
```

**Run in background:**

```powershell
Start-Job -Name "HypeLens_Pipeline" -ScriptBlock {
    Set-Location "C:\AI Finder App SU\AI_Shopping_Helper"
    & .\run_pipeline_scheduled.ps1
}
```

### Option 3: Cron Job (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Run every 6 hours
0 */6 * * * cd /path/to/AI_Shopping_Helper && ./venv/bin/python data_pipeline.py --platform all --category all --limit 5000
```

---

## 📊 Monitoring

### Check Pipeline Logs

```powershell
# View latest log
Get-Content data_pipeline_*.log -Tail 50
```

### Check Database Status

```powershell
# Run database smoke test
.\venv\Scripts\python.exe scripts\db_smoke_test.py

# Count products
.\venv\Scripts\python.exe count_products.py
```

### Check Product Statistics

```sql
-- Total products
SELECT COUNT(*) FROM products_global;

-- Products per platform
SELECT store_name, COUNT(*) 
FROM listings_scraped 
GROUP BY store_name;

-- Products per category
SELECT category, COUNT(*) 
FROM products_global 
GROUP BY category
ORDER BY COUNT(*) DESC;

-- Average price per category
SELECT 
    pg.category,
    AVG(ls.price) as avg_price,
    MIN(ls.price) as min_price,
    MAX(ls.price) as max_price
FROM products_global pg
JOIN listings_scraped ls ON pg.global_product_id = ls.global_product_id
GROUP BY pg.category;
```

---

## 🐛 Troubleshooting

### Issue 1: API Authentication Failed

**Error:**
```
✗ Flipkart API error: 401 Unauthorized
```

**Solution:**
- Verify API keys in `config/pipeline_config.env`
- Check if Affiliate ID and Token are correct
- Ensure you're approved in Flipkart Affiliate Program

### Issue 2: Slow Embedding Generation

**Error:**
```
Products per second: 0.5 (very slow)
```

**Solution:**
- Check if CLIP model is loaded correctly
- Verify GPU availability: `torch.cuda.is_available()`
- Reduce batch size: `--limit 100`
- Use smaller images (model auto-resizes to 224x224)

### Issue 3: Database Connection Timeout

**Error:**
```
sqlalchemy.exc.OperationalError: connection timeout
```

**Solution:**
- Check PostgreSQL is running
- Verify database credentials in `.env`
- Test connection: `python scripts/db_smoke_test.py`

### Issue 4: Image Download Failed

**Error:**
```
⚠ Image download failed: Connection timeout
```

**Solution:**
- Check internet connection
- Verify image URLs are accessible
- Increase timeout: `PIPELINE_TIMEOUT_SECONDS=60`

### Issue 5: Duplicate Products

**Error:**
```
Multiple products with same external_id
```

**Solution:**
- Pipeline automatically deduplicates by external_id + platform
- Check `listings_scraped` for duplicates
- Run cleanup query:
```sql
DELETE FROM listings_scraped 
WHERE listing_id NOT IN (
    SELECT MIN(listing_id) 
    FROM listings_scraped 
    GROUP BY global_product_id, store_name
);
```

---

## 🎯 Performance Optimization

### 1. Batch Processing

```python
# Process products in batches of 100
pipeline.run(platform='flipkart', category='all', limit=100)
```

### 2. Parallel Processing

```python
# Run multiple categories in parallel
from concurrent.futures import ThreadPoolExecutor

categories = ['laptops', 'smartphones', 'clothing', 'footwear']

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(pipeline.run, 'flipkart', cat, 1000)
        for cat in categories
    ]
```

### 3. GPU Acceleration

```python
# Verify GPU is being used
import torch
print(f"GPU Available: {torch.cuda.is_available()}")
print(f"Device: {torch.cuda.get_device_name(0)}")
```

### 4. Database Indexing

```sql
-- Add indexes for faster queries
CREATE INDEX idx_listings_global_id ON listings_scraped(global_product_id);
CREATE INDEX idx_listings_store ON listings_scraped(store_name);
CREATE INDEX idx_products_category ON products_global(category);
```

---

## 📈 Scaling to Millions of Products

### Current Capacity (Local Machine)

- **Products per hour:** ~1,000 - 5,000
- **Daily capacity:** ~24,000 - 120,000 products
- **Monthly capacity:** ~720,000 - 3,600,000 products

### Scaling Strategies

**1. Increase Frequency:**
- Run every 1 hour instead of 6 hours
- Monthly capacity: 2-3 million products

**2. Multiple Platforms:**
- Run Flipkart, Amazon, Myntra in parallel
- 3× capacity: 6-10 million products/month

**3. Cloud Deployment:**
- Deploy on AWS/Azure/GCP
- Use larger instances (more RAM/CPU)
- 10× capacity: 20-30 million products/month

**4. Distributed Processing:**
- Use Celery + Redis for task queue
- Multiple workers processing in parallel
- 50-100× capacity: 100+ million products/month

---

## ✅ Phase 4 Checklist

- [ ] Get Flipkart Affiliate API keys
- [ ] Get Amazon Product Advertising API keys  
- [ ] Configure `config/pipeline_config.env`
- [ ] Test with small dataset (--limit 10)
- [ ] Run full pipeline (--limit 1000)
- [ ] Set up Windows Task Scheduler / Cron Job
- [ ] Monitor logs and database growth
- [ ] Optimize for your use case

---

## 🎉 You're Ready to Scale!

Your HypeLens app can now:

1. ✅ Accept image uploads from users
2. ✅ Search 363+ products locally (Phase 1-3)
3. ✅ **Automatically add millions of products (Phase 4)** 🚀
4. ✅ Find best prices across multiple stores
5. ✅ Scale to production levels

**Next Steps:**
- Start with Flipkart API (easiest to get)
- Run pipeline daily to keep database fresh
- Monitor performance and optimize
- Deploy to cloud for 24/7 operation

---

**Questions? Check `README.md` or run:**
```bash
python data_pipeline.py --help
```
