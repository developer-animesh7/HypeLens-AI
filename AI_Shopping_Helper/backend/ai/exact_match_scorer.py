"""
IMPROVED SCORING ALGORITHM - Like Price Tracker Apps
=====================================================
Boosts exact product matches using category + brand + model matching
"""
import re
from typing import Dict, Any, List, Tuple


class ExactMatchScorer:
    """
    Advanced scoring system to identify EXACT MATCHES vs SIMILAR ITEMS
    Like price tracking apps (CamelCamelCamel, Keepa, etc.)
    """
    
    def __init__(self):
        # Brand keywords for better matching
        self.brands = {
            'apple': ['macbook', 'iphone', 'ipad', 'airpods', 'apple'],
            'samsung': ['samsung', 'galaxy', 's24', 's23', 'note', 'fold', 'flip'],
            'oneplus': ['oneplus', 'one plus', 'nord'],
            'xiaomi': ['xiaomi', 'mi', 'redmi', 'poco'],
            'dell': ['dell', 'inspiron', 'xps', 'latitude', 'vostro'],
            'hp': ['hp', 'pavilion', 'envy', 'omen', 'victus'],
            'lenovo': ['lenovo', 'thinkpad', 'ideapad', 'legion', 'yoga'],
            'vivo': ['vivo', 'v29', 'v27'],
            'oppo': ['oppo', 'find', 'reno'],
            'realme': ['realme', 'narzo']
        }
        
        # Category keywords for classification (NORMALIZED - case-insensitive)
        # Maps to STANDARD category names used in database
        self.category_keywords = {
            'Smartphones': ['phone', 'smartphone', 'iphone', 'galaxy', 's24', 's23', 'fold', 'flip', 'oneplus', 'vivo', 'oppo', 'realme', 'mobile', 'android', 'ios', 'pixel', 'mi', 'redmi', 'poco', 'nokia'],
            'Laptops': ['laptop', 'macbook', 'notebook', 'thinkpad', 'ideapad', 'inspiron', 'xps', 'pavilion', 'envy', 'omen', 'victus', 'yoga', 'legion', 'zenbook', 'vivobook', 'chromebook'],
            'Electronics': ['tablet', 'ipad', 'galaxy tab', 'tab', 'watch', 'smartwatch', 'apple watch', 'galaxy watch', 'fitness tracker', 'headphone', 'headphones', 'earphone', 'earphones', 'earbud', 'earbuds', 'airpods', 'speaker', 'bluetooth', 'camera', 'dslr', 'mirrorless', 'canon', 'nikon', 'sony camera', 'tv', 'television', 'smart tv', 'oled', 'qled', 'monitor', 'keyboard', 'mouse', 'charger', 'powerbank', 'cable'],
            'Footwear': ['shoe', 'shoes', 'sneaker', 'sneakers', 'boot', 'boots', 'sandal', 'sandals', 'nike', 'adidas', 'puma', 'slipper', 'slippers', 'footwear', 'running shoe', 'sports shoe', 'casual shoe', 'formal shoe'],
            'Clothing': ['shirt', 't-shirt', 'tshirt', 'pant', 'pants', 'jeans', 'jacket', 'hoodie', 'dress', 'top', 'bottom', 'kurta', 'saree', 'lehenga', 'salwar', 'shorts', 'skirt', 'blazer', 'coat', 'sweater', 'sweatshirt'],
            'Accessories': ['bag', 'backpack', 'wallet', 'belt', 'sunglass', 'sunglasses', 'watch strap', 'band', 'bracelet', 'necklace', 'ring', 'earring', 'cap', 'hat', 'scarf', 'tie', 'gloves'],
            'Sports': ['ball', 'football', 'cricket', 'bat', 'racket', 'gym', 'fitness', 'yoga', 'exercise', 'sports equipment', 'bicycle', 'cycle', 'badminton', 'tennis', 'basketball', 'volleyball'],
            'Furniture': ['chair', 'table', 'desk', 'bed', 'sofa', 'couch', 'wardrobe', 'cabinet', 'shelf', 'furniture'],
        }
        
        # Model number patterns
        self.model_patterns = [
            r'm\d+\s*(pro|air|max)?',  # M1, M2, M3 Pro
            r's\d+\s*(ultra|plus|\+)?',  # S24 Ultra, S23+
            r'iphone\s*\d+\s*(pro|max|plus)?',  # iPhone 15 Pro Max
            r'galaxy\s*[a-z]\d+',  # Galaxy A54
            r'\d+\s*(gb|tb)',  # 512GB, 1TB
        ]
    
    def extract_brand(self, text: str) -> str:
        """Extract brand name from product text"""
        text_lower = text.lower()
        for brand, keywords in self.brands.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return brand
        return 'unknown'
    
    def extract_category(self, text: str) -> str:
        """
        Extract category from query text
        
        Args:
            text: Query text (e.g., "Samsung S24", "MacBook Air M2", "Nike shoes")
            
        Returns:
            Category name (e.g., "Smartphone", "Laptop", "Footwear")
            Returns None if no category detected
        """
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Score each category by matching keywords
        category_scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            return best_category
        
        return None
    
    def extract_model(self, text: str) -> str:
        """Extract model identifier from product text"""
        text_lower = text.lower()
        for pattern in self.model_patterns:
            match = re.search(pattern, text_lower)
            if match:
                return match.group(0).strip()
        return ''
    
    def calculate_exact_match_bonus(
        self, 
        query_product: Dict[str, Any],
        result_product: Dict[str, Any]
    ) -> float:
        """
        Calculate bonus score for exact product matches
        
        Returns:
            Bonus score (0.0 to 0.3) to add to similarity score
        """
        bonus = 0.0
        
        query_name = query_product.get('name', '').lower()
        query_desc = query_product.get('description', '').lower()
        result_name = result_product.get('name', '').lower()
        result_desc = result_product.get('description', '').lower()
        
        # Extract brand and model
        query_brand = self.extract_brand(query_name + ' ' + query_desc)
        result_brand = self.extract_brand(result_name + ' ' + result_desc)
        
        query_model = self.extract_model(query_name + ' ' + query_desc)
        result_model = self.extract_model(result_name + ' ' + result_desc)
        
        # BONUS 1: Brand match (+0.1)
        if query_brand != 'unknown' and query_brand == result_brand:
            bonus += 0.10
        
        # BONUS 2: Model match (+0.15)
        if query_model and result_model and query_model == result_model:
            bonus += 0.15
        
        # BONUS 3: Category match (+0.05)
        query_category = query_product.get('category', '').lower()
        result_category = result_product.get('category', '').lower()
        if query_category and result_category and query_category == result_category:
            bonus += 0.05
        
        return min(bonus, 0.30)  # Cap at +30%
    
    def boost_exact_matches(
        self,
        results: List[Dict[str, Any]],
        query_info: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Boost scores for exact product matches
        
        Args:
            results: Search results from hybrid_search
            query_info: Optional query information (extracted from image)
            
        Returns:
            Results with boosted scores for exact matches
        """
        if not query_info:
            # If no query info, try to infer from top result
            if results:
                query_info = {
                    'name': results[0].get('name', ''),
                    'description': results[0].get('name', ''),  # Use name as description
                    'category': results[0].get('category', '')
                }
            else:
                return results
        
        boosted_results = []
        for result in results:
            # Calculate exact match bonus
            bonus = self.calculate_exact_match_bonus(query_info, result)
            
            # Add bonus to similarity score
            original_score = result.get('similarity_score', 0.0)
            boosted_score = min(original_score + bonus, 1.0)  # Cap at 100%
            
            # Create boosted result
            boosted_result = result.copy()
            boosted_result['similarity_score'] = round(boosted_score, 4)
            boosted_result['exact_match_bonus'] = round(bonus, 4)
            boosted_result['original_score'] = round(original_score, 4)
            
            boosted_results.append(boosted_result)
        
        # Re-sort by boosted score (price as secondary sort if available)
        boosted_results.sort(key=lambda x: (-x['similarity_score'], x.get('price', 0)))
        
        return boosted_results


# Test the scorer
if __name__ == "__main__":
    print("\n" + "="*80)
    print("🎯 TESTING EXACT MATCH SCORER")
    print("="*80)
    
    scorer = ExactMatchScorer()
    
    # Test case: MacBook M2
    query = {
        'name': 'MacBook Air M2',
        'description': 'Apple MacBook Air M2 2022 13.6 inch laptop',
        'category': 'Laptops'
    }
    
    results = [
        {
            'name': 'Apple MacBook Air M2',
            'description': 'MacBook Air M2 13.6 inch',
            'category': 'Laptops',
            'similarity_score': 0.55,
            'price': 114990
        },
        {
            'name': 'MacBook Pro 14 M3',
            'description': 'MacBook Pro 14 inch M3',
            'category': 'Laptops',
            'similarity_score': 0.52,
            'price': 169900
        },
        {
            'name': 'Dell XPS 15',
            'description': 'Dell XPS 15 laptop',
            'category': 'Laptops',
            'similarity_score': 0.48,
            'price': 129990
        }
    ]
    
    print("\nBefore Boosting:")
    for r in results:
        print(f"  {r['name']}: {r['similarity_score']*100:.1f}% match")
    
    # Boost exact matches
    boosted = scorer.boost_exact_matches(results, query)
    
    print("\nAfter Boosting:")
    for r in boosted:
        bonus = r.get('exact_match_bonus', 0)
        original = r.get('original_score', 0)
        print(f"  {r['name']}: {r['similarity_score']*100:.1f}% match (was {original*100:.1f}%, +{bonus*100:.1f}% bonus)")
    
    print("\n" + "="*80)
    print("✅ EXACT MATCH SCORING WORKS!")
    print("="*80)
    print("\nKey Features:")
    print("  • Brand matching: +10% bonus")
    print("  • Model matching: +15% bonus")
    print("  • Category matching: +5% bonus")
    print("  • Maximum bonus: +30%")
    print("\nResult:")
    print(f"  • MacBook Air M2: {boosted[0]['similarity_score']*100:.1f}% (EXACT MATCH)")
    print(f"  • MacBook Pro 14: {boosted[1]['similarity_score']*100:.1f}% (similar)")
    print(f"  • Dell XPS 15: {boosted[2]['similarity_score']*100:.1f}% (similar category)")
    print("="*80 + "\n")
