"""
Code-Mix Detection Module - Version 1.0.0 (Production)

STEP 4 of 10-Step Engineering Sprint: Lightweight Code-Mix Detection

Purpose: Decide if query is Romanized Indic, native script, pure English, or mixed
Target: 2-6ms latency

Features:
1. Heuristic check: Latin tokens + transliteration table presence → Romanized Indic
2. Distilled classifier: Binary/multi-class labeling {en, bn_roman, bn_native, mixed, other}
3. Token-level and query-level classification

Tools:
- Heuristic patterns (fast, zero latency overhead)
- ONNX Runtime quantized model (2-6ms)
- Script tags from Step 3 (tokenizer)

Classification Labels:
- pure_english: English-only query ("iphone 12 pro")
- pure_native: Native script only ("वायरलेस हेडफोन")
- romanized_indic: Romanized Indian language ("bluetooth headphone kharidna hai")
- mixed: Mix of scripts ("iphone হেডফোন")
- ambiguous: Uncertain (needs classifier)

Latency: 2-6 ms (quantized model)
"""

import logging
import re
from typing import Dict, List, Tuple, Optional, TYPE_CHECKING
from functools import lru_cache

if TYPE_CHECKING:
    import numpy as np

logger = logging.getLogger(__name__)

# Try to import ONNX Runtime for quantized model inference
try:
    import onnxruntime as ort
    import numpy as np
    ONNX_AVAILABLE = True
    logger.info("ONNX Runtime available for code-mix classification")
except ImportError:
    ONNX_AVAILABLE = False
    logger.warning("ONNX Runtime not installed. Using heuristic-only detection.")


class CodeMixDetector:
    """
    Production-grade code-mix detector (Step 4)
    
    Features:
    - Heuristic detection (fast, pattern-based)
    - Script-based classification using Step 3 tags
    - Romanization detection via transliteration tables
    - ONNX quantized classifier (optional, for ambiguous cases)
    
    Performance: 2-6ms target
    """
    
    # Common Romanized Indic patterns (Hindi/Bengali/Tamil romanization)
    ROMANIZED_PATTERNS = {
        # Hindi romanization markers
        'hindi': [
            r'\b(hai|hain|ho|ka|ki|ke|ko|se|me|ne|bhi|nahi|kya|kaise|kahan)\b',
            r'\b(aur|yah|woh|ek|do|teen|char|panch|saat|aath|nau|das)\b',
            r'\b(kharidna|chahiye|chahta|chahti|milega|kitna|kitne)\b',
            r'\b(accha|bahut|bohot|thoda|jyada|kam|zyada)\b',
            r'\b(mujhe|mujhko|tumhe|tumko|usko|dikhao|dikhaye|dikhaiye)\b',
        ],
        # Bengali romanization markers
        'bengali': [
            r'\b(ache|achhe|hobe|korbo|kora|kore|keno|kothay|kivabe)\b',
            r'\b(taka|takar|dam|dam|koto|kemon|bhalo|kharap)\b',
            r'\b(ekta|duto|tin|char|panch|choy|saat|aat|noy|dosh)\b',
            r'\b(ami|tumi|apni|amar|tomar|apnar|oder|tader)\b',
            r'\b(amake|amae|amay|tomake|tomay|dekhao|dekhaye|ar|aar|ebong)\b',
        ],
        # Tamil romanization markers
        'tamil': [
            r'\b(enna|eppadi|enga|eppo|yaar|yenna|yedhu)\b',
            r'\b(irukku|irukkum|seiyyum|panna|pannunga)\b',
            r'\b(nalla|romba|konjam|adhigam|kammiya)\b',
        ],
        # Telugu romanization markers
        'telugu': [
            r'\b(undi|undhi|cheyyi|cheyyandi|ela|ekkada|eppudu)\b',
            r'\b(manchidi|chala|konchem|ekkuva|thakkuva)\b',
        ],
    }
    
    # English-only markers (to distinguish from romanized)
    PURE_ENGLISH_PATTERNS = [
        r'\b(the|a|an|is|are|was|were|be|been|being)\b',
        r'\b(have|has|had|do|does|did|will|would|should|could)\b',
        r'\b(in|on|at|to|from|with|by|for|of|about|under|over|below|above)\b',
        r'\b(this|that|these|those|what|which|who|when|where)\b',
        r'\b(best|good|great|nice|cheap|expensive|quality|latest|new)\b',
        r'\b(buy|purchase|order|price|cost|sale|discount|offer|deal)\b',
        r'\b(phone|mobile|smartphone|laptop|tablet|headphone|camera|charger)\b',
        r'\b(wireless|bluetooth|wired|fast|charging|battery|storage)\b',
        r'\b(samsung|iphone|oneplus|realme|xiaomi|oppo|vivo|nokia|apple)\b',
        r'\b(rupees|india|online|shopping|delivery|warranty)\b',
    ]
    
    # Transliteration confidence markers
    TRANSLIT_MARKERS = {
        # Character sequences that indicate romanized Indic
        'high_confidence': [
            r'[bcdfghjklmnpqrstvwxyz]{3,}[aeiou][bcdfghjklmnpqrstvwxyz]{2,}',  # Complex consonant clusters
            r'\b[kg]h[aeiou]',  # gh, kh patterns
            r'\b[cj]h[aeiou]',  # ch, jh patterns
            r'[td]h[aeiou]',    # th, dh patterns
        ],
    }
    
    def __init__(self, model_path: Optional[str] = None, use_onnx: bool = False):
        """
        Initialize CodeMixDetector
        
        Args:
            model_path: Path to ONNX quantized classifier model (optional)
            use_onnx: Enable ONNX model for ambiguous cases
        """
        self.use_onnx = use_onnx and ONNX_AVAILABLE
        self.onnx_session = None
        
        # Load ONNX model if available
        if self.use_onnx and model_path:
            try:
                self.onnx_session = ort.InferenceSession(model_path)
                logger.info(f"ONNX code-mix classifier loaded from {model_path}")
            except Exception as e:
                logger.warning(f"Failed to load ONNX model: {e}. Using heuristics only.")
                self.onnx_session = None
        
        # Compile patterns for speed
        self.romanized_patterns_compiled = {
            lang: [re.compile(p, re.IGNORECASE) for p in patterns]
            for lang, patterns in self.ROMANIZED_PATTERNS.items()
        }
        
        self.english_patterns_compiled = [
            re.compile(p, re.IGNORECASE) for p in self.PURE_ENGLISH_PATTERNS
        ]
        
        self.translit_patterns_compiled = [
            re.compile(p, re.IGNORECASE) for p in self.TRANSLIT_MARKERS['high_confidence']
        ]
        
        logger.info(f"CodeMixDetector initialized (ONNX: {self.use_onnx})")
    
    @lru_cache(maxsize=1000)
    def detect_romanized_language(self, text: str) -> Tuple[str, float]:
        """
        Detect which Romanized Indic language (if any)
        
        Args:
            text: Input text (lowercase)
            
        Returns:
            Tuple of (language, confidence)
            Examples: ('hindi', 0.8), ('bengali', 0.6), ('none', 0.0)
        """
        if not text:
            return ('none', 0.0)
        
        # Count matches for each language
        lang_scores = {}
        
        for lang, patterns in self.romanized_patterns_compiled.items():
            # Count INDIVIDUAL word matches (not just pattern groups)
            total_matches = 0
            for p in patterns:
                total_matches += len(p.findall(text))
            
            if total_matches > 0:
                # Confidence based on number of word matches
                # 2+ matches = high confidence
                confidence = min(total_matches / 2.0, 1.0)  # Cap at 1.0
                lang_scores[lang] = confidence
        
        if not lang_scores:
            return ('none', 0.0)
        
        # Return language with highest confidence
        best_lang = max(lang_scores.items(), key=lambda x: x[1])
        return best_lang
    
    def count_english_markers(self, text: str) -> int:
        """Count English-specific markers in text"""
        count = sum(1 for p in self.english_patterns_compiled if p.search(text))
        return count
    
    def has_transliteration_markers(self, text: str) -> bool:
        """Check if text has transliteration patterns (consonant clusters, etc.)"""
        return any(p.search(text) for p in self.translit_patterns_compiled)
    
    def classify_by_script(self, tagged_tokens: List[Dict]) -> Dict:
        """
        Classify query based on script distribution from Step 3
        
        Args:
            tagged_tokens: List of tokens with script tags from tokenizer
            
        Returns:
            Dict with:
            - script_distribution: Percentage of each script
            - dominant_script: Most common script
            - is_mixed: Whether multiple scripts present
        """
        if not tagged_tokens:
            return {
                'script_distribution': {},
                'dominant_script': 'Unknown',
                'is_mixed': False
            }
        
        # Count scripts
        script_counts = {}
        for token in tagged_tokens:
            script = token.get('script', 'Unknown')
            # Skip digits and unknown
            if script not in ['Unknown', 'Digit', 'Space', 'Other']:
                script_counts[script] = script_counts.get(script, 0) + 1
        
        if not script_counts:
            return {
                'script_distribution': {},
                'dominant_script': 'Unknown',
                'is_mixed': False
            }
        
        # Calculate percentages
        total = sum(script_counts.values())
        script_distribution = {
            script: (count / total) * 100
            for script, count in script_counts.items()
        }
        
        # Dominant script
        dominant_script = max(script_counts.items(), key=lambda x: x[1])[0]
        
        # Mixed if more than one script with >10% representation
        significant_scripts = [s for s, pct in script_distribution.items() if pct > 10]
        is_mixed = len(significant_scripts) > 1
        
        return {
            'script_distribution': script_distribution,
            'dominant_script': dominant_script,
            'is_mixed': is_mixed
        }
    
    def detect_heuristic(self, text: str, tagged_tokens: List[Dict] = None, 
                        language_hint: str = None, language_confidence: float = 0.0) -> Dict:
        """
        Heuristic-based code-mix detection (Flipkart Fast Lane approach)
        
        **FLIPKART FAST LANE (Handles 80-90% of queries in <1ms):**
        
        Rule A: Pure Native Script
        - Logic: All word tokens tagged as native script (Bengali, Hindi, etc.) or Numeric
                 AND fastText hint is native language (bn, hi, ta, etc.)
        - Example: "আমাকে ২০০০ টাকা জামা দেখাও" 
                   Scripts: [Bengali, Bengali, Bengali, Bengali, Bengali]
                   Hint: bn → Matches Rule A
        - Action: Flag as pure_native → SKIP Step 5
        
        Rule B: Pure English
        - Logic: All word tokens tagged as Latin or Numeric
                 AND fastText hint is 'en' with high confidence (>85-90%)
        - Example: "show redmi note 12 pro"
                   Scripts: [Latin, Latin, Latin, Latin, Latin]
                   Hint: en (99% confidence) → Matches Rule B
        - Action: Flag as pure_english → SKIP Step 5
        
        **If NEITHER rule matches → Returns 'ambiguous' → Sends to Smart Checkpoint (ML)**
        
        Args:
            text: Input text (normalized and corrected)
            tagged_tokens: Script-tagged tokens from Step 3 (REQUIRED)
            language_hint: Language code from Step 3 fastText (e.g., 'bn', 'hi', 'en')
            language_confidence: Confidence score from Step 3 (0-1)
            
        Returns:
            Dict with:
            - label: 'pure_native', 'pure_english', or 'ambiguous'
            - confidence: Confidence score (0-1)
            - method: 'heuristic' or 'fast_lane'
            - details: Reason for classification
        """
        if not text or not tagged_tokens:
            return {
                'label': 'ambiguous',
                'confidence': 0.5,
                'method': 'heuristic',
                'details': {'reason': 'Missing input or script tags'}
            }
        
        # Define native scripts and languages
        native_scripts = ['Devanagari', 'Bengali', 'Tamil', 'Telugu', 'Gujarati', 
                         'Kannada', 'Malayalam', 'Punjabi', 'Odia', 'Gurmukhi']
        native_langs = ['hi', 'bn', 'ta', 'te', 'gu', 'kn', 'ml', 'pa', 'or', 'mr', 'sa', 'as']
        
        # Extract script tags from tagged_tokens (ignore Number and Other)
        word_scripts = []
        for token_info in tagged_tokens:
            script = token_info.get('script', 'Unknown')
            # Only consider word scripts (ignore numbers, punctuation, etc.)
            if script not in ['Number', 'Digit', 'Other', 'Unknown', 'Space']:
                word_scripts.append(script)
        
        if not word_scripts:
            # Only numbers/punctuation - ambiguous
            return {
                'label': 'ambiguous',
                'confidence': 0.5,
                'method': 'heuristic',
                'details': {'reason': 'No word tokens found'}
            }
        
        # Check if all word scripts are the same type
        all_native = all(s in native_scripts for s in word_scripts)
        all_latin = all(s == 'Latin' for s in word_scripts)
        
        # ================================================================
        # RULE A: Pure Native Script ⚡
        # ================================================================
        if all_native and language_hint in native_langs:
            return {
                'label': 'pure_native',
                'confidence': 0.95,
                'method': 'fast_lane',
                'details': {
                    'rule': 'Rule A',
                    'scripts': list(set(word_scripts)),
                    'language': language_hint,
                    'reason': f'Pure Native Script: All tokens in {set(word_scripts)}, fastText={language_hint}'
                }
            }
        
        # ================================================================
        # RULE B: Pure English ⚡
        # ================================================================
        # CRITICAL: Confidence threshold tuning (currently 85%)
        # - Too low: Misclassifies romanized queries as English
        # - Too high: Sends clear English to ML unnecessarily
        CONFIDENCE_THRESHOLD = 0.85
        
        if all_latin and language_hint == 'en' and language_confidence > CONFIDENCE_THRESHOLD:
            return {
                'label': 'pure_english',
                'confidence': language_confidence,
                'method': 'fast_lane',
                'details': {
                    'rule': 'Rule B',
                    'scripts': ['Latin'],
                    'language': 'en',
                    'fasttext_confidence': language_confidence,
                    'threshold': CONFIDENCE_THRESHOLD,
                    'reason': f'Pure English: All Latin, fastText=en ({language_confidence:.2%} > {CONFIDENCE_THRESHOLD:.0%})'
                }
            }
        
        # ================================================================
        # No Fast Lane match → Send to Smart Checkpoint (ML)
        # ================================================================
        # Possible cases:
        # - Romanized Indic: All Latin, but hint is bn/hi/ta
        # - Mixed Script: Contains both Latin and native tokens
        # - Low-Confidence English: All Latin, en hint, but confidence < 85%
        
        return {
            'label': 'ambiguous',
            'confidence': 0.5,
            'method': 'heuristic',
            'details': {
                'reason': 'Fast Lane rules did not match - needs Smart Checkpoint',
                'scripts': list(set(word_scripts)),
                'language_hint': language_hint,
                'language_confidence': language_confidence,
                'all_native': all_native,
                'all_latin': all_latin,
                'suggestion': 'Route to ML classifier for accurate classification'
            }
        }
    
    def _classify_smart_checkpoint(self, text: str, tagged_tokens: List[Dict] = None,
                                   language_hint: str = None, language_confidence: float = 0.0) -> Dict:
        """
        Smart Checkpoint (ML Classification) - Handles ambiguous cases
        
        **FLIPKART SMART CHECKPOINT (Runs only when Fast Lane fails, handles remaining 10-20%):**
        
        This lightweight ML model handles:
        - Romanized Indic: All Latin, but hint is bn/hi/ta (e.g., "amake earphone dekhao")
        - Mixed Script: Contains both Latin and native tokens (e.g., "amake ২০০০ taka earphone")
        - Low-Confidence English: All Latin, en hint, but confidence < 85%
        
        Model:
        - Distilled transformer (tiny BERT/XLM-R) or sophisticated FastText classifier
        - Trained on Flipkart's massive query dataset
        - Quantized to INT8 for speed
        - Served via ONNX Runtime
        - Target latency: 2-6ms
        
        Args:
            text: Input text
            tagged_tokens: Script-tagged tokens from Step 3
            language_hint: Language from fastText
            language_confidence: Confidence from fastText
            
        Returns:
            Dict with classification (en, bn_native, bn_roman, hi_roman, mixed, etc.)
        """
        # If ONNX model available, use it
        if self.onnx_session:
            return self._classify_with_onnx(text, tagged_tokens)
        
        # Fallback: Use pattern-based heuristics (less accurate but faster)
        # This is a simplified version when ML model is not available
        
        text_lower = text.lower()
        
        # Extract script info
        word_scripts = []
        for token_info in tagged_tokens:
            script = token_info.get('script', 'Unknown')
            if script not in ['Number', 'Digit', 'Other', 'Unknown', 'Space']:
                word_scripts.append(script)
        
        native_scripts = ['Devanagari', 'Bengali', 'Tamil', 'Telugu', 'Gujarati', 
                         'Kannada', 'Malayalam', 'Punjabi', 'Odia', 'Gurmukhi']
        native_langs = ['hi', 'bn', 'ta', 'te', 'gu', 'kn', 'ml', 'pa', 'or', 'mr', 'sa', 'as']
        
        has_latin = 'Latin' in word_scripts
        has_native = any(s in native_scripts for s in word_scripts)
        
        # Mixed script detection
        if has_latin and has_native:
            return {
                'label': 'mixed',
                'confidence': 0.85,
                'method': 'smart_checkpoint_fallback',
                'details': {
                    'reason': 'Mixed script detected (Latin + Native)',
                    'scripts': list(set(word_scripts))
                }
            }
        
        # Romanized Indic detection (Latin + Indic language hint)
        if has_latin and language_hint in native_langs:
            # Detect which romanized language using patterns
            romanized_lang, romanized_conf = self.detect_romanized_language(text_lower)
            return {
                'label': 'romanized_indic',
                'confidence': max(romanized_conf, 0.70),
                'method': 'smart_checkpoint_fallback',
                'details': {
                    'reason': f'Romanized {language_hint.upper()} detected',
                    'romanized_language': romanized_lang,
                    'language_hint': language_hint
                }
            }
        
        # Low-confidence English - check for English markers
        if has_latin and language_hint == 'en':
            english_count = self.count_english_markers(text_lower)
            if english_count >= 2:
                return {
                    'label': 'pure_english',
                    'confidence': 0.75,
                    'method': 'smart_checkpoint_fallback',
                    'details': {
                        'reason': 'Low-confidence English confirmed via markers',
                        'english_markers': english_count
                    }
                }
            else:
                # Might be romanized - check patterns
                romanized_lang, romanized_conf = self.detect_romanized_language(text_lower)
                if romanized_conf > 0.3:
                    return {
                        'label': 'romanized_indic',
                        'confidence': romanized_conf,
                        'method': 'smart_checkpoint_fallback',
                        'details': {
                            'reason': f'Romanized {romanized_lang} patterns found',
                            'romanized_language': romanized_lang
                        }
                    }
        
        # Unable to classify with confidence
        return {
            'label': 'ambiguous',
            'confidence': 0.5,
            'method': 'smart_checkpoint_fallback',
            'details': {
                'reason': 'Unable to classify confidently - ML model recommended'
            }
        }
    
    def _classify_with_onnx(self, text: str, tagged_tokens: List[Dict] = None) -> Dict:
        """
        ONNX ML model classification (actual Smart Checkpoint implementation)
        
        Args:
            text: Input text
            tagged_tokens: Script-tagged tokens
            
        Returns:
            Dict with classification from ML model
        """
        try:
            # Prepare features
            features = self._prepare_onnx_features(text, tagged_tokens)
            
            # Get input name from model
            input_name = self.onnx_session.get_inputs()[0].name
            
            # Run inference
            outputs = self.onnx_session.run(None, {input_name: features})
            
            # Parse output (assumes model outputs class probabilities)
            # Expected classes: [pure_english, pure_native, romanized_indic, mixed, ambiguous]
            class_labels = ['pure_english', 'pure_native', 'romanized_indic', 'mixed', 'ambiguous']
            
            if len(outputs) > 0:
                probabilities = outputs[0][0]  # Shape: (num_classes,)
                predicted_class = int(probabilities.argmax())
                confidence = float(probabilities[predicted_class])
                
                return {
                    'label': class_labels[predicted_class],
                    'confidence': confidence,
                    'method': 'smart_checkpoint_ml',
                    'details': {
                        'reason': 'ONNX quantized model prediction',
                        'all_probabilities': {
                            label: float(prob) 
                            for label, prob in zip(class_labels, probabilities)
                        }
                    }
                }
            else:
                raise ValueError("No output from ONNX model")
                
        except Exception as e:
            logger.warning(f"ONNX inference failed: {e}")
            # Fall back to pattern-based
            return {
                'label': 'ambiguous',
                'confidence': 0.5,
                'method': 'onnx_failed',
                'details': {
                    'error': str(e),
                    'reason': 'ONNX inference failed, recommend using pattern fallback'
                }
            }
    
    def _prepare_onnx_features(self, text: str, tagged_tokens: List[Dict] = None):
        """
        Prepare feature vector for ONNX model
        
        Args:
            text: Input text
            tagged_tokens: Optional script-tagged tokens
            
        Returns:
            NumPy array of features (shape: 1 x num_features)
        """
        if not ONNX_AVAILABLE:
            raise RuntimeError("NumPy not available")
        
        # Feature extraction for ONNX model (example features)
        features = []
        
        # 1. Script distribution features (if available)
        if tagged_tokens:
            script_info = self.classify_by_script(tagged_tokens)
            scripts = script_info.get('script_distribution', {})
            
            # One-hot encode scripts (Latin, Devanagari, Bengali, Tamil, Telugu, Other)
            features.extend([
                scripts.get('Latin', 0.0) / 100.0,
                scripts.get('Devanagari', 0.0) / 100.0,
                scripts.get('Bengali', 0.0) / 100.0,
                scripts.get('Tamil', 0.0) / 100.0,
                scripts.get('Telugu', 0.0) / 100.0,
            ])
            
            # Is mixed script
            features.append(1.0 if script_info.get('is_mixed') else 0.0)
        else:
            # No script info - use zeros
            features.extend([0.0] * 6)
        
        # 2. Text-based features
        text_lower = text.lower()
        
        # English marker count (normalized)
        english_count = self.count_english_markers(text_lower)
        features.append(min(english_count / 5.0, 1.0))  # Cap at 1.0
        
        # Romanized language confidence
        romanized_lang, romanized_conf = self.detect_romanized_language(text_lower)
        features.append(romanized_conf)
        
        # Transliteration markers
        features.append(1.0 if self.has_transliteration_markers(text_lower) else 0.0)
        
        # 3. Length features
        token_count = len(text_lower.split())
        features.append(min(token_count / 10.0, 1.0))  # Normalized token count
        
        # Character count
        features.append(min(len(text_lower) / 100.0, 1.0))  # Normalized char count
        
        # 4. Language-specific pattern matches
        for lang in ['hindi', 'bengali', 'tamil', 'telugu']:
            if lang in self.romanized_patterns_compiled:
                matches = sum(1 for p in self.romanized_patterns_compiled[lang] if p.search(text_lower))
                features.append(min(matches / 3.0, 1.0))
            else:
                features.append(0.0)
        
        # Convert to numpy array with shape (1, num_features)
        return np.array([features], dtype=np.float32)
    
    def _classify_with_onnx(self, text: str, tagged_tokens: List[Dict] = None) -> Dict:
        """
        Classify using ONNX quantized model
        
        Args:
            text: Input text
            tagged_tokens: Optional script-tagged tokens
            
        Returns:
            Classification dict
        """
        try:
            # Prepare features
            features = self._prepare_onnx_features(text, tagged_tokens)
            
            # Get input name from model
            input_name = self.onnx_session.get_inputs()[0].name
            
            # Run inference
            outputs = self.onnx_session.run(None, {input_name: features})
            
            # Parse output (assumes model outputs class probabilities)
            # Expected classes: [pure_english, pure_native, romanized_indic, mixed, ambiguous]
            class_labels = ['pure_english', 'pure_native', 'romanized_indic', 'mixed', 'ambiguous']
            
            if len(outputs) > 0:
                probabilities = outputs[0][0]  # Shape: (num_classes,)
                predicted_class = int(probabilities.argmax())
                confidence = float(probabilities[predicted_class])
                
                return {
                    'label': class_labels[predicted_class],
                    'confidence': confidence,
                    'method': 'onnx',
                    'details': {
                        'reason': 'ONNX quantized model prediction',
                        'all_probabilities': {
                            label: float(prob) 
                            for label, prob in zip(class_labels, probabilities)
                        }
                    }
                }
            else:
                raise ValueError("No output from ONNX model")
                
        except Exception as e:
            logger.warning(f"ONNX inference failed: {e}")
            # Fallback to heuristic
            return {
                'label': 'ambiguous',
                'confidence': 0.5,
                'method': 'onnx_failed',
                'details': {
                    'error': str(e),
                    'reason': 'ONNX inference failed, using heuristic fallback'
                }
            }
    
    def detect(self, text: str, tagged_tokens: List[Dict] = None, 
              language_hint: str = None, language_confidence: float = 0.0,
              use_smart_checkpoint: bool = True) -> Dict:
        """
        Main detection method (Flipkart Fast Lane + Smart Checkpoint)
        
        **FLIPKART TWO-STAGE APPROACH:**
        1. Fast Lane (Heuristics): Handles 80-90% of queries in <1ms
           - Rule A: Pure Native Script → Skip Step 5
           - Rule B: Pure English (high confidence) → Skip Step 5
        
        2. Smart Checkpoint (ML): Handles remaining 10-20% in 2-6ms
           - Romanized Indic, Mixed Script, Low-Confidence English
           - Uses lightweight distilled model (quantized INT8)
           - Served via ONNX Runtime
        
        Args:
            text: Input text (normalized and corrected from Steps 1-2)
            tagged_tokens: Script-tagged tokens from Step 3 (REQUIRED)
            language_hint: Language code from Step 3 (e.g., 'bn', 'hi', 'en')
            language_confidence: Confidence from Step 3 (0-1)
            use_smart_checkpoint: Enable Smart Checkpoint for ambiguous cases
            
        Returns:
            Dict with classification results and skip_step5 flag
        """
        # ================================================================
        # STAGE 1: Fast Lane (Heuristics) ⚡
        # ================================================================
        result = self.detect_heuristic(text, tagged_tokens, language_hint, language_confidence)
        
        # Fast Lane hit! (80-90% of queries)
        if result['label'] in ['pure_native', 'pure_english']:
            logger.debug(f"⚡ Fast Lane: {result['label']} detected (<1ms)")
            result['skip_step5'] = self.should_skip_step5(result)
            return result
        
        # ================================================================
        # STAGE 2: Smart Checkpoint (ML Classification) 🧠
        # ================================================================
        if result['label'] == 'ambiguous' and use_smart_checkpoint:
            logger.debug(f"🧠 Smart Checkpoint: Running ML classification for ambiguous case")
            ml_result = self._classify_smart_checkpoint(text, tagged_tokens, language_hint, language_confidence)
            
            # Use ML result if confidence is reasonable (>0.6)
            if ml_result['confidence'] > 0.6:
                result = ml_result
                result['details']['fast_lane_result'] = 'ambiguous'
                logger.debug(f"🧠 Smart Checkpoint: Classified as {ml_result['label']} ({ml_result['confidence']:.2%})")
            else:
                # Low confidence from ML - keep ambiguous
                result['details']['smart_checkpoint_low_confidence'] = ml_result['confidence']
                logger.debug(f"🧠 Smart Checkpoint: Low confidence ({ml_result['confidence']:.2%}), keeping ambiguous")
        elif result['label'] == 'ambiguous':
            result['details']['smart_checkpoint_disabled'] = True
            logger.debug("Smart Checkpoint disabled - returning ambiguous")
        
        # Add skip_step5 flag
        result['skip_step5'] = self.should_skip_step5(result)
        
        return result
    
    def should_skip_step5(self, detection_result: Dict) -> bool:
        """
        Determine if Step 5 (Transliteration) should be skipped
        
        **Flipkart Fast Lane Rules (Updated):**
        - Rule A: Pure Native Script → SKIP Step 5 (already in native script, confidence ≥75%)
        - Rule B: Pure English → SKIP Step 5 (confidence ≥75%)
        - Low-Confidence (<75%) → CONTINUE to Step 5 (might be romanized)
        - Romanized Indic → CONTINUE to Step 5 (needs transliteration)
        - Mixed Script → CONTINUE to Step 5 (needs processing)
        
        **NEW THRESHOLD: 75%** (lowered from 85-90%)
        Rationale: If Step 4 is 75%+ confident it's pure English/native, trust it.
        
        Args:
            detection_result: Result from detect() method
            
        Returns:
            True if Step 5 should be skipped, False otherwise
        """
        label = detection_result.get('label', 'unknown')
        confidence = detection_result.get('confidence', 0.0)
        method = detection_result.get('method', '')
        
        # Rule A: Pure Native Script → SKIP (confidence ≥ 75%)
        # Must be native script detected with reasonable confidence
        if label == 'pure_native' and confidence >= 0.75:
            logger.debug(f"✅ SKIP Step 5: Pure native script (confidence={confidence:.2%})")
            return True
        
        # Rule B: Pure English → SKIP (confidence ≥ 75%)
        # NEW: Lowered threshold from 85-90% to 75% as requested
        # If Step 4 is 75%+ confident it's English, trust it and skip transliteration
        if label == 'pure_english':
            if confidence >= 0.75:
                logger.debug(f"✅ SKIP Step 5: Pure English (confidence={confidence:.2%}, method={method})")
                return True
            else:
                logger.debug(f"⚠️ CONTINUE to Step 5: Low-confidence English ({confidence:.2%}), might be romanized")
                return False
        
        # All other cases → CONTINUE to Step 5
        # - romanized_indic: Needs transliteration
        # - mixed: Needs processing
        # - ambiguous: Better to process than skip
        # - unknown: Better to process than skip
        logger.debug(f"⚠️ CONTINUE to Step 5: {label} (confidence={confidence:.2%})")
        return False
    
    def get_stats(self) -> Dict:
        """Get detection statistics (placeholder for compatibility)"""
        return {
            'total_detections': 0,
            'heuristic_count': 0,
            'onnx_count': 0,
            'onnx_available': self.use_onnx,
        }


# Convenience function for quick detection
def detect_code_mix(text: str, tagged_tokens: List[Dict] = None) -> Dict:
    """
    Quick code-mix detection using heuristics
    
    Args:
        text: Input text
        tagged_tokens: Optional script-tagged tokens
        
    Returns:
        Classification dict
    """
    detector = CodeMixDetector(use_onnx=False)
    return detector.detect(text, tagged_tokens)
