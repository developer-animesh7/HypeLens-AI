#!/usr/bin/env python3
"""
Test URL product scraping with caching
Demonstrates: First request = 1-2s, Cached requests = <50ms
"""

import sys
import time
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.preprocess_eng.input_handler import InputHandler

def test_url_caching():
    """Test that URL caching reduces latency to <50ms"""
    
    print("\n" + "="*80)
    print("🚀 TESTING URL PRODUCT SCRAPING WITH CACHING")
    print("="*80)
    
    # Initialize handler
    handler = InputHandler()
    
    # Test URL
    test_url = "https://www.flipkart.com/safari-small-cabin-suitcase-55-cm-4-wheels-mag/p/itme32f4c89bd492?pid=STCGZN7G76ZJJ9ZA"
    
    print("\n" + "─"*80)
    print("TEST 1: COLD REQUEST (First time - needs scraping)")
    print("─"*80)
    print(f"URL: {test_url[:70]}...")
    
    start = time.time()
    result1 = handler.process(test_url)
    latency1 = (time.time() - start) * 1000
    
    print(f"\n✅ Result:")
    print(f"   Type: {result1.get('input_type')}")
    print(f"   Platform: {result1.get('platform')}")
    print(f"   Product ID: {result1.get('product_id')}")
    print(f"   Product Name: {result1.get('product_data', {}).get('name', 'N/A')[:60]}")
    print(f"   Query Text: {result1.get('query_text', '')[:70]}...")
    print(f"   Cache Hit: {result1.get('cache_hit', False)}")
    print(f"   ⏱️  Latency: {latency1:.2f}ms")
    
    print("\n" + "─"*80)
    print("TEST 2: WARM REQUEST (Same URL - should use cache)")
    print("─"*80)
    
    start = time.time()
    result2 = handler.process(test_url)
    latency2 = (time.time() - start) * 1000
    
    print(f"\n✅ Result:")
    print(f"   Type: {result2.get('input_type')}")
    print(f"   Platform: {result2.get('platform')}")
    print(f"   Product ID: {result2.get('product_id')}")
    print(f"   Product Name: {result2.get('product_data', {}).get('name', 'N/A')[:60]}")
    print(f"   Query Text: {result2.get('query_text', '')[:70]}...")
    print(f"   Cache Hit: {result2.get('cache_hit', False)}")
    print(f"   ⏱️  Latency: {latency2:.2f}ms")
    
    # Test with different URL (same product, different parameters)
    test_url2 = "https://www.flipkart.com/product/p/itme?pid=STCGZN7G76ZJJ9ZA&lid=LST123"
    
    print("\n" + "─"*80)
    print("TEST 3: SAME PRODUCT, DIFFERENT URL PARAMS (should use cache)")
    print("─"*80)
    print(f"URL: {test_url2[:70]}...")
    
    start = time.time()
    result3 = handler.process(test_url2)
    latency3 = (time.time() - start) * 1000
    
    print(f"\n✅ Result:")
    print(f"   Type: {result3.get('input_type')}")
    print(f"   Platform: {result3.get('platform')}")
    print(f"   Product ID: {result3.get('product_id')}")
    print(f"   Cache Hit: {result3.get('cache_hit', False)}")
    print(f"   ⏱️  Latency: {latency3:.2f}ms")
    
    # Performance comparison
    print("\n" + "="*80)
    print("📊 PERFORMANCE SUMMARY")
    print("="*80)
    print(f"Cold Request (Test 1):       {latency1:>8.2f}ms (scraping required)")
    print(f"Warm Request (Test 2):       {latency2:>8.2f}ms (cache hit)")
    print(f"Same Product (Test 3):       {latency3:>8.2f}ms (cache hit)")
    print(f"\nSpeedup Factor:              {latency1/latency2:>8.1f}x faster")
    print(f"Target (<50ms):              {'✅ ACHIEVED' if latency2 < 50 else '❌ NOT YET'}")
    
    # Cache stats
    cache_stats = InputHandler.get_cache_stats()
    print(f"\n📦 Cache Stats:")
    print(f"   Cached Products: {cache_stats['size']}/{cache_stats['max_size']}")
    print(f"   Products: {cache_stats['products']}")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    test_url_caching()
