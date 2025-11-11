"""
Feature & Price Extractor - Extracts product specifications and prices
Uses regex patterns and spaCy NER for structured information extraction
"""

import re
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Try to import spaCy for NER
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


class FeatureExtractor:
    """Extracts product features, specifications, and prices from text"""
    
    # Feature extraction patterns
    PATTERNS = {
        # Storage/Memory - EXPANDED: storage keyword OR standalone GB/TB in product context
        'storage': re.compile(
            r'(\d+)\s*(gb|tb)\s+(?:storage|rom|internal)|' +  # 128 gb storage
            r'\((\d+)\s+(gb|tb)\)|' +  # (128 GB) - parentheses format
            r',\s*(\d+)\s+(gb|tb)\)',  # , 128 GB) - after comma format
            re.IGNORECASE
        ),
        # RAM - Can have 'ram' keyword or just gb/mb IF no storage keyword nearby
        'ram': re.compile(r'(\d+)\s*(gb|mb)\s+ram\b', re.IGNORECASE),
        
        # Display - MUST have screen/display keyword OR be preceded by electronics terms
        'screen_size': re.compile(
            r'(?:screen|display)\s*(?:size|:)?\s*(\d+(?:\.\d+)?)\s*(inch|")|' +  # screen 6.5 inch
            r'(\d+(?:\.\d+)?)\s*(inch|")\s*(?:screen|display)',  # 6.5 inch screen
            re.IGNORECASE
        ),
        'resolution': re.compile(r'(\d+)\s*x\s*(\d+)\s*(?:pixels?|resolution|display)', re.IGNORECASE),
        
        # Camera - MUST have camera/mp keyword
        'camera_mp': re.compile(r'(\d+)\s*mp\s*(?:camera)?|(?:camera\s*)?(\d+)\s*megapixel', re.IGNORECASE),
        
        # Battery - MUST have mah/wh units (not just numbers)
        'battery': re.compile(r'(\d{3,})\s*mah|(\d{3,})\s*wh', re.IGNORECASE),  # Minimum 3 digits (100+)
        
        # Processor
        'processor': re.compile(
            r'(snapdragon|mediatek|helio|exynos|dimensity|intel|amd|apple|bionic|m\d+)\s*(\w+)?',
            re.IGNORECASE
        ),
        
        # Price (Indian Rupees) - Enhanced to detect ALL price ranges (including low prices like 500)
        'price': re.compile(
            r'(?:rs\.?|₹|rupees?|inr|taka|tk)\s*(\d+(?:,\d+)*(?:\.\d+)?)|' +  # rs/taka 50000
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:rs\.?|₹|rupees?|inr|taka|tk)|' +  # 50000 rs/taka
            r'(?:above|below|under|around|price|cost|dam|damer)\s+(\d+)|' +  # above/dam 500
            r'(\d+)\s+(?:ke\s+)?(?:upar|niche|under|above)|' +  # 500 ke upar (Hindi)
            r'(\d+)\s+(?:ar\s+)?(?:modhe|majhe)|' +  # 2000 ar modhe (Bengali romanized)
            r'(\d+)\s+(?:taka|tk)\s+(?:damer|dam)|' +  # 5000 taka damer (Bengali)
            # NEW: Product + Number (for post-translation queries like "headphones 1500")
            # Pattern allows optional adjectives before product: "wireless headphones 1500"
            # Added optional 's' for plurals: headphones, laptops, phones, etc.
            r'(?:wireless|wired|gaming|bluetooth|smart|digital|portable|electric|manual|automatic|rechargeable)?\s*' +
            r'(?:laptops?|computers?|pcs?|notebooks?|macbooks?|phones?|mobiles?|smartphones?|iphones?|' +
            r'headphones?|earphones?|earbuds|airpods|headsets?|chargers?|powerbanks?|tablets?|' +
            r'watch(?:es)?|smartwatch(?:es)?|cameras?|speakers?|mice|mouse|keyboards?|routers?|pendrives?|' +
            r'refrigerators?|fridges?|washing machines?|microwaves?|tvs?|televisions?|monitors?)\s+(\d{3,7})\b',
            re.IGNORECASE
        ),
        
        # Price range patterns (support low prices too)
        # Added Bengali romanized patterns: modhe, ar modhe, majhe, ar majhe
        # Added Bengali currency: taka, tk and price words: dam, damer
        'price_min': re.compile(r'(?:above|upar|more than|beshi)\s+(\d+)', re.IGNORECASE),
        'price_max': re.compile(
            r'(?:below|niche|under|less than|' +  # English/Hindi
            r'modhe|ar\s+modhe|majhe|ar\s+majhe|' +  # Bengali romanized
            r'kom)\s+(\d+)|' +  # Bengali "less"
            r'(\d+)\s+(?:taka|tk)\s+(?:damer|dam)',  # 5000 taka damer (under 5000 taka price)
            re.IGNORECASE
        ),
        
        # Product category - EXPANDED for ALL e-commerce
        'category': re.compile(
            r'\b(' +
            # Electronics
            r'laptop|computer|pc|notebook|macbook|' +
            r'phone|mobile|smartphone|iphone|' +
            r'headphone|earphone|earbuds|airpods|headset|' +
            r'charger|powerbank|adapter|cable|' +
            r'tablet|ipad|kindle|' +
            r'watch|smartwatch|fitband|tracker|' +
            r'camera|dslr|webcam|gopro|' +
            r'speaker|soundbar|bluetooth|jbl|' +
            r'tv|television|monitor|screen|display|' +
            r'keyboard|mouse|mousepad|' +
            r'router|modem|wifi|' +
            r'pendrive|usb|harddisk|ssd|' +
            # Home Appliances
            r'refrigerator|fridge|freezer|' +
            r'washing machine|washer|dryer|' +
            r'microwave|oven|toaster|mixer|grinder|juicer|' +
            r'iron|press|' +
            r'fan|cooler|heater|geyser|' +
            r'vacuum|cleaner|' +
            r'chimney|stove|induction|' +
            r'purifier|humidifier|dehumidifier|' +
            # Clothing & Fashion
            r'tshirt|shirt|top|blouse|kurti|kurta|' +
            r'jeans|pants|trousers|shorts|' +
            r'dress|gown|saree|lehenga|' +
            r'jacket|coat|hoodie|sweater|cardigan|' +
            r'shoes|sneakers|sandals|slippers|heels|boots|' +
            r'bag|handbag|backpack|purse|wallet|' +
            r'belt|tie|scarf|cap|hat|' +
            # Accessories & Jewelry
            r'watch|bracelet|bangle|' +
            r'necklace|chain|pendant|earring|ring|' +
            r'sunglasses|glasses|goggles|' +
            # Sports & Fitness
            r'cycle|bicycle|bike|' +
            r'treadmill|dumbbell|yoga mat|' +
            r'cricket bat|football|basketball|' +
            # Books & Stationery
            r'book|novel|notebook|diary|pen|pencil|' +
            # Beauty & Personal Care
            r'perfume|fragrance|deodorant|' +
            r'shampoo|conditioner|soap|facewash|cream|lotion|' +
            r'trimmer|shaver|razor|hairdryer|straightener|' +
            # Furniture
            r'chair|table|desk|bed|sofa|couch|mattress|pillow|' +
            r'wardrobe|cupboard|shelf|rack|' +
            # Kitchen & Dining
            r'plate|bowl|glass|mug|cup|spoon|fork|knife|' +
            r'cookware|pan|kadhai|cooker|' +
            # Toys & Baby Products
            r'toy|doll|car toy|puzzle|' +
            r'diaper|feeder|stroller|crib|' +
            # Others
            r'bottle|flask|tiffin|lunchbox|' +
            r'umbrella|raincoat|' +
            r'suitcase|luggage|trolley' +
            r')\b',
            re.IGNORECASE
        ),
        
        # Clothing Sizes
        'size': re.compile(
            r'\b(xs|s|m|l|xl|xxl|xxxl|' +  # Standard sizes
            r'\d+xl|' +  # 2xl, 3xl, etc.
            r'size\s*(\d+)|' +  # size 42
            r'(\d+)\s*inch|' +  # 32 inch waist
            r'free size|one size)\b',
            re.IGNORECASE
        ),
        
        # Material (for clothing, furniture, etc.) - NOT for colors like "steel grey"
        'material': re.compile(
            r'\b(cotton|polyester|silk|wool|leather|denim|' +
            r'linen|rayon|nylon|spandex|' +
            r'wood|metal|plastic|glass|iron|' +  # Removed 'steel' to avoid "steel grey" false positive
            r'ceramic|marble|granite)\b',
            re.IGNORECASE
        ),
        
        # Clothing sleeve type
        'sleeve': re.compile(r'\b(full sleeve|half sleeve|sleeveless|short sleeve|long sleeve)\b', re.IGNORECASE),
        
        # Furniture dimensions
        'dimension': re.compile(r'(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*(?:x\s*(\d+(?:\.\d+)?))?\s*(cm|inch|ft|meter)?', re.IGNORECASE),
        
        # Appliance capacity/power
        'capacity': re.compile(r'(\d+(?:\.\d+)?)\s*(liter|litre|kg|ton|watt|w)\b', re.IGNORECASE),
        
        # Luggage/Travel specific features
        'luggage_size': re.compile(
            r'(?:cabin|check-?in)?\s*(?:size)?\s*\(?\s*(\d+)\s*cm\s*\)?|' +  # (55 cm) or cabin size 55 cm
            r'(\d+)\s*cm\s*(?:cabin|suitcase|trolley|bag)?',  # 55 cm cabin
            re.IGNORECASE
        ),
        'luggage_type': re.compile(
            r'\b(cabin|check-?in|trolley|carry-?on|backpack|duffle|briefcase)\b',
            re.IGNORECASE
        ),
        'wheels': re.compile(r'(\d+)\s*wheels?', re.IGNORECASE),
        
        # Colors
        'color': re.compile(
            r'\b(black|white|blue|red|green|gold|silver|gray|grey|pink|purple|yellow|orange)\b',
            re.IGNORECASE
        ),
        
        # Brands
        'brand': re.compile(
            r'\b(samsung|apple|xiaomi|redmi|realme|oneplus|oppo|vivo|motorola|nokia|asus|lenovo|hp|dell|acer|lg|sony|boat|jbl|bose)\b',
            re.IGNORECASE
        ),
    }
    
    def __init__(self, use_ner=True):
        """
        Initialize Feature Extractor
        
        Args:
            use_ner (bool): Use spaCy NER for entity extraction
        """
        self.use_ner = use_ner and SPACY_AVAILABLE
        self.nlp = None
        
        if self.use_ner:
            try:
                self.nlp = spacy.load('en_core_web_sm')
                logger.info("Loaded spaCy for NER")
            except OSError:
                logger.warning("spaCy model not found. NER disabled.")
                self.use_ner = False
    
    def extract(self, text: str) -> Dict:
        """
        Extract all features from text
        
        Args:
            text (str): Input text (query or product description)
            
        Returns:
            Dict: Extracted features
        """
        features = {
            # Electronics specific
            'storage': None,
            'ram': None,
            'screen_size': None,
            'resolution': None,
            'camera_mp': [],
            'battery': None,
            'processor': None,
            # Universal features
            'price': None,
            'price_min': None,
            'price_max': None,
            'category': None,
            'category_confidence': 0.0,
            'category_method': None,
            'colors': [],
            'brands': [],
            # Clothing & Fashion
            'size': None,
            'material': None,
            'sleeve': None,
            # Furniture & Appliances
            'dimension': None,
            'capacity': None,
            # Luggage & Travel
            'luggage_size': None,
            'luggage_type': None,
            'wheels': None,
            # NER entities
            'entities': []
        }
        
        # Extract using regex patterns
        for feature_name, pattern in self.PATTERNS.items():
            extracted = self._extract_with_pattern(text, pattern, feature_name)
            if extracted:
                # Handle plural naming (color -> colors, brand -> brands)
                target_key = feature_name
                if feature_name == 'color':
                    target_key = 'colors'
                elif feature_name == 'brand':
                    target_key = 'brands'
                
                if target_key in features and isinstance(features[target_key], list):
                    features[target_key].extend(extracted)
                elif target_key in features:
                    features[target_key] = extracted[0] if extracted else None
        
        # Extract entities using NER
        if self.use_ner:
            features['entities'] = self._extract_entities(text)
        
        # FALLBACK 1: Infer category from context (brand + RAM + storage = phone/laptop)
        if features['category'] is None:
            inferred = self._infer_category_from_context(text, features)
            if inferred:
                features['category'] = inferred
                features['category_confidence'] = 0.85  # High confidence for context inference
                features['category_method'] = 'context'
                logger.info(f"✅ Context inference detected category: {inferred}")
        
        # FALLBACK 2: Use NER for category detection if still not found
        if features['category'] is None and self.use_ner:
            ner_category = self._extract_category_with_ner(text)
            if ner_category:
                features['category'] = ner_category
                features['category_confidence'] = 0.75  # Medium confidence
                features['category_method'] = 'ner'
                logger.info(f"✅ NER fallback detected category: {ner_category}")
            else:
                features['category_confidence'] = 0.0
                features['category_method'] = 'none'
                logger.warning(f"⚠️  No category detected for query: {text}")
        elif features['category']:
            # Regex detection has high confidence
            features['category_confidence'] = 0.95
            features['category_method'] = 'regex'
        else:
            # No category detected at all
            features['category_confidence'] = 0.0
            features['category_method'] = 'none'
            logger.warning(f"⚠️  No category detected for query: {text}")
        
        # NEW: Filter irrelevant features based on category
        features = self._filter_features_by_category(features)
        
        # Clean up
        features = self._clean_features(features)
        
        logger.debug(f"Extracted features: {features}")
        return features
    
    def _extract_with_pattern(self, text: str, pattern: re.Pattern, feature_name: str) -> List:
        """Extract feature using regex pattern"""
        matches = pattern.findall(text)
        results = []
        
        if not matches:
            return results
        
        if feature_name == 'storage':
            for match in matches:
                # Handle multiple pattern formats (tuple with multiple capture groups)
                # Pattern 1: (size, unit, '', '', '', '')
                # Pattern 2: ('', '', size, unit, '', '')
                # Pattern 3: ('', '', '', '', size, unit)
                if isinstance(match, tuple):
                    # Find first non-empty pair
                    for i in range(0, len(match), 2):
                        if i+1 < len(match) and match[i]:
                            size = match[i]
                            unit = match[i+1].upper() if match[i+1] else 'GB'
                            results.append(f"{size}{unit}")
                            break
                else:
                    results.append(str(match))
        
        elif feature_name == 'ram':
            for match in matches:
                size = match[0]
                unit = match[1].upper()
                results.append(f"{size}{unit}")
        
        elif feature_name == 'screen_size':
            for match in matches:
                size = match[0]
                results.append(f"{size}\"")
        
        elif feature_name == 'resolution':
            for match in matches:
                width = match[0]
                height = match[1]
                results.append(f"{width}x{height}")
        
        elif feature_name == 'camera_mp':
            for match in matches:
                mp = match[0] or match[1]
                if mp:
                    results.append(f"{mp}MP")
        
        elif feature_name == 'battery':
            for match in matches:
                capacity = match[0] or match[1]
                if capacity:
                    results.append(f"{capacity}mAh")
        
        elif feature_name == 'processor':
            for match in matches:
                proc = ' '.join([m for m in match if m]).strip()
                results.append(proc)
        
        elif feature_name == 'price':
            for match in matches:
                # Try all capture groups (now 5 groups after adding product+number pattern)
                price = match[0] or match[1] or match[2] or match[3] or (match[4] if len(match) > 4 else None)
                if price:
                    # Remove commas and convert to float
                    price_val = price.replace(',', '')
                    results.append(float(price_val))
        
        elif feature_name in ['price_min', 'price_max']:
            for match in matches:
                if match:
                    # Handle both tuple (from groups) and string (from simple pattern)
                    if isinstance(match, tuple):
                        # Extract the first non-empty group
                        price_val = next((m for m in match if m), None)
                    else:
                        price_val = match
                    
                    if price_val:
                        # Remove commas and convert to float
                        price_val = str(price_val).replace(',', '')
                        results.append(float(price_val))
        
        elif feature_name == 'category':
            # Return the first category found
            if matches:
                results.append(matches[0].lower())
        
        elif feature_name in ['size', 'sleeve', 'material', 'capacity', 'luggage_type']:
            # Single value features
            if matches:
                if isinstance(matches[0], tuple):
                    val = ' '.join([m for m in matches[0] if m]).strip()
                else:
                    val = matches[0]
                results.append(val)
        
        elif feature_name == 'luggage_size':
            # Extract luggage size (e.g., "55 cm")
            for match in matches:
                if isinstance(match, tuple):
                    # Get first non-empty value
                    size = next((m for m in match if m), None)
                    if size:
                        results.append(f"{size} cm")
                else:
                    results.append(f"{match} cm")
        
        elif feature_name == 'wheels':
            # Extract wheel count
            for match in matches:
                results.append(match)
        
        elif feature_name == 'dimension':
            for match in matches:
                # Format: WxHxD or WxH
                dims = [d for d in match[:3] if d]
                unit = match[3] if len(match) > 3 and match[3] else ''
                dim_str = 'x'.join(dims)
                if unit:
                    dim_str += unit
                results.append(dim_str)
        
        elif feature_name in ['color', 'brand']:
            results = list(set([m.lower() for m in matches]))
        
        return results
    
    def _extract_entities(self, text: str) -> List[Dict]:
        """Extract named entities using spaCy NER"""
        if not self.nlp:
            return []
        
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char
            })
        
        return entities
    
    def _infer_category_from_context(self, text: str, features: Dict) -> Optional[str]:
        """
        Infer product category from contextual clues (brand + specs combo)
        
        Examples:
            - realme + 5g + ram + storage = phone
            - dell + intel + ram + ssd = laptop
            - sony + mp + lens = camera
        
        Args:
            text (str): Input text
            features (Dict): Already extracted features
            
        Returns:
            Optional[str]: Inferred category or None
        """
        text_lower = text.lower()
        
        # Phone brands + specs = phone
        phone_brands = ['realme', 'xiaomi', 'redmi', 'samsung', 'oppo', 'vivo', 'oneplus', 
                       'iphone', 'apple', 'nokia', 'motorola', 'poco', 'iqoo', 'nothing']
        phone_indicators = ['5g', '4g', 'dual sim', 'selfie', 'front camera', 'rear camera']
        
        # Laptop brands + specs = laptop
        laptop_brands = ['dell', 'hp', 'lenovo', 'asus', 'acer', 'msi', 'macbook', 'thinkpad']
        laptop_indicators = ['intel', 'amd', 'ryzen', 'i3', 'i5', 'i7', 'i9', 'ssd', 'windows', 'linux']
        
        # Check if it's a phone
        has_phone_brand = any(brand in text_lower for brand in phone_brands)
        has_phone_indicator = any(ind in text_lower for ind in phone_indicators)
        has_ram = features.get('ram') is not None
        has_storage = features.get('storage') is not None
        
        if has_phone_brand and (has_phone_indicator or (has_ram and has_storage)):
            logger.info(f"Context inference: phone brand + specs detected")
            return 'phone'
        
        # Check if it's a laptop
        has_laptop_brand = any(brand in text_lower for brand in laptop_brands)
        has_laptop_indicator = any(ind in text_lower for ind in laptop_indicators)
        
        if has_laptop_brand and (has_laptop_indicator or (has_ram and has_storage)):
            logger.info(f"Context inference: laptop brand + specs detected")
            return 'laptop'
        
        # Check for "p1", "p2", "p3", etc. (common phone naming)
        if re.search(r'\bp\d+\b', text_lower) and (has_ram or has_storage):
            logger.info(f"Context inference: phone model naming pattern detected")
            return 'phone'
        
        return None
    
    def _extract_category_with_ner(self, text: str) -> Optional[str]:
        """
        Extract category using NER when regex fails (FALLBACK)
        
        Args:
            text (str): Input text
            
        Returns:
            Optional[str]: Detected category or None
        """
        if not self.nlp:
            return None
        
        # Common words to ignore (too generic)
        IGNORE_WORDS = {
            'product', 'item', 'thing', 'stuff', 'something', 'anything',
            'price', 'rupee', 'rs', 'inr', 'under', 'above', 'below',
            'quality', 'best', 'good', 'cheap', 'expensive', 'new', 'old'
        }
        
        doc = self.nlp(text)
        
        # Strategy 1: Look for PRODUCT entities
        for ent in doc.ents:
            if ent.label_ == 'PRODUCT':
                category_candidate = ent.text.lower().strip()
                if category_candidate not in IGNORE_WORDS:
                    logger.info(f"NER detected category from PRODUCT entity: {category_candidate}")
                    return category_candidate
        
        # Strategy 2: Look for noun chunks (product names)
        for chunk in doc.noun_chunks:
            # Get the main noun (root of the chunk)
            category_candidate = chunk.root.text.lower().strip()
            
            # Filter criteria:
            # - Not in ignore list
            # - At least 3 characters
            # - Is a noun (not verb/adjective)
            if (category_candidate not in IGNORE_WORDS and 
                len(category_candidate) > 2 and
                chunk.root.pos_ == 'NOUN'):
                logger.info(f"NER detected category from noun chunk: {category_candidate}")
                return category_candidate
        
        logger.debug("NER could not detect category")
        return None
    
    def _filter_features_by_category(self, features: Dict) -> Dict:
        """
        Remove irrelevant features based on product category
        Only show features that make sense for the detected category
        """
        category = features.get('category', '').lower() if features.get('category') else None
        
        if not category:
            return features  # No filtering if category unknown
        
        # Define relevant features for each category type
        CATEGORY_FEATURES = {
            # Electronics (phones, laptops, tablets, etc.)
            'electronics': ['ram', 'storage', 'screen_size', 'resolution', 'camera_mp', 
                          'battery', 'processor', 'price', 'price_min', 'price_max', 
                          'category', 'category_confidence', 'category_method', 
                          'colors', 'brands', 'entities'],
            
            # Luggage & Travel
            'luggage': ['luggage_size', 'luggage_type', 'wheels', 'material', 
                       'price', 'price_min', 'price_max', 'category', 
                       'category_confidence', 'category_method', 'colors', 
                       'brands', 'entities'],
            
            # Clothing & Fashion
            'clothing': ['size', 'material', 'sleeve', 'price', 'price_min', 
                        'price_max', 'category', 'category_confidence', 
                        'category_method', 'colors', 'brands', 'entities'],
            
            # Furniture & Home
            'furniture': ['dimension', 'material', 'price', 'price_min', 
                         'price_max', 'category', 'category_confidence', 
                         'category_method', 'colors', 'brands', 'entities'],
            
            # Appliances
            'appliances': ['capacity', 'dimension', 'price', 'price_min', 
                          'price_max', 'category', 'category_confidence', 
                          'category_method', 'colors', 'brands', 'entities'],
        }
        
        # Map specific categories to category types
        CATEGORY_MAPPING = {
            # Electronics
            'laptop': 'electronics', 'phone': 'electronics', 'mobile': 'electronics',
            'tablet': 'electronics', 'headphone': 'electronics', 'earphone': 'electronics',
            'watch': 'electronics', 'smartwatch': 'electronics', 'camera': 'electronics',
            'tv': 'electronics', 'monitor': 'electronics', 'speaker': 'electronics',
            
            # Luggage
            'suitcase': 'luggage', 'bag': 'luggage', 'backpack': 'luggage',
            'trolley': 'luggage', 'duffle': 'luggage', 'briefcase': 'luggage',
            'luggage': 'luggage',
            
            # Clothing
            'tshirt': 'clothing', 'shirt': 'clothing', 'jeans': 'clothing',
            'dress': 'clothing', 'saree': 'clothing', 'shoes': 'clothing',
            'jacket': 'clothing', 'sweater': 'clothing',
            
            # Furniture
            'chair': 'furniture', 'table': 'furniture', 'sofa': 'furniture',
            'bed': 'furniture', 'desk': 'furniture', 'wardrobe': 'furniture',
            
            # Appliances
            'refrigerator': 'appliances', 'washing machine': 'appliances',
            'microwave': 'appliances', 'fan': 'appliances', 'ac': 'appliances',
        }
        
        # Determine category type
        category_type = CATEGORY_MAPPING.get(category, None)
        
        if not category_type:
            return features  # Unknown category, keep all features
        
        # Get relevant features for this category type
        relevant_features = CATEGORY_FEATURES.get(category_type, [])
        
        # Remove irrelevant features (set to None instead of deleting)
        for key in list(features.keys()):
            if key not in relevant_features:
                # Don't show this feature for this category
                if key in features:
                    del features[key]
        
        logger.debug(f"Filtered features for {category} ({category_type}): kept {len(features)} relevant features")
        return features
    
    def _clean_features(self, features: Dict) -> Dict:
        """Clean and deduplicate extracted features"""
        # Remove None values from lists
        for key in ['camera_mp', 'colors', 'brands']:
            if key in features and features[key]:
                features[key] = list(set([f for f in features[key] if f]))
        
        # Remove empty lists
        for key in list(features.keys()):
            if isinstance(features[key], list) and not features[key]:
                features[key] = None
        
        return features
    
    def extract_price(self, text: str) -> Optional[float]:
        """
        Extract price from text
        
        Args:
            text (str): Input text
            
        Returns:
            Optional[float]: Extracted price or None
        """
        price_match = self.PATTERNS['price'].search(text)
        if price_match:
            # Check all groups (pattern has multiple alternatives)
            for group in price_match.groups():
                if group:
                    return float(group.replace(',', ''))
        return None
    
    def extract_brand(self, text: str) -> Optional[str]:
        """
        Extract brand name from text
        
        Args:
            text (str): Input text
            
        Returns:
            Optional[str]: Brand name or None
        """
        brand_match = self.PATTERNS['brand'].search(text)
        if brand_match:
            return brand_match.group(0).lower()
        return None
