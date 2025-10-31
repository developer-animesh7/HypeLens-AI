# 🚀 How to Use the REAL Flipkart API

## ✅ You Now Have TWO Automation Tools:

### 1. **data_pipeline_real_api.py** (NEW - Uses Real Flipkart API)
   - ✅ Fetches products from actual Flipkart Affiliate API
   - ✅ Supports all Flipkart categories
   - ✅ Generates AI embeddings for visual search
   - ❌ Requires Flipkart Affiliate approval (can take 2-3 days)

### 2. **scrape_flipkart_products.py** (Existing - Works Now!)
   - ✅ Works immediately, no API keys needed
   - ✅ Scrapes Flipkart website directly
   - ✅ Adds products to your database
   - ⚠️ Limited to public product pages

---

## 🎯 Quick Start (Use Real API)

### Step 1: Get Flipkart Affiliate API Keys

1. **Sign Up for Flipkart Affiliate Program**
   - Go to: https://affiliate.flipkart.com/
   - Click "Register" and create account
   - Fill in your details (website/app info)
   - **Approval takes 2-3 business days**

2. **Generate API Credentials**
   - After approval, login to dashboard
   - Go to: **API** section → **Get API Credentials**
   - You'll see:
     - **Affiliate ID** (Tracking ID) - Example: `vijay80gm`
     - **Affiliate Token** - Example: `abc123xyz456...`
   - Copy both values

3. **Add to Configuration**
   ```bash
   # Edit config/pipeline_config.env
   notepad config\pipeline_config.env
   
   # Replace:
   FLIPKART_AFFILIATE_ID=vijay80gm  # Your actual ID
   FLIPKART_AFFILIATE_TOKEN=abc123xyz456...  # Your actual token
   ```

### Step 2: Test the API

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# List all available categories
python data_pipeline_real_api.py --list-categories

# Example output:
# 📂 Available Flipkart Categories:
# ======================================================================
#   tyy             → Mobiles
#   4io             → Laptops
#   6bo             → Tablets
#   czl             → Televisions
#   reh             → Bags & Wallets
#   ...
```

### Step 3: Fetch Real Products

```bash
# Fetch 100 mobiles from Flipkart
python data_pipeline_real_api.py --category tyy --limit 100

# Fetch 500 laptops
python data_pipeline_real_api.py --category 4io --limit 500

# Search for specific products
python data_pipeline_real_api.py --search "macbook" --limit 10

# Continuous mode (runs every 6 hours)
python data_pipeline_real_api.py --category tyy --limit 1000 --continuous
```

### Step 4: Verify in Database

```bash
# Check database after fetching
python check_database_products.py

# Expected output:
# ✅ Total Products: 600  (Your existing 370 + 100 new from API + 130 more)
# ✅ Total Listings: 600
#
# 📦 Products by Store:
#    Flipkart        → 600 products  ← New products from real API!
```

---

## 📚 Flipkart API Categories (Most Popular)

| Category Code | Name | Example Use |
|---------------|------|-------------|
| `tyy` | Mobiles & Accessories | `--category tyy --limit 500` |
| `4io` | Laptops | `--category 4io --limit 300` |
| `6bo` | Tablets | `--category 6bo --limit 100` |
| `czl` | Televisions | `--category czl --limit 200` |
| `reh` | Bags & Wallets | `--category reh --limit 500` |
| `osp` | Footwear | `--category osp --limit 1000` |
| `clo` | Clothing | `--category clo --limit 2000` |
| `t4f` | Home & Kitchen | `--category t4f --limit 500` |
| `7jv` | Food & Nutrition | `--category 7jv --limit 300` |

**Get full list:**
```bash
python data_pipeline_real_api.py --list-categories
```

---

## 🔥 Real-World Usage Examples

### Example 1: Daily Laptop Price Updates
```bash
# Schedule this in Windows Task Scheduler (runs daily at 3 AM)
python data_pipeline_real_api.py --category 4io --limit 1000
```

### Example 2: Multi-Category Product Sync
```bash
# Fetch products from multiple categories (run as batch script)
python data_pipeline_real_api.py --category tyy --limit 500  # Mobiles
python data_pipeline_real_api.py --category 4io --limit 300  # Laptops
python data_pipeline_real_api.py --category czl --limit 200  # TVs
```

### Example 3: Search-Based Product Discovery
```bash
# Find specific products by keyword
python data_pipeline_real_api.py --search "iphone 15" --limit 10
python data_pipeline_real_api.py --search "macbook pro" --limit 10
python data_pipeline_real_api.py --search "nike shoes" --limit 50
```

### Example 4: Continuous Background Sync
```bash
# Run continuously (updates every 6 hours automatically)
python data_pipeline_real_api.py --category tyy --limit 2000 --continuous
```

---

## 🆚 When to Use Which Tool?

### Use **data_pipeline_real_api.py** (Real API) When:
- ✅ You have Flipkart Affiliate approval
- ✅ Need large-scale product data (thousands of products)
- ✅ Want automatic price updates
- ✅ Need complete product metadata (specs, ratings, etc.)
- ✅ Building production system

### Use **scrape_flipkart_products.py** (Web Scraper) When:
- ✅ Testing without API keys
- ✅ Need quick product data immediately
- ✅ Fetching small number of products (< 200)
- ✅ Development/prototyping phase

---

## 🚨 Common Issues & Solutions

### Issue 1: "Missing API credentials!"
**Solution:**
```bash
# Make sure you added your keys to config/pipeline_config.env
notepad config\pipeline_config.env

# Should look like:
FLIPKART_AFFILIATE_ID=your_actual_id
FLIPKART_AFFILIATE_TOKEN=your_actual_token
```

### Issue 2: "Category 'xyz' not found!"
**Solution:**
```bash
# List all valid categories first
python data_pipeline_real_api.py --list-categories

# Use exact category code from the list
python data_pipeline_real_api.py --category tyy --limit 100
```

### Issue 3: API returns empty results
**Possible Reasons:**
- Category has no products
- API rate limit exceeded (wait 1 hour)
- Invalid affiliate credentials
- URL expired (URLs valid for 10 hours only)

**Solution:**
```bash
# Try a popular category first
python data_pipeline_real_api.py --category tyy --limit 10

# Check logs for detailed error messages
```

### Issue 4: "Failed to generate embedding"
**This is normal!** Some product images may:
- Not load properly
- Be invalid URLs
- Be blocked by Flipkart

**Solution:** The pipeline continues processing other products. Check logs for success rate.

---

## 📊 API Limits & Best Practices

### Flipkart API Rate Limits
- **Free Tier**: ~500 requests/hour
- **Batch Size**: 500 products per API call
- **URL Expiry**: 10 hours

### Best Practices
1. **Start Small**: Test with `--limit 10` first
2. **Respect Rate Limits**: Don't hammer the API (built-in 0.5s delay)
3. **Use Continuous Mode**: For automated updates (runs every 6 hours)
4. **Monitor Logs**: Check log files for errors
5. **Verify Results**: Use `check_database_products.py` after each run

### Recommended Update Frequency
- **Electronics**: Every 6 hours (prices change frequently)
- **Fashion**: Twice daily (3 AM, 3 PM)
- **Books**: Once daily
- **Furniture**: Weekly

---

## 🎓 Advanced: API Response Format

### Product Structure (v1.1.0)
```json
{
  "productBaseInfoV1": {
    "productId": "MOBXYZ123",
    "title": "Samsung Galaxy S24 5G (256GB, Black)",
    "productBrand": "Samsung",
    "flipkartSpecialPrice": {"amount": 74999, "currency": "INR"},
    "maximumRetailPrice": {"amount": 84999, "currency": "INR"},
    "discountPercentage": 11.76,
    "imageUrls": {"800x800": "https://...", "400x400": "https://..."},
    "productUrl": "https://dl.flipkart.com/...",
    "inStock": true,
    "categoryPath": "[[{\"node_name\":\"Mobiles\"}]]"
  },
  "productShippingInfoV1": {
    "shippingCharges": {"amount": 0, "currency": "INR"},
    "sellerName": "RetailNet",
    "sellerAverageRating": 4.3
  }
}
```

Our pipeline automatically:
1. Extracts relevant fields
2. Normalizes data format
3. Generates AI embeddings
4. Stores in database
5. Updates ChromaDB vector index

---

## 📈 Scaling to Millions of Products

### Phase 1: Start Small (Your Current State)
```bash
# Fetch 100-500 products per category
python data_pipeline_real_api.py --category tyy --limit 500
```
**Result**: ~500 products, takes 2-3 minutes

### Phase 2: Scale to Thousands
```bash
# Fetch multiple categories in parallel (run in separate terminals)
# Terminal 1:
python data_pipeline_real_api.py --category tyy --limit 5000  # Mobiles

# Terminal 2:
python data_pipeline_real_api.py --category 4io --limit 3000  # Laptops

# Terminal 3:
python data_pipeline_real_api.py --category czl --limit 2000  # TVs
```
**Result**: ~10,000 products, takes 30-40 minutes

### Phase 3: Automate Everything
```bash
# Create Windows Task Scheduler task
# Task 1: Daily at 3 AM
python data_pipeline_real_api.py --category tyy --limit 10000

# Task 2: Daily at 6 AM
python data_pipeline_real_api.py --category 4io --limit 5000
```
**Result**: 15,000 new products daily automatically

### Phase 4: Scale to Millions (Production)
- Use cloud servers (AWS/Azure)
- Multiple affiliate accounts (scale API limits)
- Distributed processing (multiple workers)
- Database sharding (split by category)

**Capacity**: 100,000+ products/day

---

## 🎉 Success Checklist

- [ ] Got Flipkart Affiliate approval
- [ ] Added API keys to config file
- [ ] Listed categories successfully
- [ ] Fetched 10 test products
- [ ] Verified products in database
- [ ] Scaled to 100+ products
- [ ] Set up automated scheduling

---

## 📞 Need Help?

1. **Check Logs**: Look at `data_pipeline_YYYYMMDD_HHMMSS.log`
2. **Test API**: Run `--list-categories` to verify credentials
3. **Start Small**: Always test with `--limit 10` first
4. **Verify Database**: Use `check_database_products.py` after each run

**Happy Automating! 🚀**
