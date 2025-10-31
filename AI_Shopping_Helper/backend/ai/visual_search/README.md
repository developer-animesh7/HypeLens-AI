# HypeLens Visual Search (Member 1)

Owner: Image → Embedding → FAISS (CLIP pipeline)

What’s here:
- API routes: `backend/ai/visual_search/api.py` (mounted at `/api/clip`)
- Pipeline: `backend/ai/visual_search/pipeline.py` (model load, search, build helpers)
- Optional web fallback: `backend/ai/visual_search/web.py` (Bing Visual Search)

Endpoints:
- POST `/api/clip/search_by_image` — image upload → results
  - params: `top_k`, `category`, `source=auto|local|web`
- GET `/api/clip/search_status` — readiness, artifacts, rebuild state
- POST `/api/clip/rebuild` — background rebuild of embeddings + FAISS

Artifacts:
- `artifacts/image_embeds.npy`, `artifacts/id_map.npy`, `artifacts/index.faiss`

Env flags:
- `DATABASE_PATH` — path to real SQLite file (or adapt DB connector)
- `CLIP_MIN_SCORE`, `CLIP_OVERSAMPLE`, `CLIP_BUILD_BATCH`, `CLIP_CACHE_IMAGES`
- `ENABLE_WEB_FALLBACK=1`, `BING_API_KEY` for web search

Rebuild from DB:
- `python run_project.py --rebuild-clip`

Notes:
- This module is the single source of truth for visual search. Other teams should only integrate via the routes and artifacts documented above.