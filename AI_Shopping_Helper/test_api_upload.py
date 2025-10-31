"""
Quick test to verify image upload API works
"""
import requests
import sys
from pathlib import Path

# Find a test image
test_images = [
    "images/test_local2.jpg",
    "images/test.jpg",
]

image_path = None
for img in test_images:
    if Path(img).exists():
        image_path = img
        break

if not image_path:
    print("❌ No test image found!")
    sys.exit(1)

print(f"\n🧪 Testing API with image: {image_path}")
print("="*60)

# Test 1: Health check
print("\n1️⃣ Testing /health endpoint...")
try:
    response = requests.get("http://localhost:8000/health", timeout=3)
    print(f"   ✅ Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    sys.exit(1)

# Test 2: Image upload
print("\n2️⃣ Testing /api/hybrid/hybrid_search endpoint...")
try:
    with open(image_path, 'rb') as f:
        files = {'file': (Path(image_path).name, f, 'image/jpeg')}
        data = {'top_k': '5', 'products_source': 'db'}
        
        response = requests.post(
            "http://localhost:8000/api/hybrid/hybrid_search",
            files=files,
            data=data,
            timeout=30
        )
        
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ SUCCESS!")
        print(f"   Search ID: {result.get('search_id')}")
        print(f"   Total Results: {result.get('total_results')}")
        
        if result.get('exact_match'):
            print(f"   Exact Match: {result['exact_match']['name']}")
            print(f"   Score: {result['exact_match']['similarity_score']:.2%}")
        
        print(f"\n   Similar Items: {len(result.get('similar_items', []))}")
        for i, item in enumerate(result.get('similar_items', [])[:3], 1):
            print(f"      {i}. {item['name']} ({item['similarity_score']:.2%})")
    else:
        print(f"   ❌ FAILED!")
        print(f"   Error: {response.text}")
        
except Exception as e:
    print(f"   ❌ Failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("✅ Test complete!")
