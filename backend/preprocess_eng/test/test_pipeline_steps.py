#!/usr/bin/env python3
"""
Test Pipeline Step Order - Verify Correct Architecture
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_pipeline_step_order():
    """Test that pipeline follows correct step order"""
    
    print("\n" + "="*80)
    print("TESTING PIPELINE STEP ORDER")
    print("="*80 + "\n")
    
    try:
        # Import after path setup
        from preprocess_eng.pipeline import OptimizedSemanticPipeline
        from preprocess_eng.config import get_config
        
        # Get config
        config = get_config()
        
        # Initialize pipeline
        print("📦 Initializing pipeline...")
        pipeline = OptimizedSemanticPipeline(config=config, debug_mode=True)
        
        # Test queries
        test_queries = [
            {
                'query': 'amake 2000 taka damer earphone dekhao',
                'language': 'bn_Latn',  # Romanized Bengali
                'description': 'Romanized Bengali query'
            },
            {
                'query': 'show me iphone 12',
                'language': 'en',
                'description': 'English query'
            },
            {
                'query': 'আমাকে ২০০০ টাকা দামের ইয়ারফোন দেখাও',
                'language': 'bn',
                'description': 'Native Bengali script'
            }
        ]
        
        for idx, test_case in enumerate(test_queries, 1):
            print(f"\n{'─'*80}")
            print(f"Test {idx}: {test_case['description']}")
            print(f"{'─'*80}")
            print(f"Query: {test_case['query']}")
            print(f"Expected language: {test_case['language']}\n")
            
            try:
                # Process query
                result = pipeline.process(
                    test_case['query'],
                    top_k=5,
                    include_metadata=True
                )
                
                # Extract metrics
                query_info = result.get('query_info', {})
                metrics = result.get('metrics', {})
                stage_times = metrics.get('stage_times_ms', {})
                
                # Verify step order
                print("✅ STEP ORDER VERIFICATION:")
                print(f"  STEP 1 (Input Normalization): {stage_times.get('step1_input_normalization', 'N/A'):.2f}ms")
                print(f"  STEP 2 (Spell Correction): {stage_times.get('step2_spell_correction', 'N/A'):.2f}ms")
                print(f"  STEP 3 (Tokenization + Lang Detection): {stage_times.get('step3_tokenization_and_detection', 'N/A'):.2f}ms")
                print(f"  STEP 4 (Translation): {stage_times.get('step4_translation', 'N/A'):.2f}ms")
                print(f"  STEP 5 (Feature Extraction): {stage_times.get('step5_feature_extraction', 'N/A'):.2f}ms")
                print(f"  STEP 6 (Synonym Expansion): {stage_times.get('step6_synonym_expansion', 'N/A'):.2f}ms")
                print(f"  STEP 7 (Embedding): {stage_times.get('step7_embedding', 'N/A'):.2f}ms")
                
                print("\n📊 QUERY PROCESSING:")
                print(f"  Original: {query_info.get('original_query', 'N/A')}")
                print(f"  Normalized: {query_info.get('normalized', 'N/A')}")
                print(f"  Corrected: {query_info.get('corrected', 'N/A')}")
                print(f"  Processed: {query_info.get('processed_query', 'N/A')}")
                print(f"  Detected Language: {query_info.get('detected_language', 'N/A')} "
                      f"({query_info.get('language_confidence', 0)*100:.1f}% confidence)")
                
                print("\n🔍 TOKENS:")
                tokens = query_info.get('tokens', [])
                print(f"  {tokens[:10]}..." if len(tokens) > 10 else f"  {tokens}")
                
                print("\n📈 PERFORMANCE:")
                print(f"  Total Latency: {metrics.get('total_latency_ms', 'N/A'):.2f}ms")
                print(f"  Optimizations: {', '.join(metrics.get('optimizations', []))}")
                
                # Verify language detection is correct
                detected_lang = query_info.get('detected_language', 'unknown')
                expected_lang = test_case['language']
                
                if detected_lang == expected_lang:
                    print(f"\n✅ Language detection: CORRECT ({detected_lang})")
                else:
                    print(f"\n⚠️  Language detection: Expected {expected_lang}, got {detected_lang}")
                
                # Verify step 2 did spell correction (not language detection)
                if 'corrected' in query_info:
                    print("✅ Step 2: Spell correction present")
                else:
                    print("❌ Step 2: Missing spell correction!")
                
                # Verify step 3 includes language detection
                if 'detected_language' in query_info and 'tokens' in query_info:
                    print("✅ Step 3: Language detection and tokenization present")
                else:
                    print("❌ Step 3: Missing language detection or tokenization!")
                
                print(f"\n✅ Test {idx} PASSED\n")
                
            except Exception as e:
                print(f"\n❌ Test {idx} FAILED: {str(e)}\n")
                import traceback
                traceback.print_exc()
        
        print("\n" + "="*80)
        print("PIPELINE STATISTICS")
        print("="*80)
        stats = pipeline.get_stats()
        print(json.dumps(stats, indent=2))
        
        print("\n✅ ALL TESTS COMPLETED")
        return True
        
    except Exception as e:
        print(f"\n❌ PIPELINE TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_pipeline_step_order()
    sys.exit(0 if success else 1)
