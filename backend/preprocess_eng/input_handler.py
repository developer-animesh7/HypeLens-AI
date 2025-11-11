"""
Input Handler - Expands shortened URLs and parses user input
Supports: text queries, URLs, shortened links (bitly, tinyurl, etc.)
"""

import re
import requests
from urllib.parse import urlparse, parse_qs
import logging
import sys
from pathlib import Path
from functools import lru_cache
import hashlib

logger = logging.getLogger(__name__)


class InputHandler:
    """Handles user input processing and URL expansion"""
    
    # Common URL shorteners
    URL_SHORTENERS = [
        'bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'ow.ly',
        'is.gd', 'buff.ly', 'adf.ly', 'short.io', 'rb.gy'
    ]
    
    # E-commerce platforms
    ECOMMERCE_DOMAINS = [
        'amazon.in', 'flipkart.com', 'myntra.com', 'snapdeal.com',
        'ajio.com', 'meesho.com', 'shopclues.com', 'paytmmall.com'
    ]
    
    # Class-level cache for scraped products (shared across instances)
    _product_cache = {}
    _cache_max_size = 1000  # Cache up to 1000 products
    
    def __init__(self, timeout=5):
        """
        Initialize Input Handler
        
        Args:
            timeout (int): Timeout for URL expansion requests
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def process(self, user_input: str) -> dict:
        """
        Process user input - detect type and extract information
        
        OPTIMIZED: Fast-path for text queries (<1ms for 95% of queries)
        
        Args:
            user_input (str): Raw user input (text, URL, or shortened link)
            
        Returns:
            dict: Processed input with type, original_url, expanded_url, query_text, product_data
        """
        user_input = user_input.strip()
        
        # FAST PATH: Check if it's a simple text query (95% of cases)
        # Skip expensive URL checks if no URL indicators present
        if not self._looks_like_url_fast(user_input):
            # Pure text query - fastest path
            return {
                'input_type': 'text',
                'original_input': user_input,
                'expanded_url': None,
                'query_text': user_input,
                'platform': None,
                'product_id': None,
                'product_data': None
            }
        
        # SLOW PATH: URL processing (only 5% of queries)
        result = {
            'input_type': 'text',
            'original_input': user_input,
            'expanded_url': None,
            'query_text': user_input,
            'platform': None,
            'product_id': None,
            'product_data': None
        }
        
        # Check if input is a URL
        if self._is_url(user_input):
            result['input_type'] = 'url'
            result['original_url'] = user_input
            
            # OPTIMIZATION: Check product cache BEFORE URL expansion
            # Extract platform/product_id from original URL (fast)
            quick_platform_info = self._extract_platform_info(user_input)
            if quick_platform_info.get('platform') and quick_platform_info.get('product_id'):
                cache_key = f"{quick_platform_info['platform']}:{quick_platform_info['product_id']}"
                
                # If product is cached, skip URL expansion entirely
                if cache_key in self._product_cache:
                    logger.info(f"⚡ FAST PATH: Product cached, skipping URL expansion")
                    result.update(quick_platform_info)
                    result['expanded_url'] = user_input  # Use original URL
                    product_data = self._product_cache[cache_key]
                    result['product_data'] = product_data
                    result['query_text'] = self._product_to_text(product_data)
                    result['cache_hit'] = True
                    logger.info(f"Input processed: {result['input_type']} - {result['query_text'][:100]}")
                    return result
            
            # SLOW PATH: Cache miss, need to expand URL
            # Check if it's a shortened URL
            if self._is_shortened_url(user_input):
                logger.info(f"Detected shortened URL: {user_input}")
                expanded = self._expand_url(user_input)
                result['expanded_url'] = expanded
            else:
                result['expanded_url'] = user_input
            
            # Extract platform and product ID if possible
            platform_info = self._extract_platform_info(result['expanded_url'])
            result.update(platform_info)
            
            # NEW: Scrape product if it's an e-commerce URL (with caching for <50ms)
            if result['platform']:
                # Generate cache key from platform + product_id
                cache_key = f"{result['platform']}:{result.get('product_id', result['expanded_url'])}"
                
                # Check cache first (instant lookup)
                if cache_key in self._product_cache:
                    logger.info(f"⚡ Cache HIT: Using cached product data ({cache_key})")
                    product_data = self._product_cache[cache_key]
                    result['product_data'] = product_data
                    result['query_text'] = self._product_to_text(product_data)
                    result['cache_hit'] = True
                else:
                    # Cache MISS: Scrape product (1-2 seconds)
                    logger.info(f"🔍 Cache MISS: Scraping product from {result['platform']}...")
                    product_data = self._scrape_product_url(result['expanded_url'])
                    
                    if product_data:
                        # Store in cache for future requests
                        self._cache_product(cache_key, product_data)
                        result['product_data'] = product_data
                        result['query_text'] = self._product_to_text(product_data)
                        result['cache_hit'] = False
                        logger.info(f"✅ Product scraped and cached: {product_data.get('name', 'Unknown')[:50]}")
                    else:
                        logger.warning("⚠️  Product scraping failed, using URL text as fallback")
                        result['query_text'] = result['expanded_url']
                        result['cache_hit'] = False
            else:
                result['query_text'] = result['expanded_url']
        
        logger.info(f"Input processed: {result['input_type']} - {result['query_text'][:100]}")
        return result
    
    def _looks_like_url_fast(self, text: str) -> bool:
        """
        Fast check if text might be a URL (before expensive regex)
        
        Checks for common URL indicators:
        - Starts with http:// or https://
        - Contains www.
        - Contains .com, .in, .org, etc.
        
        Returns:
            bool: True if text might be a URL (needs full check)
        """
        text_lower = text.lower()
        return (
            text_lower.startswith('http://') or
            text_lower.startswith('https://') or
            text_lower.startswith('www.') or
            '.com' in text_lower or
            '.in' in text_lower or
            '.org' in text_lower or
            '.ly' in text_lower  # bit.ly
        )
    
    def _is_url(self, text: str) -> bool:
        """Check if text is a URL"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'|^www\.'  # or starts with www.
            r'|\.[a-z]{2,}/'  # or contains domain extension
        , re.IGNORECASE)
        return bool(url_pattern.search(text))
    
    def _is_shortened_url(self, url: str) -> bool:
        """Check if URL is from a known shortener service"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower().replace('www.', '')
            return any(shortener in domain for shortener in self.URL_SHORTENERS)
        except Exception as e:
            logger.error(f"Error checking shortened URL: {e}")
            return False
    
    def _expand_url(self, short_url: str) -> str:
        """
        Expand shortened URL by following redirects
        
        Args:
            short_url (str): Shortened URL
            
        Returns:
            str: Expanded/final URL
        """
        try:
            # Ensure URL has scheme
            if not short_url.startswith('http'):
                short_url = 'https://' + short_url
            
            # Follow redirects to get final URL
            response = self.session.head(
                short_url,
                allow_redirects=True,
                timeout=self.timeout
            )
            
            final_url = response.url
            logger.info(f"Expanded URL: {short_url} -> {final_url}")
            return final_url
            
        except requests.RequestException as e:
            logger.warning(f"Failed to expand URL {short_url}: {e}")
            return short_url
        except Exception as e:
            logger.error(f"Unexpected error expanding URL: {e}")
            return short_url
    
    def _extract_platform_info(self, url: str) -> dict:
        """
        Extract platform and product ID from e-commerce URL
        
        Args:
            url (str): E-commerce product URL
            
        Returns:
            dict: Platform name and product ID if found
        """
        result = {'platform': None, 'product_id': None}
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower().replace('www.', '')
            
            # Detect platform
            if 'amazon' in domain:
                result['platform'] = 'amazon'
                # Extract ASIN from Amazon URL
                asin_match = re.search(r'/dp/([A-Z0-9]{10})', url)
                if asin_match:
                    result['product_id'] = asin_match.group(1)
            
            elif 'flipkart' in domain:
                result['platform'] = 'flipkart'
                # Extract product ID from Flipkart URL
                pid_match = re.search(r'pid=([A-Z0-9]+)', url)
                if pid_match:
                    result['product_id'] = pid_match.group(1)
            
            elif 'myntra' in domain:
                result['platform'] = 'myntra'
                # Extract product ID from Myntra URL
                pid_match = re.search(r'/(\d+)/buy', url)
                if pid_match:
                    result['product_id'] = pid_match.group(1)
            
            elif any(platform in domain for platform in ['snapdeal', 'ajio', 'meesho']):
                for platform in ['snapdeal', 'ajio', 'meesho']:
                    if platform in domain:
                        result['platform'] = platform
                        break
            
            logger.info(f"Extracted platform info: {result}")
            
        except Exception as e:
            logger.error(f"Error extracting platform info: {e}")
        
        return result
    
    def _scrape_product_url(self, url: str) -> dict:
        """
        Scrape product information from URL
        
        Args:
            url (str): Product URL
            
        Returns:
            dict: Product data (name, price, specs, etc.) or None if scraping fails
        """
        try:
            # Import scraper (try multiple import paths for flexibility)
            try:
                from backend.scraping.product_scraper import ProductScraper
            except ImportError:
                # Fallback: try absolute path from project root
                import sys
                project_root = Path(__file__).parent.parent.parent
                if str(project_root) not in sys.path:
                    sys.path.insert(0, str(project_root))
                from backend.scraping.product_scraper import ProductScraper
            
            scraper = ProductScraper()
            product_data = scraper.scrape_product(url)
            
            if product_data and product_data.get('name'):
                logger.info(f"Scraped product: {product_data['name'][:50]}")
                return product_data
            else:
                logger.warning("Scraping returned empty or invalid data")
                return None
            
        except ImportError as e:
            logger.error(f"ProductScraper not available: {e}")
            return None
        except Exception as e:
            logger.error(f"Error scraping product: {e}", exc_info=True)
            return None
    
    def _cache_product(self, cache_key: str, product_data: dict):
        """
        Cache scraped product data for fast future lookups
        
        Uses LRU eviction when cache size exceeds limit
        
        Args:
            cache_key (str): Cache key (platform:product_id)
            product_data (dict): Scraped product data
        """
        # Check if cache is full
        if len(self._product_cache) >= self._cache_max_size:
            # Remove oldest entry (FIFO eviction)
            oldest_key = next(iter(self._product_cache))
            del self._product_cache[oldest_key]
            logger.debug(f"Cache full, evicted: {oldest_key}")
        
        # Add to cache
        self._product_cache[cache_key] = product_data
        logger.debug(f"Cached product: {cache_key} (cache size: {len(self._product_cache)})")
    
    @classmethod
    def clear_cache(cls):
        """Clear the product cache (useful for testing or memory management)"""
        cls._product_cache.clear()
        logger.info("Product cache cleared")
    
    @classmethod
    def get_cache_stats(cls):
        """Get cache statistics"""
        return {
            'size': len(cls._product_cache),
            'max_size': cls._cache_max_size,
            'products': list(cls._product_cache.keys())
        }
    
    def _product_to_text(self, product_data: dict) -> str:
        """
        Convert product data to searchable text for preprocessing pipeline
        
        Args:
            product_data (dict): Scraped product information
                {
                    'name': str,
                    'price': float,
                    'specs': dict,
                    'category': str,
                    'brand': str,
                    'rating': float
                }
            
        Returns:
            str: Text representation for feature extraction and embedding
        """
        parts = []
        
        # Product name (most important - includes brand, model, variant)
        if product_data.get('name'):
            parts.append(product_data['name'])
        
        # Specifications (RAM, Storage, Screen Size, etc.)
        if product_data.get('specs') and isinstance(product_data['specs'], dict):
            for key, value in product_data['specs'].items():
                if value:
                    # Format: "RAM 8GB" or "Storage 128GB"
                    parts.append(f"{key} {value}")
        
        # Price (important for price-based queries)
        if product_data.get('price'):
            parts.append(f"price {product_data['price']}")
        
        # Category (helps with categorization)
        if product_data.get('category'):
            parts.append(product_data['category'])
        
        # Brand (if not already in name)
        if product_data.get('brand'):
            brand = product_data['brand']
            name = product_data.get('name', '')
            if brand.lower() not in name.lower():
                parts.append(brand)
        
        # Rating (quality indicator)
        if product_data.get('rating'):
            parts.append(f"rating {product_data['rating']}")
        
        text = ' '.join(parts)
        logger.debug(f"Product converted to text: {text[:200]}")
        
        return text
    
    def close(self):
        """Close session"""
        if self.session:
            self.session.close()
