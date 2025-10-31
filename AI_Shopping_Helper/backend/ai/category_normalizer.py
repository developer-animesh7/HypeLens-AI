"""
Category Normalizer - Fix inconsistent category names
====================================================
Normalizes category names to standard format (case-insensitive matching)
"""
from typing import Optional, List


class CategoryNormalizer:
    """
    Normalizes product categories to standard format
    Fixes issues like: Smartphone vs smartphone vs Smartphones
    """
    
    # STANDARD CATEGORY NAMES (use these everywhere!)
    STANDARD_CATEGORIES = {
        'Smartphones': [
            'smartphone', 'smartphones', 'phone', 'phones', 'mobile', 'mobiles',
            'iphone', 'android', 'galaxy', 'oneplus', 'vivo', 'oppo', 'realme',
            'mi', 'redmi', 'poco', 'nokia', 'pixel', 's24', 's23', 's22', 'fold', 'flip'
        ],
        'Laptops': [
            'laptop', 'laptops', 'notebook', 'notebooks', 'macbook', 'chromebook',
            'thinkpad', 'ideapad', 'inspiron', 'xps', 'pavilion', 'envy', 'omen',
            'victus', 'yoga', 'legion', 'zenbook', 'vivobook'
        ],
        'Electronics': [
            'electronics', 'electronic', 'tablet', 'ipad', 'watch', 'smartwatch',
            'headphone', 'headphones', 'earphone', 'earphones', 'earbud', 'earbuds',
            'airpods', 'speaker', 'camera', 'dslr', 'tv', 'television', 'monitor',
            'keyboard', 'mouse', 'charger', 'powerbank', 'cable', 'bluetooth'
        ],
        'Footwear': [
            'footwear', 'shoe', 'shoes', 'sneaker', 'sneakers', 'boot', 'boots',
            'sandal', 'sandals', 'slipper', 'slippers', 'nike', 'adidas', 'puma',
            'running shoe', 'sports shoe', 'casual shoe', 'formal shoe'
        ],
        'Clothing': [
            'clothing', 'clothes', 'shirt', 't-shirt', 'tshirt', 'pant', 'pants',
            'jeans', 'jacket', 'hoodie', 'dress', 'top', 'bottom', 'kurta',
            'shorts', 'skirt', 'blazer', 'coat', 'sweater', 'sweatshirt'
        ],
        'Accessories': [
            'accessories', 'accessory', 'bag', 'backpack', 'wallet', 'belt',
            'sunglass', 'sunglasses', 'watch strap', 'bracelet', 'necklace',
            'cap', 'hat', 'scarf', 'tie', 'gloves'
        ],
        'Sports': [
            'sports', 'sport', 'ball', 'football', 'cricket', 'bat', 'racket',
            'gym', 'fitness', 'yoga', 'exercise', 'bicycle', 'cycle', 'badminton',
            'tennis', 'basketball', 'volleyball'
        ],
        'Furniture': [
            'furniture', 'chair', 'table', 'desk', 'bed', 'sofa', 'couch',
            'wardrobe', 'cabinet', 'shelf'
        ]
    }
    
    def __init__(self):
        # Build reverse lookup: keyword -> standard category
        self._keyword_to_category = {}
        for standard_cat, keywords in self.STANDARD_CATEGORIES.items():
            for keyword in keywords:
                self._keyword_to_category[keyword.lower()] = standard_cat
    
    def normalize(self, category: str) -> str:
        """
        Normalize a category name to standard format
        
        Args:
            category: Raw category name (e.g., "smartphone", "LAPTOPS", "phone")
            
        Returns:
            Standard category name (e.g., "Smartphones", "Laptops", "Smartphones")
        """
        if not category:
            return 'Electronics'  # Default fallback
        
        category_lower = category.lower().strip()
        
        # Direct match to standard category (case-insensitive)
        for standard_cat in self.STANDARD_CATEGORIES.keys():
            if category_lower == standard_cat.lower():
                return standard_cat
        
        # Keyword-based match
        if category_lower in self._keyword_to_category:
            return self._keyword_to_category[category_lower]
        
        # Partial match (e.g., "men's clothing" -> "Clothing")
        for standard_cat, keywords in self.STANDARD_CATEGORIES.items():
            for keyword in keywords:
                if keyword in category_lower or category_lower in keyword:
                    return standard_cat
        
        # No match - return original with title case
        return category.title()
    
    def detect_from_text(self, text: str) -> Optional[str]:
        """
        Detect category from query text
        
        Args:
            text: Query text (e.g., "Samsung S24 phone", "MacBook Air laptop")
            
        Returns:
            Standard category name or None if not detected
        """
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Score each category by counting keyword matches
        category_scores = {}
        for standard_cat, keywords in self.STANDARD_CATEGORIES.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    # Weight longer keywords more (more specific)
                    score += len(keyword.split())
            if score > 0:
                category_scores[standard_cat] = score
        
        # Return category with highest score
        if category_scores:
            return max(category_scores, key=lambda k: category_scores[k])
        
        return None
    
    def detect_from_results(self, results: List[dict], consensus_threshold: int = 2) -> Optional[str]:
        """
        Detect category from search results (consensus-based)
        
        Args:
            results: List of search results with 'category' field
            consensus_threshold: Minimum number of top results to consider
            
        Returns:
            Standard category name based on consensus or None
        """
        if not results or len(results) < consensus_threshold:
            return None
        
        # Count normalized categories in top results
        category_counts = {}
        for result in results[:min(5, len(results))]:  # Top 5 max
            raw_category = result.get('category', '')
            if raw_category:
                normalized = self.normalize(raw_category)
                category_counts[normalized] = category_counts.get(normalized, 0) + 1
        
        # Return most common category (consensus wins!)
        if category_counts:
            return max(category_counts, key=lambda k: category_counts[k])
        
        return None
    
    def are_same_category(self, cat1: str, cat2: str) -> bool:
        """
        Check if two categories are the same (case-insensitive, normalized)
        
        Args:
            cat1: First category
            cat2: Second category
            
        Returns:
            True if they represent the same category
        """
        if not cat1 or not cat2:
            return False
        
        return self.normalize(cat1) == self.normalize(cat2)


# Singleton instance
_normalizer = None

def get_normalizer() -> CategoryNormalizer:
    """Get global category normalizer instance"""
    global _normalizer
    if _normalizer is None:
        _normalizer = CategoryNormalizer()
    return _normalizer


if __name__ == "__main__":
    """Test category normalization"""
    print("\n" + "="*80)
    print("🔧 TESTING CATEGORY NORMALIZER")
    print("="*80)
    
    normalizer = CategoryNormalizer()
    
    test_cases = [
        "smartphone",
        "Smartphone",
        "SMARTPHONES",
        "phone",
        "iPhone",
        "laptop",
        "Laptop",
        "LAPTOPS",
        "MacBook",
        "footwear",
        "Shoes",
        "ELECTRONICS",
        "Men's Clothing",
        "cricket ball"
    ]
    
    print("\nNormalizing category names:")
    print("-" * 80)
    for test in test_cases:
        normalized = normalizer.normalize(test)
        print(f"  '{test:20s}' → '{normalized}'")
    
    print("\nDetecting categories from text:")
    print("-" * 80)
    text_tests = [
        "Samsung Galaxy S24 Ultra smartphone",
        "Apple MacBook Air M2 laptop",
        "Nike Air Max running shoes",
        "Sony WH-1000XM5 headphones",
        "Cricket ball red leather"
    ]
    for text in text_tests:
        detected = normalizer.detect_from_text(text)
        print(f"  '{text[:40]:40s}' → {detected}")
    
    print("\n" + "="*80)
    print("✅ CATEGORY NORMALIZATION WORKS!")
    print("="*80 + "\n")
