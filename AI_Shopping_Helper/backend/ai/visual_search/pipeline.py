"""Pipeline utilities for CLIP visual search (moved from src/clip_pipeline)."""
from __future__ import annotations
import os
from io import BytesIO
from typing import List, Dict, Any, Optional

import numpy as np
import faiss  # type: ignore
from PIL import Image
import torch
import open_clip

# Config
INDEX_PATH = os.getenv("CLIP_FAISS_INDEX", os.path.join("artifacts", "index.faiss"))
IDMAP_PATH = os.getenv("CLIP_ID_MAP", os.path.join("artifacts", "id_map.npy"))
MIN_SCORE = os.getenv("CLIP_MIN_SCORE")
from backend.database.db_connection import DatabaseConnection

# UPGRADED: ViT-L/14 for maximum accuracy (304M params, 768-dim embeddings)
MODEL_NAME = "ViT-L-14"
PRETRAINED = "openai"

_device = torch.device("cpu")
_model = None
_preprocess = None
_index = None
_idmap = None


def _load_model_once():
    global _model, _preprocess
    if _model is None or _preprocess is None:
        model, _, preprocess = open_clip.create_model_and_transforms(MODEL_NAME, pretrained=PRETRAINED, device=_device)
        model.eval()
        _model, _preprocess = model, preprocess


def _load_index_once():
    global _index, _idmap
    if _index is None:
        if not os.path.exists(INDEX_PATH) or not os.path.exists(IDMAP_PATH):
            raise RuntimeError("CLIP index or id_map not found. Build artifacts first.")
        _index = faiss.read_index(INDEX_PATH)
        _idmap = np.load(IDMAP_PATH, allow_pickle=True)


def reset_index_cache() -> None:
    global _index, _idmap
    _index = None
    _idmap = None


def get_embedding(image_bytes: bytes) -> np.ndarray:
    _load_model_once()
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    image_tensor = _preprocess(image).unsqueeze(0).to(_device)
    with torch.no_grad():
        image_features = _model.encode_image(image_tensor)
        normalized = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
    return normalized.cpu().numpy().astype("float32")


def search_similar(embedding: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
    _load_index_once()
    distances, indices = _index.search(embedding, k)
    results: List[Dict[str, Any]] = []
    min_score_val: float | None = None
    if MIN_SCORE:
        try:
            min_score_val = float(MIN_SCORE)
        except ValueError:
            min_score_val = None
    for score, idx in zip(distances[0], indices[0]):
        if idx == -1 or idx >= len(_idmap):
            continue
        pid = int(_idmap[idx])
        if min_score_val is not None and score < min_score_val:
            continue
        results.append({"product_id": pid, "score": float(score)})
    return results


def fetch_products(product_ids: List[int]) -> List[Dict[str, Any]]:
    if not product_ids:
        return []
    # Use unified DB connector (works for PostgreSQL and SQLite)
    try:
        db = DatabaseConnection()
        # SQLAlchemy will handle param styles; use named params for portability
        placeholders = ", ".join([f":id{i}" for i in range(len(product_ids))])
        params = {f"id{i}": pid for i, pid in enumerate(product_ids)}
        query = f"""
        SELECT id, name, category, price, platform, url,
               specs, image_url, description, created_at, updated_at
        FROM products
        WHERE id IN ({placeholders})
        ORDER BY price ASC
        """
        rows = db.execute_query(query, params)
        products: List[Dict[str, Any]] = []
        for row in rows:
            r = row if isinstance(row, dict) else dict(row)
            products.append({
                'product_id': r.get('id'),
                'name': r.get('name'),
                'category': r.get('category'),
                'price': r.get('price'),
                'platform': r.get('platform'),
                'affiliate_link': r.get('url'),
                'image_url': r.get('image_url'),
                'description': r.get('description'),
                'specs': r.get('specs'),
                'created_at': r.get('created_at'),
                'updated_at': r.get('updated_at'),
            })
        return products
    except Exception:
        return []


OVERSAMPLE_FACTOR = int(os.getenv("CLIP_OVERSAMPLE", "5"))


def find_similar_products(image_bytes: bytes, top_k: int = 10, category: Optional[str] = None) -> Dict[str, Any]:
    try:
        embedding = get_embedding(image_bytes)
        k = top_k if not category else min(top_k * OVERSAMPLE_FACTOR, 1000)
        scored = search_similar(embedding, k=k)
        id_list = [r["product_id"] for r in scored]
        products = fetch_products(id_list)
        score_map = {r["product_id"]: r["score"] for r in scored}
        enriched = []
        for p in products:
            item = dict(p)
            item["similarity"] = score_map.get(p["product_id"], None)
            item["embed_used"] = "ViT-B/32-openai"
            enriched.append(item)
        if category:
            cat = category.lower().strip()
            filtered = [p for p in enriched if (p.get("category") or "").lower() == cat]
            if len(filtered) < top_k:
                remaining = [p for p in enriched if p not in filtered]
                remaining.sort(key=lambda x: (x.get("similarity") or 0), reverse=True)
                filtered.extend(remaining[: top_k - len(filtered)])
            filtered.sort(key=lambda x: (x.get("similarity") or 0), reverse=True)
            filtered = filtered[:top_k]
            return {"status": "success", "total_results": len(filtered), "results": filtered}
        enriched.sort(key=lambda x: (x.get("similarity") or 0), reverse=True)
        enriched = enriched[:top_k]
        return {"status": "success", "total_results": len(enriched), "results": enriched}
    except Exception as e:
        return {"status": "error", "error": str(e), "results": []}


# Build helpers
from PIL import Image
import requests
from io import BytesIO

IMAGES_DIR = os.path.join("images")
EMBEDS_OUT = os.path.join("artifacts", "image_embeds.npy")
IDMAP_OUT = os.path.join("artifacts", "id_map.npy")
BATCH = int(os.getenv("CLIP_BUILD_BATCH", "16"))
LIMIT_ENV = os.getenv("CLIP_LIMIT")
CACHE = os.getenv("CLIP_CACHE_IMAGES", "0") == "1"


def _open_image(src: str):
    if os.path.exists(src):
        try:
            return Image.open(src).convert("RGB")
        except Exception:
            return None
    if src.startswith("http://") or src.startswith("https://"):
        try:
            resp = requests.get(src, timeout=15)
            resp.raise_for_status()
            return Image.open(BytesIO(resp.content)).convert("RGB")
        except Exception:
            return None
    maybe = os.path.join(IMAGES_DIR, src)
    if os.path.exists(maybe):
        try:
            return Image.open(maybe).convert("RGB")
        except Exception:
            return None
    return None


def build_db_embeddings():
    os.makedirs(os.path.dirname(EMBEDS_OUT), exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)
    db = DatabaseConnection()
    db.connect()
    limit_clause = ""
    if LIMIT_ENV:
        try:
            limit = int(LIMIT_ENV)
            limit_clause = f" LIMIT {limit}"
        except ValueError:
            pass
    rows = db.execute_query(
        f"""
        SELECT id, image_url FROM products
        WHERE image_url IS NOT NULL AND TRIM(image_url) <> ''
        {limit_clause}
        """
    )
    model, _, preprocess = open_clip.create_model_and_transforms(MODEL_NAME, pretrained=PRETRAINED, device="cpu")
    model.eval()

    def encode_batch(tensors):
        with torch.no_grad():
            feats = model.encode_image(torch.stack(tensors))
            feats = feats / feats.norm(dim=-1, keepdim=True)
            return feats.cpu().numpy().astype("float32")

    ids = []
    batch = []
    all_embeds = []
    for r in rows:
        pid = str(r["id"]) if isinstance(r, dict) else str(r[0])
        url = r["image_url"] if isinstance(r, dict) else r[1]
        img = _open_image(url)
        if img is None:
            cache_path = os.path.join(IMAGES_DIR, f"{pid}.jpg")
            if os.path.exists(cache_path):
                try:
                    img = Image.open(cache_path).convert("RGB")
                except Exception:
                    img = None
        else:
            if CACHE:
                try:
                    img.save(os.path.join(IMAGES_DIR, f"{pid}.jpg"), format="JPEG")
                except Exception:
                    pass
        if img is None:
            continue
        try:
            tensor = preprocess(img)
            batch.append(tensor)
            ids.append(pid)
            if len(batch) >= BATCH:
                all_embeds.append(encode_batch(batch))
                batch.clear()
        except Exception:
            continue
    if batch:
        all_embeds.append(encode_batch(batch))
    if not all_embeds:
        db.disconnect()
        return
    E = np.vstack(all_embeds).astype("float32")
    np.save(EMBEDS_OUT, E)
    np.save(IDMAP_OUT, np.array(ids, dtype=object))
    db.disconnect()


def build_faiss_index():
    if not os.path.exists(EMBEDS_OUT):
        raise RuntimeError("Embeddings not found. Run build_db_embeddings first.")
    import faiss  # type: ignore
    E = np.load(EMBEDS_OUT)
    index = faiss.IndexFlatIP(E.shape[1])
    index.add(E)
    faiss.write_index(index, INDEX_PATH)


# Web fallback
from .web import visual_search_web


def web_visual_search(image_bytes: bytes, top_k: int = 10) -> List[Dict[str, Any]]:
    return visual_search_web(image_bytes, top_k=top_k)
