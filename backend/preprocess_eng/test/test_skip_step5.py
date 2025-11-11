"""
Test script to verify Skip Step 5 logic with 75% threshold
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.preprocess_eng.tokenizer import Tokenizer
from backend.preprocess_eng.code_mix_detector import CodeMixDetector
from backend.preprocess_eng.spell_corrector import SpellCorrector
from backend.preprocess_eng.input_handler import InputHandler

def test_skip_step5():
    """Test Skip Step 5 logic with 75% confidence threshold"""
    
    print("=" * 80)
    print("SKIP STEP 5 LOGIC TEST (Threshold: ≥75%)")
    print("=" * 80)
    print()
    
    # Initialize components
    print("Initializing components...")
    input_handler = InputHandler()
    spell_corrector = SpellCorrector()
    tokenizer = Tokenizer(force_rust=True)
    detector = CodeMixDetector(use_onnx=False)
    print("✅ Components loaded")
    print()
    
    # Test cases
    test_cases = [
        ("boat trimmer under 1500", "English with brand name", True),
        ("wireless headphones under 5000", "Pure English query", True),
        ("cost trimmer under 1500", "English product query", True),
        ("mujhe headphone chahiye", "Romanized Hindi", False),
        ("amake earphone dekhao", "Romanized Bengali", False),
        ("आमके ईयरफोन देखाओ", "Native script", True),
    ]
    
    results = []
    
    for query, description, expected_skip in test_cases:
        print(f"Query: {query}")
        print(f"Description: {description}")
        
        # Step 1: Normalize
        step1_result = input_handler.process(query)
        normalized = step1_result.get('normalized_text', query)
        
        # Step 2: Spell correct
        corrected = spell_corrector.correct(normalized)
        
        # Step 3: Tokenize with script tags
        step3_result = tokenizer.tokenize_step3_strict(corrected, tag_scripts=True)
        tagged_tokens = step3_result.get('script_tagged_tokens', [])
        language = step3_result.get('primary_language', 'en')
        language_confidence = step3_result.get('language_confidence', 0.0)
        
        # Step 4: Code-mix detection (with Smart Checkpoint enabled)
        step4_result = detector.detect(
            corrected,
            tagged_tokens=tagged_tokens,
            language_hint=language,
            language_confidence=language_confidence,
            use_smart_checkpoint=True  # ENABLE Smart Checkpoint for ambiguous cases
        )
        
        label = step4_result.get('label', 'unknown')
        confidence = step4_result.get('confidence', 0.0) * 100
        skip_step5 = step4_result.get('skip_step5', False)
        method = step4_result.get('method', 'unknown')
        
        print(f"  Corrected: {corrected}")
        print(f"  Label: {label}")
        print(f"  Method: {method}")
        print(f"  Confidence: {confidence:.1f}%")
        print(f"  Skip Step 5: {'✅ YES' if skip_step5 else '❌ NO'}")
        print(f"  Expected: {'✅ YES' if expected_skip else '❌ NO'}")
        
        # Verify
        if skip_step5 == expected_skip:
            print("  ✅ PASS")
            results.append((query, True))
        else:
            print(f"  ❌ FAIL: Expected skip={expected_skip}, got skip={skip_step5}")
            results.append((query, False))
        
        print()
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for query, passed_test in results:
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status}: {query}")
    
    print()
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print()
        print("=" * 80)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 80)
        print()
        print("✅ Pure English queries with ≥75% confidence SKIP Step 5")
        print("✅ Pure native queries with ≥75% confidence SKIP Step 5")
        print("✅ Romanized queries CONTINUE to Step 5")
        print()
        return True
    else:
        print()
        print("=" * 80)
        print("❌ SOME TESTS FAILED")
        print("=" * 80)
        return False


if __name__ == "__main__":
    success = test_skip_step5()
    sys.exit(0 if success else 1)
