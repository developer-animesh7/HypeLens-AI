"""
Interactive Test for Steps 1-5: Complete Preprocessing Pipeline
================================================================

Tests the complete pipeline from user input to transliteration:
- Step 1: Input Normalization
- Step 2: Language Detection
- Step 3: Tokenization & Script Detection
- Step 4: Code-Mix Analysis & Romanization Detection
- Step 5: Transliteration (Romanized → Native Script)

Author: AI Shopping Helper Team
Date: October 18, 2025

Usage:
    python3 test_steps1_5_interactive.py
"""

import sys
import os
import time
import logging
from typing import Dict, Any

# Add parent directory to path so we can import modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Also add the AI_Shopping_Helper directory for backend imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class CompletePipelineTest:
    """Interactive test for Steps 1-5"""
    
    def __init__(self):
        """Initialize all pipeline components"""
        print("=" * 80)
        print("INITIALIZING PREPROCESSING PIPELINE (Steps 1-5)")
        print("=" * 80)
        print()
        
        # Step 1: Input Normalization
        print("⏳ Loading Step 1: Input Normalization...")
        try:
            from input_handler import InputHandler
            self.input_handler = InputHandler()
            print("✅ Step 1 loaded")
        except Exception as e:
            print(f"❌ Step 1 failed: {e}")
            self.input_handler = None
        
        # Step 2: Spell Correction & Query Rewrite
        print("⏳ Loading Step 2: Spell Correction & Query Rewrite...")
        try:
            from spell_corrector import SpellCorrector
            self.spell_corrector = SpellCorrector()
            print("✅ Step 2 loaded")
        except Exception as e:
            print(f"❌ Step 2 failed: {e}")
            self.spell_corrector = None
        
        # Step 3: Tokenization & Script Detection
        print("⏳ Loading Step 3: Tokenization & Script Detection...")
        try:
            from tokenizer import Tokenizer
            self.tokenizer = Tokenizer()
            print("✅ Step 3 loaded")
        except Exception as e:
            print(f"⚠️  Step 3 failed: {e}")
            self.tokenizer = None
        
        # Step 4: Code-Mix Detection (Flipkart-Style)
        print("⏳ Loading Step 4: Lightweight Code-Mix Detection...")
        try:
            from code_mix_detector import CodeMixDetector
            self.code_mix_detector = CodeMixDetector(use_onnx=False)
            print("✅ Step 4 loaded (Flipkart-style Fast Lane + Smart Checkpoint)")
        except Exception as e:
            print(f"❌ Step 4 failed: {e}")
            self.code_mix_detector = None
            # Fallback to old detector
            try:
                from smart_romanized_detector import SmartRomanizedDetector
                self.script_detector = SmartRomanizedDetector()
                print("⚠️  Using fallback detector (old implementation)")
            except:
                self.script_detector = None
        
        # Step 5: Transliteration
        print("⏳ Loading Step 5: Transliteration (this may take 3-4s)...")
        try:
            # Add parent directory to path for imports
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from transliteration import get_step5_pipeline
            self.transliteration_pipeline = get_step5_pipeline()
            print("✅ Step 5 loaded")
        except Exception as e:
            print(f"❌ Step 5 failed: {e}")
            self.transliteration_pipeline = None
        
        print()
        print("=" * 80)
        print("✅ PIPELINE INITIALIZATION COMPLETE")
        print("=" * 80)
        print()
    
    def step1_normalize(self, query: str) -> Dict[str, Any]:
        """Step 1: Input Normalization"""
        print("\n" + "─" * 80)
        print("STEP 1: Input Normalization")
        print("─" * 80)
        
        if not self.input_handler:
            print("❌ Step 1 not available")
            return {"normalized": query, "original": query, "input_type": "text"}
        
        start = time.perf_counter()
        
        # Process input (input_handler uses .process() method)
        result = self.input_handler.process(query)
        
        latency = (time.perf_counter() - start) * 1000
        
        # For text queries, use query_text. For URLs, product_data is converted to text
        # FIXED: Changed from 'query' to 'query_text' to match input_handler output
        normalized = result.get('query_text', query)
        
        print(f"Input:      {query}")
        print(f"Type:       {result.get('input_type', 'text')}")
        print(f"Normalized: {normalized}")
        print(f"Latency:    {latency:.2f}ms")
        
        # ADDED: Show scraped product data if URL was processed
        if result.get('input_type') == 'url':
            print()
            print(f"🔗 URL Processing:")
            print(f"   Platform: {result.get('platform', 'Unknown')}")
            print(f"   Product ID: {result.get('product_id', 'N/A')}")
            if result.get('product_data'):
                product = result['product_data']
                print(f"   📦 Product Scraped:")
                print(f"      Name: {product.get('name', 'Unknown')[:60]}")
                if product.get('price'):
                    print(f"      Price: ₹{product.get('price')}")
                if product.get('rating'):
                    print(f"      Rating: {product.get('rating')}/5.0")
                if product.get('category'):
                    print(f"      Category: {product.get('category')}")
                print(f"   ✅ Converted to text: {normalized[:80]}...")
        
        return {"normalized": normalized, "original": query, **result}
    
    def step2_spell_correction(self, text: str) -> Dict[str, Any]:
        """
        Step 2: Spell Correction & Query Rewrite
        
        **Specification:**
        - SymSpell-based correction (precomputed dictionary)
        - High-confidence rewrite rules from query logs
        - Aggressive unit normalization (taka, rs, inr)
        - Latency Target: 1-3ms
        - Why before tokenization: Avoids fragmented tokens like "iphon12"
        """
        print("\n" + "─" * 80)
        print("STEP 2: Spell Correction & Query Rewrite")
        print("─" * 80)
        
        if not self.spell_corrector:
            print("❌ Step 2 not available")
            return {"corrected": text, "corrections": [], "latency_ms": 0.0}
        
        start = time.perf_counter()
        
        # Apply spell correction and query rewrites
        corrected_text = self.spell_corrector.correct(text, apply_unit_normalization=True)
        
        latency = (time.perf_counter() - start) * 1000
        
        # Track if any changes were made
        corrections = []
        if corrected_text != text:
            corrections.append({'original': text, 'corrected': corrected_text})
        
        print(f"Input:       {text}")
        print(f"Corrected:   {corrected_text}")
        if corrections:
            print(f"Changes:     {len(corrections)} corrections applied")
            for corr in corrections[:3]:  # Show first 3
                print(f"             - {corr.get('original', '?')} → {corr.get('corrected', '?')}")
        else:
            print(f"Changes:     No corrections needed")
        print(f"Latency:     {latency:.2f}ms")
        
        return {"corrected": corrected_text, "corrections": corrections, "latency_ms": latency}
    
    def step3_tokenize_and_detect_script(self, text: str) -> Dict[str, Any]:
        """
        Step 3: Tokenization & Script Detection & Language Detection
        
        **Specification:**
        - Action 1: FastTokenize (Rust-based) or ICU BreakIterator fallback
        - Action 2: Script Detection - Regex-based Unicode block tagging per token
        - Action 3: Language Detection - fastText (lid.176.bin) once per query (PARALLEL with Action 1)
        - Latency Target: 1-3ms total for short queries
        - Works on: All Indic scripts (Bengali, Hindi, Tamil, etc.)
        - No heavy dependencies or GPU
        """
        print("\n" + "─" * 80)
        print("STEP 3: Tokenization, Script Detection & Language Detection")
        print("─" * 80)
        
        if not self.tokenizer:
            print("❌ Step 3 not available")
            return {
                "tokens": text.split(),
                "language": "en",
                "confidence": 0.0,
                "scripts": ["Latin"],
                "script_distribution": {},
                "latency_ms": 0
            }
        
        start = time.perf_counter()
        
        # Use STRICT Step 3 compliance method with script tagging enabled
        # This follows the exact specification:
        # 1. Tokenization (FastTokenize)
        # 2. Script Detection (Regex - per token)
        # 3. Language Detection (fastText - whole string)
        result = self.tokenizer.tokenize_step3_strict(text, tag_scripts=True)
        
        latency = (time.perf_counter() - start) * 1000
        
        # Extract results
        tokens = result.get('tokens', [])
        script_tags = result.get('script_tags', [])
        language = result.get('language', 'en')
        language_confidence = result.get('language_confidence', 0.0)
        tagged_tokens = result.get('tagged_tokens', [])
        
        # Format script tags for display
        if script_tags:
            script_tags_display = ', '.join(script_tags[:8])
            if len(script_tags) > 8:
                script_tags_display += ', ...'
        else:
            script_tags_display = 'not tagged'
        
        print(f"Input:               {text}")
        print(f"Language (fastText): {language}")
        print(f"Confidence:          {language_confidence:.2%}")
        print(f"Tokens:              {tokens[:8]}{'...' if len(tokens) > 8 else ''}")
        print(f"Token Count:         {len(tokens)}")
        print(f"Script Tags:         [{script_tags_display}]")
        print(f"Latency:             {latency:.2f}ms {'✅' if latency <= 3 else '⚠️'}")
        
        return {
            'tokens': tokens,
            'script_tags': script_tags,
            'language': language,
            'language_confidence': language_confidence,
            'tagged_tokens': tagged_tokens,
            'latency_ms': latency
        }
    
    def step4_detect_script(self, text: str, detected_lang: str, language_confidence: float = 0.0, 
                           tagged_tokens: list = None) -> Dict[str, Any]:
        """
        Step 4: Lightweight Code-Mix Detection (Flipkart-Style)
        
        Two-pronged approach:
        1. Fast Lane (Heuristics): Handles 80-90% instantly (<1ms)
        2. Smart Checkpoint (ML): Handles ambiguous cases (2-6ms)
        
        Args:
            text: Input text
            detected_lang: Language detected by Step 3
            language_confidence: Confidence from Step 3 (0.0-1.0)
            tagged_tokens: Script-tagged tokens from Step 3
        """
        print("\n" + "─" * 80)
        print("STEP 4: Lightweight Code-Mix Detection (Flipkart-Style)")
        print("─" * 80)
        
        if not hasattr(self, 'code_mix_detector') or not self.code_mix_detector:
            print("❌ Step 4 not available (using fallback)")
            # Fallback to old behavior
            if hasattr(self, 'script_detector') and self.script_detector:
                romanized_lang, confidence = self.script_detector.detect_romanized_language(text)
                return {
                    "romanized": romanized_lang is not None,
                    "native": False,
                    "english": detected_lang == 'en',
                    "mixed": False,
                    "script_type": "romanized" if romanized_lang else "english",
                    "romanized_lang": romanized_lang,
                    "confidence": confidence
                }
            return {
                "romanized": False,
                "native": True,
                "english": False,
                "mixed": False,
                "script_type": "unknown"
            }
        
        start = time.perf_counter()
        
        # Use new Flipkart-style CodeMixDetector with language hint from Step 3
        result = self.code_mix_detector.detect(
            text, 
            tagged_tokens,
            language_hint=detected_lang,
            language_confidence=language_confidence
        )
        
        latency = (time.perf_counter() - start) * 1000
        
        # Extract results
        script_label = result.get('label', 'ambiguous')
        confidence = result.get('confidence', 0.0)
        detection_method = result.get('method', 'heuristic')
        detection_path = result.get('details', {}).get('reason', 'Unknown')
        
        # Map to old format for compatibility
        script_type_map = {
            'pure_english': 'english',
            'pure_native': 'native_script',
            'romanized_indic': 'romanized',
            'mixed': 'mixed',
            'ambiguous': 'unknown'
        }
        
        script_type = script_type_map.get(script_label, 'unknown')
        romanized = script_label in ['romanized_indic', 'mixed']
        native = script_label == 'pure_native'
        english = script_label == 'pure_english'
        mixed = script_label == 'mixed'
        
        # Get romanized language if available
        romanized_lang = result.get('details', {}).get('romanized_language')
        
        # Get skip_step5 flag from CodeMixDetector (Flipkart Fast Lane rules)
        skip_step5 = result.get('skip_step5', False)
        
        # Build result dictionary
        result = {
            "script_type": script_type,
            "romanized": romanized,
            "native": native,
            "english": english,
            "mixed": mixed,
            "romanized_lang": romanized_lang,
            "confidence": confidence,
            "skip_step5": skip_step5,
            "detection_method": detection_method,
            "detection_path": detection_path
        }
        
        # Print results
        print(f"Input:             {text}")
        print(f"Detection Method:  {detection_method} ({detection_path})")
        print(f"Script Label:      {script_label}")
        print(f"Script Type:       {script_type}")
        print(f"Romanized:         {romanized}")
        print(f"Native:            {native}")
        print(f"English:           {english}")
        print(f"Mixed:             {mixed}")
        if romanized_lang:
            print(f"Romanized Lang:    {romanized_lang}")
        print(f"Skip Step 5:       {'✅ YES' if skip_step5 else '❌ NO (needs transliteration)'}")
        print(f"Confidence:        {confidence:.2%}")
        print(f"Latency:           {latency:.2f}ms {'✅' if latency <= 6 else '⚠️'}")
        
        return result
    
    def step5_transliterate(self, text: str, script_flags: Dict, detected_lang: str) -> Dict[str, Any]:
        """Step 5: Transliteration (Romanized → Native Script)"""
        print("\n" + "─" * 80)
        print("STEP 5: Transliteration")
        print("─" * 80)
        
        if not self.transliteration_pipeline:
            print("❌ Step 5 not available")
            return {"normalized_query": text, "skipped": True}
        
        # Map language codes to IndicTrans2 format
        # Support both ISO codes (hi, bn) and Romanized codes (hi_Latn, bn_Latn)
        lang_map = {
            "hi": "hin_Deva",
            "hin_Deva": "hin_Deva",
            "hi_Latn": "hin_Deva",  # Romanized Hindi → Hindi Devanagari
            "bn": "ben_Beng",
            "ben_Beng": "ben_Beng",
            "bn_Latn": "ben_Beng",  # Romanized Bengali → Bengali script
            "te": "tel_Telu",
            "tel_Telu": "tel_Telu",
            "ta": "tam_Taml",
            "tam_Taml": "tam_Taml",
            "mr": "mar_Deva",
            "mar_Deva": "mar_Deva",
            "gu": "guj_Gujr",
            "guj_Gujr": "guj_Gujr",
            "kn": "kan_Knda",
            "kan_Knda": "kan_Knda",
            "ml": "mal_Mlym",
            "mal_Mlym": "mal_Mlym",
            "pa": "pan_Guru",
            "pan_Guru": "pan_Guru",
            "en": "en",  # English - no transliteration (default)
            
            # English names from Step 4 code_mix_detector (CRITICAL!)
            "hindi": "hin_Deva",
            "bengali": "ben_Beng",
            "telugu": "tel_Telu",
            "tamil": "tam_Taml",
            "marathi": "mar_Deva",
            "gujarati": "guj_Gujr",
            "kannada": "kan_Knda",
            "malayalam": "mal_Mlym",
            "punjabi": "pan_Guru",
        }
        
        # Use romanized_lang from Step 4 if available, otherwise use detected_lang from Step 3
        romanized_lang = script_flags.get("romanized_lang")
        lang_to_use = romanized_lang if romanized_lang else detected_lang
        
        target_lang = lang_map.get(lang_to_use, "hin_Deva")
        
        # CRITICAL: If romanized Indic detected, ensure we transliterate (not pass through)
        if script_flags.get("romanized", False) and target_lang == "en":
            # Romanized was detected but no specific language, default to Hindi
            target_lang = "hin_Deva"
        
        # Create language flags for Step 5
        language_flags = {
            "romanized": script_flags.get("romanized", False),
            "native": script_flags.get("native", False),
            "english": script_flags.get("english", False),
            "mixed": script_flags.get("mixed", False)
        }
        
        start = time.perf_counter()
        
        # Transliterate
        result = self.transliteration_pipeline.process(
            query=text,
            language_flags=language_flags,
            target_lang=target_lang
        )
        
        latency = (time.perf_counter() - start) * 1000
        
        print(f"Input:           {text}")
        print(f"Target Language: {target_lang}")
        print(f"Output:          {result.normalized_query}")
        print(f"Romanized:       {result.romanized_detected}")
        print(f"Cache Hit:       {result.cache_hit}")
        print(f"Latency:         {result.latency_ms:.2f}ms")
        
        return result.to_dict()
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process query through all 5 steps"""
        print("\n" + "=" * 80)
        print(f"PROCESSING QUERY: {query}")
        print("=" * 80)
        
        pipeline_start = time.perf_counter()
        
        # Step 1: Input Normalization
        step1_result = self.step1_normalize(query)
        normalized_text = step1_result.get("normalized", query)
        
        # Step 2: Spell Correction & Query Rewrite
        step2_result = self.step2_spell_correction(normalized_text)
        corrected_text = step2_result.get("corrected", normalized_text)
        
        # Step 3: Tokenization, Script Detection & Language Detection
        step3_result = self.step3_tokenize_and_detect_script(corrected_text)
        tokens = step3_result.get("tokens", [])
        detected_lang = step3_result.get("language", "en")
        language_confidence = step3_result.get("language_confidence", 0.0)
        tagged_tokens = step3_result.get("tagged_tokens", [])
        
        # Step 4: Code-Mix Analysis & Script Detection (Flipkart-Style)
        step4_result = self.step4_detect_script(corrected_text, detected_lang, language_confidence, tagged_tokens)
        
        # Step 5: Transliteration
        step5_result = self.step5_transliterate(
            corrected_text,
            step4_result,
            detected_lang
        )
        
        total_latency = (time.perf_counter() - pipeline_start) * 1000
        
        # Final result
        print("\n" + "=" * 80)
        print("PIPELINE SUMMARY")
        print("=" * 80)
        print(f"Original Query:    {query}")
        print(f"Normalized:        {normalized_text}")
        print(f"Spell-Corrected:   {corrected_text}")
        print(f"Detected Language: {detected_lang} ({language_confidence:.2%} confidence)")
        print(f"Script Type:       {step4_result.get('script_type', 'unknown')}")
        print(f"Final Output:      {step5_result.get('normalized_query', normalized_text)}")
        print(f"Total Latency:     {total_latency:.2f}ms")
        print("=" * 80)
        
        return {
            "original": query,
            "step1": step1_result,
            "step2": step2_result,
            "step3": step3_result,
            "step4": step4_result,
            "step5": step5_result,
            "total_latency_ms": total_latency
        }
    
    def interactive_mode(self):
        """Interactive mode - user inputs queries"""
        print("\n" + "=" * 80)
        print("INTERACTIVE MODE - Steps 1-5 Pipeline Test")
        print("=" * 80)
        print()
        print("Enter queries to test the complete preprocessing pipeline.")
        print("Type 'quit' or 'exit' to stop.")
        print()
        print("Example queries:")
        print("  - mujhe headphone chahiye (Romanized Hindi)")
        print("  - amake earphone dekhao (Romanized Bengali)")
        print("  - wireless headphone under 5000 (English)")
        print("  - मुझे हेडफोन चाहिए (Native Hindi)")
        print("  - আমাকে ইয়ারফোন দেখাও (Native Bengali)")
        print()
        print("=" * 80)
        print()
        
        query_count = 0
        
        while True:
            try:
                # Get user input
                query = input(f"\n[Query {query_count + 1}] Enter your query: ").strip()
                
                # Check for exit
                if query.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Exiting interactive mode...")
                    break
                
                # Skip empty queries
                if not query:
                    print("⚠️  Empty query, please try again.")
                    continue
                
                # Process query
                result = self.process_query(query)
                query_count += 1
                
            except EOFError:
                # EOF reached (stdin closed or Ctrl+D) - exit gracefully
                print("\n\n👋 End of input. Exiting...")
                break
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted by user. Exiting...")
                break
            except Exception as e:
                logger.error(f"Error processing query: {e}", exc_info=True)
                print(f"\n❌ Error: {e}")
                print("Please try another query.\n")
        
        # Final summary
        print("\n" + "=" * 80)
        print("SESSION SUMMARY")
        print("=" * 80)
        print(f"Total queries processed: {query_count}")
        
        if self.transliteration_pipeline:
            stats = self.transliteration_pipeline.get_stats()
            print(f"Cache hit rate: {stats.get('cache_hit_rate', 'N/A')}")
            print(f"Cache size: {stats.get('cache_size', 'N/A')}")
        
        print("=" * 80)
        print("\n✅ Test complete!")


def run_demo_queries():
    """Run predefined demo queries"""
    print("\n" + "=" * 80)
    print("DEMO MODE - Running Predefined Test Queries")
    print("=" * 80)
    print()
    
    pipeline = CompletePipelineTest()
    
    demo_queries = [
        "mujhe headphone chahiye",                              # Romanized Hindi
        "amake 12000 taka damer earphone dekhao",              # Romanized Bengali
        "wireless headphone under 5000",                        # English
        "naku wireless earbuds kavali",                         # Romanized Telugu
        "मुझे हेडफोन चाहिए",                                   # Native Hindi
        "আমাকে ইয়ারফোন দেখাও",                                 # Native Bengali
        "bluetooth headphone kharidna hai",                     # Romanized Hindi + English
    ]
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n{'=' * 80}")
        print(f"DEMO QUERY {i}/{len(demo_queries)}")
        print(f"{'=' * 80}")
        
        pipeline.process_query(query)
        
        # Pause between queries
        if i < len(demo_queries):
            time.sleep(1)
    
    print("\n" + "=" * 80)
    print("✅ DEMO COMPLETE")
    print("=" * 80)


def main():
    """Main entry point"""
    print("\n" + "=" * 100)
    print(" " * 20 + "STEPS 1-5: PREPROCESSING PIPELINE TEST")
    print("=" * 100)
    print()
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        # Run demo mode
        run_demo_queries()
    else:
        # Run interactive mode
        pipeline = CompletePipelineTest()
        pipeline.interactive_mode()


if __name__ == "__main__":
    main()
