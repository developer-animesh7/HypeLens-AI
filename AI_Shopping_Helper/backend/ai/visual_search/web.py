"""Web visual search fallback (Bing Visual Search)."""
from __future__ import annotations
import os
from typing import List, Dict
import requests
from urllib.parse import urlparse

BING_API_KEY = os.getenv("BING_API_KEY")
BING_ENDPOINT = os.getenv("BING_VISUAL_ENDPOINT", "https://api.bing.microsoft.com/v7.0/images/visualsearch")


def _host(u: str | None) -> str | None:
    if not u:
        return None
    try:
        return urlparse(u).hostname
    except Exception:
        return None


def visual_search_web(image_bytes: bytes, top_k: int = 10) -> List[Dict]:
    if not BING_API_KEY:
        raise RuntimeError("BING_API_KEY not configured")
    headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
    files = {"image": ("query.jpg", image_bytes, "application/octet-stream")}
    params = {"modules": "All"}
    resp = requests.post(BING_ENDPOINT, headers=headers, files=files, params=params, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    results: List[Dict] = []
    for tag in data.get("tags") or []:
        for act in tag.get("actions") or []:
            if act.get("actionType") in ("VisualSearch", "ImageResults", "SimilarImages", "PagesIncluding"):
                value = (act.get("data") or {}).get("value") or []
                for item in value:
                    name = item.get("name") or item.get("hostPageDisplayUrl") or ""
                    host_url = item.get("hostPageUrl") or item.get("webSearchUrl")
                    img_url = item.get("thumbnailUrl") or item.get("contentUrl")
                    platform = _host(host_url) or _host(item.get("contentUrl")) or "web"
                    results.append({
                        "product_id": None,
                        "name": name,
                        "category": None,
                        "price": None,
                        "platform": platform,
                        "affiliate_link": host_url or item.get("contentUrl"),
                        "image_url": img_url,
                        "description": None,
                        "specs": None,
                        "source": "web",
                        "similarity": None,
                    })
                    if len(results) >= top_k:
                        return results
    return results[:top_k]
