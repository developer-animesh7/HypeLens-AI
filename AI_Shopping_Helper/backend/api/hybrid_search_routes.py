"""
FastAPI routes for Hybrid Search (CLIP + Keyword)
HypeLens v1.0 - Phase 2: Multi-Store Price Aggregation
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional
import os

from backend.ai.hybrid_search import search_and_save
from backend.ai.search_engine_singleton import get_search_engine

router = APIRouter()


@router.post("/hybrid_search")
async def hybrid_search_endpoint(
    file: UploadFile = File(...),
    query_text: Optional[str] = Query(default=None, description="Optional keyword query"),
    top_k: int = Query(default=10, ge=1, le=50),
    products_source: str = Query(default="db", description="db for PostgreSQL, json for products.json"),
):
    """
    HypeLens v1.0 Hybrid Search: CLIP + TF-IDF + Multi-Store Pricing
    
    PHASE 2 FEATURES:
    - Uses preloaded CLIP model (instant response!)
    - Queries new HypeLens schema (products_global + listings_scraped)
    - Returns multi-store pricing for exact matches
    - Separates exact matches from similar items
    
    Args:
        - **file**: Product image upload
        - **query_text**: Optional text query for keyword matching
        - **top_k**: Number of results (1-50)
        - **products_source**: "db" for PostgreSQL, "json" for products.json
    
    Returns:
        JSON with exact_match and similar_items sections
    """
    if not file:
        raise HTTPException(status_code=400, detail="No image file provided")
    
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read image bytes
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty image file")
    
    try:
        # PHASE 2 FIX: Use singleton engine (loads only once!)
        engine = get_search_engine()
        
        # Perform hybrid search and save to DB
        result = search_and_save(
            image_bytes=image_bytes,
            image_name=file.filename or "unknown.jpg",
            query_text=query_text,
            top_k=top_k,
            products_source=products_source,
            engine=engine  # Pass singleton engine!
        )
        
        return JSONResponse(content=result)
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Hybrid search failed: {str(e)}"
        )


@router.get("/search_history/{search_id}")
async def get_search_history(search_id: int):
    """
    Retrieve a previously saved search result by ID.
    
    - **search_id**: Database ID from clip_search_results table
    """
    from backend.database.db_connection import DatabaseConnection
    
    db = DatabaseConnection()
    
    query = """
    SELECT id, image_name, raw_json_result, created_at
    FROM public.clip_search_results
    WHERE id = :search_id
    """
    
    result = db.execute_query(query, {'search_id': search_id})
    
    if not result:
        raise HTTPException(status_code=404, detail="Search result not found")
    
    row = result[0]
    
    return JSONResponse(content={
        'search_id': row['id'],
        'image_name': row['image_name'],
        'created_at': str(row['created_at']),
        'results': row['raw_json_result']
    })


@router.get("/search_history")
async def list_search_history(limit: int = Query(default=20, ge=1, le=100)):
    """
    List recent search history.
    
    - **limit**: Number of records to return (1-100)
    """
    from backend.database.db_connection import DatabaseConnection
    
    db = DatabaseConnection()
    
    query = """
    SELECT id, image_name, created_at,
           jsonb_array_length(raw_json_result) as result_count
    FROM public.clip_search_results
    ORDER BY created_at DESC
    LIMIT :limit
    """
    
    results = db.execute_query(query, {'limit': limit})
    
    history = []
    for row in results:
        history.append({
            'search_id': row['id'],
            'image_name': row['image_name'],
            'created_at': str(row['created_at']),
            'result_count': row['result_count']
        })
    
    return JSONResponse(content={'total': len(history), 'searches': history})


@router.get("/download_export/{filename}")
async def download_export(filename: str):
    """
    Download exported JSON results for team testing.
    
    - **filename**: Name of the exported JSON file
    """
    export_dir = "search_results_export"
    filepath = os.path.join(export_dir, filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Export file not found")
    
    # Security: Prevent path traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    return FileResponse(
        path=filepath,
        media_type="application/json",
        filename=filename
    )


@router.get("/list_exports")
async def list_exports():
    """
    List all available JSON exports for download.
    """
    export_dir = "search_results_export"
    
    if not os.path.exists(export_dir):
        return JSONResponse(content={'total': 0, 'exports': []})
    
    files = []
    for filename in os.listdir(export_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(export_dir, filename)
            stat = os.stat(filepath)
            files.append({
                'filename': filename,
                'size_bytes': stat.st_size,
                'download_url': f'/api/hybrid/download_export/{filename}',
                'created': stat.st_ctime
            })
    
    # Sort by creation time (newest first)
    files.sort(key=lambda x: x['created'], reverse=True)
    
    return JSONResponse(content={'total': len(files), 'exports': files})
