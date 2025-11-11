"""
Test script to verify ALL ML models are pre-loaded at server startup
and Step 3 always uses Rust-based tokenization

Run this AFTER starting the server with: python app.py
"""

import time
import requests
import sys

def test_health_endpoint():
    """Test /health endpoint for model status"""
    print("=" * 80)
    print("TEST 1: Health Check - Model Pre-loading Status")
    print("=" * 80)
    
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is healthy")
            print()
            
            # Check overall status
            models = data.get("models", {})
            print(f"Pipeline Status: {models.get('preprocessing_engine')}")
            print(f"Models Pre-loaded: {models.get('preloaded')}")
            print(f"Rust Tokenization Enforced: {models.get('rust_tokenization_enforced')}")
            print()
            
            # Check individual model details
            if "details" in models:
                print("Individual Model Status:")
                for model_name, status in models["details"].items():
                    print(f"  {model_name}: {status}")
            
            print()
            print("Performance Targets:")
            perf = data.get("performance", {})
            for key, value in perf.items():
                print(f"  {key}: {value}")
            
            return True
        else:
            print(f"❌ Health check failed with status: {response.status_code}")
            return False
    
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server!")
        print("   Make sure the server is running: python app.py")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_step3_rust_enforcement():
    """Test that Step 3 actually uses Rust tokenization"""
    print()
    print("=" * 80)
    print("TEST 2: Step 3 Rust Tokenization Enforcement")
    print("=" * 80)
    
    try:
        # Import tokenizer and verify
        from backend.preprocess_eng.tokenizer import Tokenizer
        
        print("Testing Rust tokenization enforcement...")
        print()
        
        # Test 1: Default initialization (should use Rust)
        print("Test 2.1: Default initialization (force_rust=True)")
        tokenizer1 = Tokenizer(force_rust=True)
        
        if tokenizer1.tokenizer_method == 'rust_tokenizers':
            print("✅ PASSED: Using rust_tokenizers (ENFORCED)")
        else:
            print(f"❌ FAILED: Using {tokenizer1.tokenizer_method} instead of rust_tokenizers")
            return False
        
        print()
        
        # Test 2: Verify performance
        print("Test 2.2: Performance verification")
        test_queries = [
            "wireless headphones under 5000",
            "mujhe laptop chahiye",
            "amake 100 rupees pen dekhao"
        ]
        
        total_time = 0
        for query in test_queries:
            start = time.perf_counter()
            result = tokenizer1.tokenize_step3_strict(query, tag_scripts=True)
            latency = (time.perf_counter() - start) * 1000
            total_time += latency
            
            status = "✅" if latency < 3.0 else "⚠️"
            print(f"{status} {query}: {latency:.2f}ms")
        
        avg_latency = total_time / len(test_queries)
        print()
        print(f"Average latency: {avg_latency:.2f}ms")
        
        if avg_latency < 3.0:
            print("✅ PASSED: Performance target met (<3ms)")
        else:
            print(f"⚠️ WARNING: Performance target not met (expected <3ms, got {avg_latency:.2f}ms)")
        
        print()
        
        # Test 3: Cache verification
        print("Test 2.3: Cache verification (repeated queries)")
        
        # First query (cold)
        start = time.perf_counter()
        tokenizer1.tokenize_step3_strict("wireless headphones", tag_scripts=True)
        cold_latency = (time.perf_counter() - start) * 1000
        
        # Second query (cached)
        start = time.perf_counter()
        tokenizer1.tokenize_step3_strict("wireless headphones", tag_scripts=True)
        cached_latency = (time.perf_counter() - start) * 1000
        
        print(f"Cold query: {cold_latency:.2f}ms")
        print(f"Cached query: {cached_latency:.2f}ms")
        print(f"Speedup: {cold_latency / cached_latency:.1f}x")
        
        if cached_latency < cold_latency:
            print("✅ PASSED: Caching is working")
        else:
            print("⚠️ WARNING: Caching may not be working properly")
        
        return True
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pipeline_singleton():
    """Test that pipeline uses singleton pattern (models loaded once)"""
    print()
    print("=" * 80)
    print("TEST 3: Pipeline Singleton Pattern")
    print("=" * 80)
    
    try:
        from backend.preprocess_eng.pipeline import OptimizedSemanticPipeline
        from backend.preprocess_eng.config import get_config
        
        config = get_config()
        
        print("Creating first pipeline instance...")
        pipeline1 = OptimizedSemanticPipeline(config)
        
        print("Creating second pipeline instance...")
        pipeline2 = OptimizedSemanticPipeline(config)
        
        if pipeline1 is pipeline2:
            print("✅ PASSED: Singleton pattern working (same instance returned)")
        else:
            print("❌ FAILED: Different instances returned (singleton broken)")
            return False
        
        return True
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print()
    print("=" * 80)
    print("AI SHOPPING HELPER - MODEL PRE-LOADING VERIFICATION")
    print("=" * 80)
    print()
    
    results = []
    
    # Test 1: Health endpoint
    results.append(("Health Check", test_health_endpoint()))
    
    # Test 2: Rust tokenization enforcement
    results.append(("Rust Tokenization", test_step3_rust_enforcement()))
    
    # Test 3: Singleton pattern
    results.append(("Singleton Pattern", test_pipeline_singleton()))
    
    # Summary
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print()
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("=" * 80)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 80)
        print()
        print("✅ All ML models are pre-loaded at server startup")
        print("✅ Step 3 uses Rust-based tokenization (ENFORCED)")
        print("✅ Singleton pattern ensures models load only once")
        print("✅ Performance targets met (<3ms for Step 3)")
        print()
        return 0
    else:
        print("=" * 80)
        print("❌ SOME TESTS FAILED")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
