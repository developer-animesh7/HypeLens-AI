# 🔄 HypeLens - Development Workflow

**Complete development and operational workflow**

---

## 🚀 Daily Startup Workflow

```
1. Double-click: start_hypelens.bat
   ↓
2. Wait 10 seconds (loading AI model)
   ↓
3. Open browser: http://localhost:3000
   ↓
4. Start using HypeLens!
```

**That's it! One click and you're ready.** ✅

---

## 🛑 Shutdown Workflow

```
Option 1: Double-click stop_hypelens.bat
Option 2: Close both terminal windows
Option 3: Press Ctrl+C in each terminal
```

---

## 🔍 Search Workflow (User Perspective)

```mermaid
User opens http://localhost:3000
    ↓
Choose search method:
  1. Search by URL → Enter product URL → Analyze
  2. Search by Image → Upload image → Search
    ↓
Wait 1-3 seconds
    ↓
View Results:
  - Exact Match (if found)
  - Similar Items
  - Multi-store prices
    ↓
Click "Buy Now" → Go to store
```

---

## ⚙️ Technical Search Workflow (Backend)

### **Image Search Process**

```
1. USER ACTION
   - Upload product image (JPG/PNG)
   - Click search button

2. FRONTEND (Next.js)
   - Create FormData with image
   - POST to /api/hybrid/hybrid_search
   - Show loading spinner

3. BACKEND API (FastAPI)
   - Receive image file
   - Validate file type and size
   - Call HybridSearchEngine

4. CLIP MODEL PROCESSING
   - Convert image to tensor
   - Generate 768-dim embedding
   - Normalize embedding vector

5. PRODUCT MATCHING
   a) Load products from cache (or DB)
   b) Load product embeddings (cached)
   c) Compute cosine similarity
   d) Rank by similarity score

6. KEYWORD SEARCH (if text provided)
   - Build TF-IDF index (cached)
   - Search product descriptions
   - Combine with visual scores

7. EXACT MATCH SCORING
   - Detect brand name
   - Detect model number
   - Boost exact matches (+30%)

8. MULTI-STORE PRICING
   - Query listings_scraped table
   - Get prices from all stores
   - Identify cheapest option

9. RESPONSE FORMATTING
   - Separate exact match
   - Rank similar items
   - Add store listings
   - Return JSON

10. FRONTEND RENDERING
    - Parse JSON response
    - Animate card entrance
    - Display with 3D effects
    - Show multi-store prices
```

**Total Time:** 1-3 seconds

---

## 💾 Data Flow Diagram

```
┌─────────────┐
│   Browser   │
│ (Port 3000) │
└──────┬──────┘
       │ HTTP POST /api/hybrid/hybrid_search
       │ (Image file + params)
       ↓
┌──────────────────┐
│   FastAPI Server │
│   (Port 8000)    │
└────────┬─────────┘
         │
         ↓
┌────────────────────────┐
│  Singleton Engine      │
│  (Loaded once in RAM)  │
│                        │
│  ┌──────────────────┐  │
│  │  CLIP ViT-L/14   │  │
│  │  (304M params)   │  │
│  └──────────────────┘  │
│                        │
│  ┌──────────────────┐  │
│  │ Embedding Cache  │  │
│  │ (363 products)   │  │
│  └──────────────────┘  │
│                        │
│  ┌──────────────────┐  │
│  │  TF-IDF Index    │  │
│  │  (Keyword search)│  │
│  └──────────────────┘  │
└────────┬───────────────┘
         │
         ↓
┌──────────────────┐
│   PostgreSQL     │
│  (Port 5432)     │
│                  │
│  products_global │
│  listings_scraped│
└────────┬─────────┘
         │
         ↓
┌──────────────────┐
│  JSON Response   │
│  (Results)       │
└────────┬─────────┘
         │
         ↓
┌─────────────┐
│   Browser   │
│  (Renders)  │
└─────────────┘
```

---

## 🔧 Development Workflow

### **Making Code Changes**

#### **Backend Changes (Python)**
```
1. Edit files in backend/
2. Save file
3. Backend auto-reloads (--reload flag)
4. Test immediately
```

#### **Frontend Changes (React/Next.js)**
```
1. Edit files in frontend-nextjs/src/
2. Save file
3. Frontend auto-compiles (Turbopack)
4. Browser auto-refreshes
5. See changes immediately
```

---

## 🐛 Debugging Workflow

### **Issue: Slow Search**
```
1. Check Terminal 1 (Backend)
   - Look for "Initializing..." message
   - Should only appear once at startup

2. Check cache status
   - First search: 2-3 seconds (normal)
   - Later searches: 1-2 seconds (normal)
   - If always slow: Restart backend

3. Verify singleton working
   - Should see: "HybridSearchEngine singleton ready!"
   - Only once per startup
```

### **Issue: No Results**
```
1. Check Terminal 1 for errors
2. Verify database connection
   - Run: python check_database_status.py

3. Check product count
   - Run: python count_products.py
   - Should show: 363 products

4. Test API directly
   - Go to: http://localhost:8000/docs
   - Try /api/hybrid/hybrid_search endpoint
```

### **Issue: Frontend Not Loading**
```
1. Check Terminal 2 (Frontend)
   - Look for compilation errors

2. Clear Next.js cache
   - Stop frontend (Ctrl+C)
   - Delete: frontend-nextjs/.next/
   - Restart: npm run dev

3. Reinstall dependencies
   - cd frontend-nextjs
   - rm -rf node_modules
   - npm install
```

---

## 🔄 Update Workflow

### **Adding New Products**
```
1. Prepare product data (JSON)
2. Run: python add_real_products.py
3. Verify: python count_products.py
4. Restart backend (to clear cache)
5. Test search with new products
```

### **Updating Database Schema**
```
1. Edit: migrations/schema_hypelens.sql
2. Backup database
3. Run migration script
4. Verify schema changes
5. Restart application
```

---

## 📊 Performance Monitoring Workflow

### **Check Search Performance**
```
1. Run: python test_optimized_performance.py
2. Expected results:
   - First search: 2-3 seconds
   - Second search: 1-2 seconds
   - Third search: 1-2 seconds

3. If slower:
   - Check CPU usage
   - Check RAM usage (8GB minimum)
   - Verify SSD/HDD speed
```

### **Monitor API Response Times**
```
1. Open: http://localhost:8000/docs
2. Use Swagger UI to test endpoints
3. Check response times
4. Expected: < 2 seconds per request
```

---

## 🧪 Testing Workflow

### **Manual Testing**
```
1. Start application
2. Upload test images:
   - MacBook image → Should find laptops
   - iPhone image → Should find phones
   - Shirt image → Should find clothing

3. Verify results:
   - Check similarity scores (> 0.7 for good matches)
   - Verify multi-store prices shown
   - Test "Clear image" button
   - Try different search sources (Auto/Local/Web)
```

### **Automated Testing**
```
1. Backend API tests:
   - python test_search_endpoint.py

2. Database tests:
   - python scripts/db_smoke_test.py

3. Performance tests:
   - python test_optimized_performance.py
```

---

## 🔐 Security Workflow

### **Before Deployment**
```
1. Change database password
2. Set up environment variables
3. Enable HTTPS
4. Add rate limiting
5. Implement authentication
6. Review CORS settings
```

---

## 📦 Backup Workflow

### **Regular Backups**
```
1. Database backup:
   pg_dump hypelens_db > backup_$(date +%Y%m%d).sql

2. Code backup:
   git commit -am "Backup"
   git push

3. Configuration backup:
   - Copy config/ folder
   - Save .env file (securely)
```

---

## 🚀 Deployment Workflow

### **Production Deployment**
```
1. Test locally thoroughly
2. Update requirements.txt
3. Build frontend:
   - cd frontend-nextjs
   - npm run build

4. Configure production settings:
   - Set environment variables
   - Update database credentials
   - Configure domain

5. Deploy backend:
   - Use gunicorn/uvicorn
   - Set up reverse proxy (nginx)

6. Deploy frontend:
   - Use Vercel or similar
   - Or serve with nginx

7. Monitor logs and performance
```

---

## 🎯 Common Tasks Quick Reference

| Task | Command/Action |
|------|----------------|
| Start app | `start_hypelens.bat` |
| Stop app | `stop_hypelens.bat` |
| Check products | `python count_products.py` |
| Test API | http://localhost:8000/docs |
| View frontend | http://localhost:3000 |
| Check backend logs | Terminal 1 output |
| Check frontend logs | Terminal 2 output |
| Clear cache | Restart backend |
| Update deps | `pip install -r requirements.txt` |
| Frontend deps | `cd frontend-nextjs && npm install` |

---

## ⚡ Performance Optimization Checklist

- ✅ Singleton pattern for CLIP model
- ✅ Embedding cache for products
- ✅ TF-IDF cache for keywords
- ✅ Product cache for database
- ✅ Optimized similarity search (argpartition)
- ✅ Lazy loading for frontend
- ✅ Image compression
- ✅ Database indexing

---

## 🎨 UI/UX Workflow

### **Design Changes**
```
1. Edit Tailwind classes in components
2. Save file
3. See changes instantly (hot reload)
4. Adjust animations in globals.css
5. Test on different screen sizes
```

### **Adding New Components**
```
1. Create file in frontend-nextjs/src/components/
2. Import in page.tsx
3. Add props and types
4. Style with Tailwind
5. Test functionality
```

---

**Last Updated:** October 24, 2025  
**Workflow Status:** Optimized & Production Ready ✅
