#!/usr/bin/env python3
"""
Quick Performance Test - Steps 1-3 Only (No Transliteration)
Tests the critical fast steps to verify optimizations
"""
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

import time
from AI_Shopping_Helper.backend.preprocess_eng.input_handler import InputHandler
from AI_Shopping_Helper.backend.preprocess_eng.spell_corrector import SpellCorrector
from AI_Shopping_Helper.backend.preprocess_eng.tokenizer import Tokenizer

print("\n" + "="*80)
print("QUICK PERFORMANCE TEST - Steps 1-3")
print("="*80 + "\n")

# Initialize components
print("⏳ Loading components...")
start = time.perf_counter()

input_handler = InputHandler()
spell_corrector = SpellCorrector()
tokenizer = Tokenizer(enable_edge_ngrams=True)

load_time = (time.perf_counter() - start) * 1000
print(f"✅ Components loaded in {load_time:.1f}ms\n")

# Test queries
test_queries = [
    "amake 2000 takar earphone dekhao",
    "wireless headphone under 5000",
    "show me iphone 12",
    "samsung galaxy f21 price",
    "laptop under 50000 rupees"
]

print("="*80)
print("RUNNING PERFORMANCE TESTS (3 iterations each for warmup)")
print("="*80 + "\n")

for query in test_queries:
    print(f"Query: {query}")
    print("-" * 80)
    
    # Warm up (run twice to let caches warm up)
    for warmup in range(2):
        input_result = input_handler.process(query)
        normalized = input_result['query_text']
        corrected = spell_corrector.correct(normalized)
        tokens_result = tokenizer.tokenize_production(corrected, tag_scripts=True, generate_ngrams=False)
    
    # Actual timing run
    timings = []
    
    # Step 1
    start = time.perf_counter()
    input_result = input_handler.process(query)
    normalized = input_result['query_text']
    step1_time = (time.perf_counter() - start) * 1000
    
    # Step 2
    start = time.perf_counter()
    corrected = spell_corrector.correct(normalized)
    step2_time = (time.perf_counter() - start) * 1000
    
    # Step 3
    start = time.perf_counter()
    tokens_result = tokenizer.tokenize_production(corrected, tag_scripts=True, generate_ngrams=False)
    step3_time = (time.perf_counter() - start) * 1000
    
    total_time = step1_time + step2_time + step3_time
    
    # Display results
    print(f"  Step 1 (Input):  {step1_time:6.2f}ms {'✅' if step1_time < 1.0 else '⚠️' if step1_time < 2.0 else '❌'} (target: <1ms)")
    print(f"  Step 2 (Spell):  {step2_time:6.2f}ms {'✅' if step2_time <= 3.0 else '⚠️' if step2_time < 5.0 else '❌'} (target: 1-3ms)")
    print(f"  Step 3 (Token):  {step3_time:6.2f}ms {'✅' if step3_time <= 3.0 else '⚠️' if step3_time < 6.0 else '❌'} (target: 1-3ms)")
    print(f"  Total Steps 1-3: {total_time:6.2f}ms {'✅' if total_time <= 7.0 else '⚠️' if total_time < 12.0 else '❌'} (target: <7ms)")
    
    # Show results
    print(f"  Tokens: {tokens_result['tokens']}")
    print(f"  Language: {tokens_result['language']} ({tokens_result['language_confidence']*100:.1f}%)")
    print()

print("="*80)
print("PERFORMANCE SUMMARY")
print("="*80)
print("Optimizations Applied:")
print("  ✅ Step 1: Fast URL detection (skip regex for text queries)")
print("  ✅ Step 2: LRU caching (10K entries)")
print("  ✅ Step 3: Reduced n-gram generation (4+ chars only, max=8)")
print("  ✅ Step 3: Optimized mixed-script detection")
print("\nExpected Performance:")
print("  Step 1: <1ms   (text queries)")
print("  Step 2: <3ms   (with cache hits)")
print("  Step 3: <3ms   (optimized n-grams)")
print("  Total:  <7ms   (all three steps)")
print("\n" + "="*80)
