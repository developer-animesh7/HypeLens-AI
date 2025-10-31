"""
Test smartphone category filtering with actual smartphone image
"""
import requests
import json

# Test with smartphone image URL
SMARTPHONE_IMAGE = "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9"  # iPhone

print("🧪 Testing Category Filtering with Smartphone Image")
print("=" * 70)

try:
    # Health check
    response = requests.get("http://localhost:8000/health", timeout=5)
    print(f"\n1️⃣ Backend Health: {response.json()['status']}")
    
    # Search with smartphone image URL
    print(f"\n2️⃣ Searching with smartphone image...")
    print(f"   Image: {SMARTPHONE_IMAGE}")
    
    payload = {
        'image_url': SMARTPHONE_IMAGE,
        'top_k': 10,
        'products_source': 'db'
    }
    
    response = requests.post(
        "http://localhost:8000/api/hybrid/hybrid_search",
        json=payload,
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        results = data.get('similar_items', [])
        
        print(f"\n✅ Search successful!")
        print(f"   Total results: {len(results)}")
        print(f"   Search ID: {data.get('search_id')}")
        
        print(f"\n📊 Top 10 Results:")
        print("=" * 70)
        
        # Count categories
        categories = {}
        for idx, item in enumerate(results[:10], 1):
            category = item.get('category', 'Unknown')
            score = item.get('similarity_score', 0) * 100
            name = item.get('name', 'Unknown')[:50]
            
            categories[category] = categories.get(category, 0) + 1
            
            # Color code by category
            if category == 'Smartphones':
                color = '🟢'  # Green - CORRECT
            elif category in ['Electronics', 'Laptops']:
                color = '🟡'  # Yellow - Close
            else:
                color = '🔴'  # Red - WRONG
            
            print(f"  {idx:2d}. {color} [{category:15s}] {score:5.1f}% - {name}")
            
            # Show penalty info if available
            if 'penalty_applied' in item:
                print(f"      ⚠️  {item['penalty_applied']}")
        
        print("\n" + "=" * 70)
        print("📈 Category Distribution:")
        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            percentage = (count / len(results)) * 100
            print(f"   {cat:15s}: {count:2d} items ({percentage:5.1f}%)")
        
        print("\n" + "=" * 70)
        if categories.get('Smartphones', 0) >= 8:
            print("✅ SUCCESS: Category filtering working! 80%+ smartphones")
        elif categories.get('Smartphones', 0) >= 5:
            print("⚠️  PARTIAL: Some filtering, but needs improvement")
        else:
            print("❌ FAILED: Category filtering NOT working!")
            
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.text}")

except requests.exceptions.ConnectionError:
    print("❌ Error: Backend not running!")
    print("   Start it with: uvicorn app:app --host 0.0.0.0 --port 8000")
except Exception as e:
    print(f"❌ Error: {e}")

print("=" * 70)
