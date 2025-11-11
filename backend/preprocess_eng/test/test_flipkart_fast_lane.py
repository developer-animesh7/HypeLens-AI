"""
Test script to verify Flipkart Fast Lane Rules A and B for all Indic languages
"""
import sys
sys.path.insert(0, 'backend/preprocess_eng')

from tokenizer import Tokenizer
from code_mix_detector import CodeMixDetector
import time

def test_fast_lane_rules():
    """
    Test Flipkart Fast Lane implementation:
    - Rule A: Pure Native Script (all Indic languages)
    - Rule B: Pure English (high confidence >85%)
    """
    print('='*80)
    print('FLIPKART FAST LANE RULES VALIDATION')
    print('='*80)
    print()
    
    # Initialize components
    print('⏳ Initializing components...')
    tokenizer = Tokenizer()
    detector = CodeMixDetector(use_onnx=False)
    print('✅ Components initialized')
    print()
    
    # Test cases for all Indic languages
    test_cases = [
        # Rule A: Pure Native Script tests
        {
            'query': 'अच्छा हेडफोन दिखाओ',
            'expected_script': 'Devanagari',
            'expected_lang': 'hi',
            'expected_label': 'pure_native',
            'expected_rule': 'Rule A',
            'skip_step5': True,
            'description': 'Hindi (Devanagari)'
        },
        {
            'query': 'আমাকে ইয়ারফোন দেখাও',
            'expected_script': 'Bengali',
            'expected_lang': 'bn',
            'expected_label': 'pure_native',
            'expected_rule': 'Rule A',
            'skip_step5': True,
            'description': 'Bengali (Bengali script)'
        },
        {
            'query': 'நல்ல ஹெட்ஃபோன்',
            'expected_script': 'Tamil',
            'expected_lang': 'ta',
            'expected_label': 'pure_native',
            'expected_rule': 'Rule A',
            'skip_step5': True,
            'description': 'Tamil (Tamil script)'
        },
        {
            'query': 'మంచి హెడ్ఫోన్',
            'expected_script': 'Telugu',
            'expected_lang': 'te',
            'expected_label': 'pure_native',
            'expected_rule': 'Rule A',
            'skip_step5': True,
            'description': 'Telugu (Telugu script)'
        },
        {
            'query': 'સારા હેડફોન',
            'expected_script': 'Gujarati',
            'expected_lang': 'gu',
            'expected_label': 'pure_native',
            'expected_rule': 'Rule A',
            'skip_step5': True,
            'description': 'Gujarati (Gujarati script)'
        },
        {
            'query': 'ಒಳ್ಳೆಯ ಹೆಡ್ಫೋನ್',
            'expected_script': 'Kannada',
            'expected_lang': 'kn',
            'expected_label': 'pure_native',
            'expected_rule': 'Rule A',
            'skip_step5': True,
            'description': 'Kannada (Kannada script)'
        },
        {
            'query': 'നല്ല ഹെഡ്ഫോൺ',
            'expected_script': 'Malayalam',
            'expected_lang': 'ml',
            'expected_label': 'pure_native',
            'expected_rule': 'Rule A',
            'skip_step5': True,
            'description': 'Malayalam (Malayalam script)'
        },
        
        # Rule B: Pure English tests (high confidence >85%)
        {
            'query': 'wireless bluetooth headphone',
            'expected_script': 'Latin',
            'expected_lang': 'en',
            'expected_label': 'pure_english',
            'expected_rule': 'Rule B',
            'skip_step5': True,
            'description': 'Pure English (high confidence)'
        },
        {
            'query': 'show redmi note 12 pro',
            'expected_script': 'Latin',
            'expected_lang': 'en',
            'expected_label': 'pure_english',
            'expected_rule': 'Rule B',
            'skip_step5': True,
            'description': 'Pure English (product query)'
        },
        {
            'query': 'best headphone under 5000',
            'expected_script': 'Latin',
            'expected_lang': 'en',
            'expected_label': 'pure_english',
            'expected_rule': 'Rule B',
            'skip_step5': True,
            'description': 'Pure English (with price)'
        },
        
        # Romanized Indic (should NOT match Rule A or B)
        {
            'query': 'mujhe headphone chahiye',
            'expected_script': 'Latin',
            'expected_lang': 'hi',
            'expected_label': 'romanized_indic',
            'expected_rule': 'Romanized',
            'skip_step5': False,
            'description': 'Romanized Hindi (needs Step 5)'
        },
        {
            'query': 'amake earphone dekhao',
            'expected_script': 'Latin',
            'expected_lang': 'bn',
            'expected_label': 'romanized_indic',
            'expected_rule': 'Romanized',
            'skip_step5': False,
            'description': 'Romanized Bengali (needs Step 5)'
        },
    ]
    
    print(f'Testing {len(test_cases)} queries...')
    print('='*80)
    print()
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        query = test['query']
        
        # Step 3: Tokenize and detect language
        start = time.perf_counter()
        step3_result = tokenizer.tokenize_production(query, tag_scripts=True, generate_ngrams=False)
        step3_latency = (time.perf_counter() - start) * 1000
        
        detected_lang = step3_result['language']
        lang_confidence = step3_result['language_confidence']
        tagged_tokens = step3_result['tagged_tokens']
        
        # Step 4: Code-mix detection with Fast Lane
        start = time.perf_counter()
        step4_result = detector.detect(
            query,
            tagged_tokens,
            language_hint=detected_lang,
            language_confidence=lang_confidence
        )
        step4_latency = (time.perf_counter() - start) * 1000
        
        # Validate results
        script_label = step4_result['label']
        skip_step5 = script_label in ['pure_english', 'pure_native']
        reason = step4_result['details'].get('reason', '')
        
        # Check if test passed
        lang_match = detected_lang == test['expected_lang']
        label_match = script_label == test['expected_label']
        skip_match = skip_step5 == test['skip_step5']
        
        test_passed = lang_match and label_match and skip_match
        
        if test_passed:
            status = '✅ PASS'
            passed += 1
        else:
            status = '❌ FAIL'
            failed += 1
        
        print(f'[Test {i}] {status} - {test["description"]}')
        print(f'  Query: "{query}"')
        print(f'  Step 3: {detected_lang} ({lang_confidence:.1%}) | Latency: {step3_latency:.2f}ms')
        print(f'  Step 4: {script_label} | {reason}')
        print(f'  Skip Step 5: {skip_step5} | Latency: {step4_latency:.2f}ms')
        
        if not test_passed:
            print(f'  Expected: lang={test["expected_lang"]}, label={test["expected_label"]}, skip={test["skip_step5"]}')
            print(f'  Got:      lang={detected_lang}, label={script_label}, skip={skip_step5}')
        
        print()
    
    print('='*80)
    print('TEST SUMMARY')
    print('='*80)
    print(f'Total:  {len(test_cases)}')
    print(f'Passed: {passed} ✅')
    print(f'Failed: {failed} ❌')
    print()
    
    if failed == 0:
        print('🎉 ALL TESTS PASSED! Flipkart Fast Lane fully compliant!')
    else:
        print(f'⚠️  {failed} test(s) failed. Review implementation.')
    
    print('='*80)
    
    return failed == 0

if __name__ == "__main__":
    success = test_fast_lane_rules()
    sys.exit(0 if success else 1)
