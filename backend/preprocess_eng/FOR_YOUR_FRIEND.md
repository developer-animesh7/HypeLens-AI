# 📋 FOR YOUR FRIEND: Recommendation System Implementation Guide

## Hey! 👋

Your friend has built the **Preprocessing & Product Search System**. Now it's your turn to build the **Recommendation System**!

---

## What You'll Receive

Your friend's system will give you:

```json
{
  "product_id": 123,
  "product_name": "Sony WH-1000XM5 Wireless Headphones",
  "category": "headphones",
  "price": 29990,
  "embedding": [0.123, -0.456, 0.789, ...],  // 768 float values
  "embedding_metadata": {
    "embedding_model": "intfloat/e5-base-v2",
    "embedding_dimension": 768,
    "normalized": true
  }
}
```

---

## What You Need to Build

### Endpoint: `POST /api/recommend`

**Request**:
```json
{
  "product_id": 123,
  "embedding": [768 floats],
  "category": "headphones",
  "price": 29990,
  "top_k": 10
}
```

**Response**:
```json
{
  "recommendations": [
    {
      "id": 456,
      "name": "Bose QuietComfort 45",
      "price": 28500,
      "similarity_score": 0.92,
      "url": "https://...",
      "image_url": "https://..."
    },
    ... (9 more)
  ],
  "metadata": {
    "total_recommendations": 10,
    "generation_time_ms": 45.3
  }
}
```

---

## How to Build It

### Option 1: Use Same Pinecone Index (Recommended)

```python
import pinecone
from pinecone import Pinecone

# Use same credentials as your friend
pc = Pinecone(api_key="pcsk_***")
index = pc.Index("product-search")

def generate_recommendations(product_embedding, product_id, top_k=10):
    # Query Pinecone for similar products
    results = index.query(
        vector=product_embedding,
        top_k=top_k + 1,  # +1 to exclude main product
        include_metadata=True
    )
    
    recommendations = []
    for match in results['matches']:
        if match['id'] != str(product_id):
            recommendations.append({
                'id': int(match['id']),
                'name': match['metadata']['name'],
                'price': match['metadata']['price'],
                'similarity_score': match['score'],
                'url': match['metadata'].get('url'),
                'image_url': match['metadata'].get('image_url')
            })
    
    return recommendations[:top_k]
```

---

### Option 2: Custom Similarity + Filters

```python
import numpy as np
from database import get_all_products

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def generate_recommendations_custom(
    product_embedding,
    product_id,
    category=None,
    price_range=None,
    top_k=10
):
    # Get all products (or filter by category)
    all_products = get_all_products(category=category)
    
    similarities = []
    for product in all_products:
        if product['id'] == product_id:
            continue
        
        # Calculate similarity
        sim = cosine_similarity(product_embedding, product['embedding'])
        
        # Apply price filter
        if price_range:
            if product['price'] < price_range[0] or product['price'] > price_range[1]:
                continue
        
        # Custom scoring (similarity + rating + price)
        rating_score = product.get('rating', 0) / 5.0
        price_score = 1 - abs(product['price'] - product.get('target_price', product['price'])) / 100000
        
        final_score = sim * 0.7 + rating_score * 0.2 + price_score * 0.1
        
        similarities.append({
            'product': product,
            'similarity_score': sim,
            'final_score': final_score
        })
    
    # Sort by final score
    similarities.sort(key=lambda x: x['final_score'], reverse=True)
    
    return [s['product'] for s in similarities[:top_k]]
```

---

### Option 3: Hybrid (Pinecone + Custom Ranking)

```python
def generate_recommendations_hybrid(
    product_embedding,
    product_id,
    category=None,
    price_range=None,
    top_k=10
):
    # Step 1: Get candidates from Pinecone (fast)
    results = index.query(
        vector=product_embedding,
        top_k=50,  # Get more candidates
        include_metadata=True
    )
    
    # Step 2: Apply filters
    filtered = []
    for match in results['matches']:
        if match['id'] == str(product_id):
            continue
        
        # Category filter
        if category and match['metadata'].get('category') != category:
            continue
        
        # Price filter
        if price_range:
            price = match['metadata'].get('price', 0)
            if price < price_range[0] or price > price_range[1]:
                continue
        
        filtered.append(match)
    
    # Step 3: Custom ranking
    for product in filtered:
        rating = product['metadata'].get('rating', 0)
        rating_boost = rating / 5.0
        product['final_score'] = product['score'] * 0.8 + rating_boost * 0.2
    
    # Sort and return
    filtered.sort(key=lambda x: x['final_score'], reverse=True)
    
    return [{
        'id': int(p['id']),
        'name': p['metadata']['name'],
        'price': p['metadata']['price'],
        'similarity_score': p['score'],
        'final_score': p['final_score'],
        'url': p['metadata'].get('url'),
        'image_url': p['metadata'].get('image_url')
    } for p in filtered[:top_k]]
```

---

## FastAPI Example

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class RecommendationRequest(BaseModel):
    product_id: int
    embedding: List[float]
    category: str = None
    price: float = None
    top_k: int = 10

class RecommendationResponse(BaseModel):
    recommendations: List[dict]
    metadata: dict

@app.post("/api/recommend", response_model=RecommendationResponse)
async def recommend(request: RecommendationRequest):
    try:
        # Generate recommendations
        recommendations = generate_recommendations(
            product_embedding=request.embedding,
            product_id=request.product_id,
            top_k=request.top_k
        )
        
        return {
            "recommendations": recommendations,
            "metadata": {
                "total_recommendations": len(recommendations),
                "generation_time_ms": 45.3  # Measure actual time
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Testing Your System

### 1. Test with Sample Embedding

```python
# Create test embedding (768 floats)
test_embedding = [0.1] * 768

# Test your function
recommendations = generate_recommendations(
    product_embedding=test_embedding,
    product_id=123,
    top_k=10
)

print(f"Found {len(recommendations)} recommendations")
for rec in recommendations:
    print(f"- {rec['name']}: {rec['similarity_score']:.3f}")
```

---

### 2. Test Your API

```bash
curl -X POST http://localhost:8080/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 123,
    "embedding": [0.1, 0.2, ...],  // 768 floats
    "category": "headphones",
    "top_k": 10
  }'
```

---

## Integration with Friend's System

### Complete Flow:

```
User Search Query
       ↓
[Friend's System]
  Preprocessing → Find Product → Generate Embedding
       ↓
  Returns: {product, embedding}
       ↓
[Your System]
  Receives: {product_id, embedding}
       ↓
  Generate Recommendations
       ↓
  Returns: {recommendations: [...]}
       ↓
[Frontend]
  Display: Main Product + Recommendations
```

---

## What Your Friend Provides

### Pinecone Credentials:
- **API Key**: Ask your friend
- **Index Name**: `product-search`
- **Region**: `us-east-1`
- **Dimension**: 768

### PostgreSQL Access (optional):
- **Host**: `localhost`
- **Port**: `5432`
- **Database**: `shopping_assistant`
- **User/Password**: Ask your friend

---

## Quick Start Checklist

- [ ] Get Pinecone API key from your friend
- [ ] Install Pinecone: `pip install pinecone-client`
- [ ] Install FastAPI: `pip install fastapi uvicorn`
- [ ] Implement `generate_recommendations()` function
- [ ] Create `/api/recommend` endpoint
- [ ] Test with sample embedding
- [ ] Integrate with friend's system
- [ ] Test complete flow

---

## Need Help?

Ask your friend to share:
1. `INTEGRATION_GUIDE.md` - Complete integration docs
2. Pinecone API key and credentials
3. Sample embedding data for testing

Good luck! 🚀
