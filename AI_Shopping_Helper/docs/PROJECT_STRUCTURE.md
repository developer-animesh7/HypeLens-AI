# 📁 HypeLens - Project Structure

**Complete file and folder organization**

---

## 🗂️ Root Directory

```
AI_Shopping_Helper/
│
├── 🚀 start_hypelens.bat           # ONE-CLICK START
├── 🛑 stop_hypelens.bat            # ONE-CLICK STOP  
├── 📖 README.md                    # Complete documentation
├── 📋 PROJECT_STRUCTURE.md         # This file
├── 🔄 WORKFLOW.md                  # Development workflow
│
├── 📄 app.py                       # Main FastAPI application
├── 📄 requirements.txt             # Python dependencies
├── 📄 .gitignore                   # Git ignore rules
│
└── (Other files below...)
```

---

## 🐍 Backend Directory

```
backend/
│
├── __init__.py
│
├── ai/                             # AI & Machine Learning
│   ├── __init__.py
│   ├── hybrid_search.py           # Main search engine (CLIP + TF-IDF)
│   ├── search_engine_singleton.py # Singleton pattern for model
│   ├── exact_match_scorer.py      # Product matching logic
│   └── visual_search/             # CLIP model utilities
│       ├── __init__.py
│       └── api.py
│
├── api/                            # REST API Routes
│   ├── __init__.py
│   ├── routes.py                  # Main API routes
│   └── hybrid_search_routes.py    # Hybrid search endpoints
│
├── database/                       # Database Layer
│   ├── __init__.py
│   └── db_connection.py           # PostgreSQL connection
│
├── scraping/                       # Web Scraping
│   ├── __init__.py
│   └── (scraping modules)
│
└── utils/                          # Utility Functions
    ├── __init__.py
    └── (utility modules)
```

---

## ⚛️ Frontend Directory

```
frontend-nextjs/
│
├── 📄 package.json                 # Node.js dependencies
├── 📄 tsconfig.json                # TypeScript config
├── 📄 tailwind.config.ts           # Tailwind CSS config
├── 📄 next.config.ts               # Next.js config
├── 📄 postcss.config.mjs           # PostCSS config
├── 📄 eslint.config.mjs            # ESLint config
│
├── public/                         # Static files
│   └── (images, icons, etc.)
│
└── src/                            # Source code
    │
    ├── app/                        # Next.js App Router
    │   ├── layout.tsx              # Root layout
    │   ├── page.tsx                # Main page (search interface)
    │   └── globals.css             # Global styles + animations
    │
    ├── components/                 # React Components
    │   ├── ImageSearchUpload.tsx   # Image upload with preview
    │   ├── ImageSearchResults.tsx  # Search results display
    │   ├── ProductAnalyzer.tsx     # URL search component
    │   ├── ProductResults.tsx      # Product results
    │   ├── LoadingSpinner.tsx      # Loading animation
    │   └── ErrorMessage.tsx        # Error display
    │
    └── types/                      # TypeScript Types
        └── product.ts              # Product interface definitions
```

---

## 💾 Data Directory

```
data/
│
├── products.json                   # Fallback product database
└── chroma_db/                      # Vector database (if used)
    └── (vector embeddings)
```

---

## 🔄 Migrations Directory

```
migrations/
│
├── schema_hypelens.sql             # PostgreSQL schema
├── migrate_data.py                 # Data migration script
└── rebuild_index.py                # Rebuild search index
```

---

## 📊 Database Schema Files

```
scripts/
│
├── schema_postgres.sql             # Complete PostgreSQL schema
├── init_postgres_schema.py         # Schema initialization
├── data_collector.py               # Data collection utilities
└── db_smoke_test.py                # Database tests
```

---

## 🎨 Configuration

```
config/
│
└── settings.py                     # Application settings
```

---

## 📦 Python Virtual Environment

```
venv/                               # Python virtual environment
│
├── Scripts/                        # Executables
│   ├── python.exe                  # Python interpreter
│   ├── pip.exe                     # Package manager
│   └── activate.bat                # Activation script
│
└── Lib/                            # Python packages
    └── site-packages/              # Installed packages
        ├── fastapi/
        ├── open_clip/
        ├── torch/
        └── (other packages...)
```

---

## 📂 Utility Scripts (Root Level)

```
Root Scripts:
│
├── add_real_products.py            # Add products to database
├── add_real_flipkart_urls.py       # Add Flipkart URLs
├── add_big_database.py             # Bulk data import
├── scrape_flipkart_products.py     # Web scraping
├── count_products.py               # Count database entries
├── check_database_status.py        # Database health check
├── test_database_query.py          # Test queries
├── test_search_endpoint.py         # API testing
├── test_optimized_performance.py   # Performance testing
└── web_fallback_and_export.py      # Export utilities
```

---

## 🗄️ Database Backups

```
Root Backups:
│
├── backup_20251024_204605.sql      # Database backup
└── backup_20251024_204639.sql      # Database backup
```

---

## 📤 Search Results Export

```
search_results_export/
│
└── search_*.json                   # Exported search results
```

---

## 🖼️ Images/Assets

```
images/                             # Project images
│
└── (product images, logos, etc.)
```

---

## 🚫 Files to Ignore

```
__pycache__/                        # Python cache (auto-generated)
node_modules/                       # Node.js packages (auto-generated)
.next/                              # Next.js build (auto-generated)
*.pyc                               # Python compiled files
.env                                # Environment variables (sensitive)
```

---

## 📝 Important Files Only

### **Essential Files:**
1. `README.md` - Complete documentation
2. `PROJECT_STRUCTURE.md` - This file
3. `WORKFLOW.md` - Development workflow
4. `start_hypelens.bat` - Startup script
5. `stop_hypelens.bat` - Stop script
6. `app.py` - Main application
7. `requirements.txt` - Dependencies

### **Configuration Files:**
- `tailwind.config.ts` - UI styling
- `tsconfig.json` - TypeScript setup
- `next.config.ts` - Next.js setup
- `package.json` - Node dependencies

### **Core Code:**
- `backend/ai/hybrid_search.py` - Search engine
- `backend/api/hybrid_search_routes.py` - API
- `frontend-nextjs/src/app/page.tsx` - Main UI
- `frontend-nextjs/src/components/*.tsx` - UI components

---

## 📏 Directory Sizes (Approximate)

| Directory | Size | Description |
|-----------|------|-------------|
| `venv/` | 2-3 GB | Python packages |
| `frontend-nextjs/node_modules/` | 500 MB | Node packages |
| `backend/` | 5 MB | Python code |
| `frontend-nextjs/src/` | 2 MB | React code |
| `data/` | 1 MB | Product data |
| Total (excluding venv) | ~510 MB | Working code |

---

## 🎯 File Count Summary

- **Python Files:** ~50
- **TypeScript/React Files:** ~15
- **Configuration Files:** ~10
- **Documentation Files:** 3 (essential)
- **Batch Scripts:** 2
- **SQL Files:** 3

---

## 🔍 Quick File Finder

**Need to find a file? Use this guide:**

| What You Need | File Location |
|---------------|---------------|
| Start app | `start_hypelens.bat` |
| Stop app | `stop_hypelens.bat` |
| Main docs | `README.md` |
| Search engine | `backend/ai/hybrid_search.py` |
| Main UI | `frontend-nextjs/src/app/page.tsx` |
| API routes | `backend/api/hybrid_search_routes.py` |
| Database schema | `migrations/schema_hypelens.sql` |
| Styling | `frontend-nextjs/src/app/globals.css` |
| Components | `frontend-nextjs/src/components/` |

---

**Last Updated:** October 24, 2025  
**Total Files:** ~500 (including dependencies)  
**Core Project Files:** ~80
