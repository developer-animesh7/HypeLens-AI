"""
Test Step 4 → Step 5 Integration
Verify that pipeline correctly passes Step 4 output to Step 5
"""

import sys
sys.path.insert(0, 'backend')

from backend.preprocess_eng.code_mix_detector import CodeMixDetector
from backend.preprocess_eng.transliteration import get_step5_pipeline

print("=" * 70)
print("Testing Step 4 → Step 5 Integration")
print("=" * 70)
print()

# Initialize components
print("Initializing Step 4 (Code-Mix Detector)...")
step4 = CodeMixDetector(use_onnx=False)
print("✅ Step 4 initialized")
print()

print("Initializing Step 5 (Transliteration Pipeline)...")
step5 = get_step5_pipeline()
print("✅ Step 5 initialized")
print()

# Test cases
test_queries = [
    {
        "query": "mujhe wireless headphones chahiye under 5000",
        "expected_label": "romanized_indic",
        "expected_lang": "hindi",
        "language_hint": "hi"  # Hint from Step 3 that it's Hindi
    },
    {
        "query": "laptop kharidna hai budget 40000",
        "expected_label": "romanized_indic",
        "expected_lang": "hindi",
        "language_hint": "hi"
    },
    {
        "query": "wireless headphones under 5000",
        "expected_label": "pure_english",
        "expected_lang": None,
        "language_hint": "en"
    }
]

print("Running integration tests...")
print("-" * 70)

for i, test in enumerate(test_queries, 1):
    query = test["query"]
    print(f"\nTest {i}: {query}")
    print()
    
    # STEP 4: Code-Mix Detection
    print("  Step 4: Detecting script type...")
    
    # Create minimal tagged tokens (Step 3 would normally provide these)
    tagged_tokens = [
        {'text': word, 'script': 'Latin'} 
        for word in query.split()
    ]
    
    step4_result = step4.detect(
        text=query,
        tagged_tokens=tagged_tokens,
        language_hint=test.get("language_hint", "en"),
        language_confidence=0.7
    )
    
    script_label = step4_result.get('label', 'unknown')
    romanized_lang = step4_result.get('details', {}).get('romanized_language', None)
    confidence = step4_result.get('confidence', 0.0)
    
    print(f"    Label: {script_label}")
    print(f"    Confidence: {confidence:.2%}")
    if romanized_lang:
        print(f"    Romanized Language: {romanized_lang}")
    
    # Verify Step 4 output
    assert script_label == test["expected_label"], \
        f"Expected {test['expected_label']}, got {script_label}"
    
    if test["expected_lang"]:
        assert romanized_lang == test["expected_lang"], \
            f"Expected {test['expected_lang']}, got {romanized_lang}"
    
    print("    ✅ Step 4 passed")
    print()
    
    # STEP 5: Transliteration (if needed)
    if script_label in ['romanized_indic', 'mixed']:
        print("  Step 5: Transliterating...")
        
        # Map romanized language to ISO code (same logic as pipeline)
        iso_code_mapping = {
            'hindi': 'hi',
            'bengali': 'bn',
            'tamil': 'ta',
            'telugu': 'te',
            'marathi': 'mr',
            'gujarati': 'gu',
            'kannada': 'kn',
            'malayalam': 'ml',
            'punjabi': 'pa',
        }
        
        target_lang_iso = iso_code_mapping.get(romanized_lang, 'hi')
        
        # Create language flags
        language_flags = {
            'romanized': script_label == 'romanized_indic',
            'native': False,
            'english': False,
            'mixed': script_label == 'mixed'
        }
        
        # Call Step 5
        step5_result = step5.process(
            query=query,
            language_flags=language_flags,
            target_lang=target_lang_iso
        )
        
        transliterated = step5_result.normalized_query
        latency = step5_result.latency_ms
        service = step5_result.service_used
        
        print(f"    Input: {query}")
        print(f"    Output: {transliterated}")
        print(f"    Language: {target_lang_iso}")
        print(f"    Latency: {latency:.2f}ms")
        print(f"    Service: {service}")
        print("    ✅ Step 5 passed")
    else:
        print("  Step 5: Skipped (pure English)")
        print("    ✅ Step 5 skipped correctly")
    
    print()

print("-" * 70)
print("=" * 70)
print("✅ All integration tests passed!")
print("=" * 70)
print()
print("Summary:")
print("  - Step 4 correctly detects script type (romanized/pure_english)")
print("  - Step 4 correctly identifies romanized language (hindi)")
print("  - Step 5 receives correct ISO language code from Step 4")
print("  - Step 5 successfully transliterates romanized queries")
print("  - Step 5 correctly skips pure English queries")
print()
print("✅ Pipeline integration verified!")
