"""FastAPI routes for HypeLens visual search (CLIP + optional web fallback)."""
from fastapi import APIRouter, UploadFile, File, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
import os
import traceback

from .pipeline import (
    find_similar_products,
    _load_model_once,
    _load_index_once,
    reset_index_cache,
    build_db_embeddings,
    build_faiss_index,
    web_visual_search,
)

router = APIRouter()

# Rebuild status (in-process)
_rebuild_status = {"running": False, "stage": None, "error": None}


@router.post("/search_by_image")
async def search_image(
    file: UploadFile = File(...),
    top_k: int = 10,
    category: str | None = Query(default=None),
    source: str = Query(default="auto", description="auto|local|web"),
):
    if not file:
        raise HTTPException(status_code=400, detail="No image file provided")
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty image file")
    if top_k < 1 or top_k > 50:
        raise HTTPException(status_code=400, detail="top_k must be between 1 and 50")

    if source == "local":
        result = find_similar_products(data, top_k=top_k, category=category)
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=f"Search failed: {result.get('error')}")
        return JSONResponse(content=result)
    elif source == "web":
        try:
            results = web_visual_search(data, top_k=top_k)
            return JSONResponse(content={
                "status": "success",
                "total_results": len(results),
                "results": results,
                "source": "web",
            })
        except Exception as e:
            return JSONResponse(content={"status": "error", "error": str(e), "results": []})
    else:
        result = find_similar_products(data, top_k=top_k, category=category)
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=f"Search failed: {result.get('error')}")
        if (result.get("status") == "success" and not result.get("results")) and os.getenv("ENABLE_WEB_FALLBACK") == "1":
            try:
                results = web_visual_search(data, top_k=top_k)
                return JSONResponse(content={
                    "status": "success",
                    "total_results": len(results),
                    "results": results,
                    "source": "web",
                })
            except Exception:
                pass
        return JSONResponse(content=result)


@router.get("/search_status")
async def search_status():
    try:
        _load_model_once()
        if not _rebuild_status["running"]:
            _load_index_once()
        artifacts = {
            "embeddings": os.path.exists(os.path.join("artifacts", "image_embeds.npy")),
            "id_map": os.path.exists(os.path.join("artifacts", "id_map.npy")),
            "index": os.path.exists(os.path.join("artifacts", "index.faiss")),
        }
        return {
            "status": "rebuilding" if _rebuild_status["running"] else "ready",
            "model": "ViT-B-32 (OpenAI)",
            "device": "CPU",
            "embedding_size": 512,
            "artifacts": artifacts,
            "rebuild": _rebuild_status,
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def _do_rebuild():
    try:
        _rebuild_status.update({"running": True, "stage": "encoding", "error": None})
        build_db_embeddings()
        _rebuild_status.update({"stage": "indexing"})
        build_faiss_index()
        reset_index_cache()
        _rebuild_status.update({"stage": "done", "running": False})
    except Exception as e:
        _rebuild_status.update({"stage": "error", "error": f"{e}\n{traceback.format_exc()}", "running": False})


@router.post("/rebuild")
async def rebuild(background_tasks: BackgroundTasks):
    if _rebuild_status["running"]:
        raise HTTPException(status_code=409, detail="Rebuild already in progress")
    os.makedirs("artifacts", exist_ok=True)
    background_tasks.add_task(_do_rebuild)
    return {"status": "started", "rebuild": _rebuild_status}
