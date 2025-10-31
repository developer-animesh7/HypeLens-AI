"""
Product scraper for extracting product information from e-commerce websites
"""

import requests
from bs4 import BeautifulSoup
# Selenium is optional; fall back gracefully if it's not installed
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
except Exception:  # ImportError or runtime issues
    webdriver = None  # type: ignore
    Options = None  # type: ignore
    By = None  # type: ignore
import re
import json
import time
import logging

logger = logging.getLogger(__name__)

class ProductScraper:
    """Scrapes product information from various e-commerce platforms"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Chrome options for Selenium (only if Selenium is available)
        self.chrome_options = None
        if Options is not None:
            self.chrome_options = Options()
            self.chrome_options.add_argument('--headless')
            self.chrome_options.add_argument('--no-sandbox')
            self.chrome_options.add_argument('--disable-dev-shm-usage')
    
    def scrape_product(self, url):
        """
        Scrape product information from a given URL
        
        Args:
            url (str): Product URL
            
        Returns:
            dict: Product information including name, price, specs, rating
        """
        try:
            # Determine platform and use appropriate scraper
            if 'amazon' in url.lower():
                return self._scrape_amazon(url)
            elif 'flipkart' in url.lower():
                return self._scrape_flipkart(url)
            elif 'myntra' in url.lower():
                return self._scrape_myntra(url)
            else:
                return self._scrape_generic(url)
                
        except Exception as e:
            logger.error(f"Error scraping product from {url}: {str(e)}")
            return None
    
    def _scrape_amazon(self, url):
        """Scrape Amazon product"""
        try:
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract product information
            name = self._extract_amazon_name(soup)
            price = self._extract_amazon_price(soup)
            rating = self._extract_amazon_rating(soup)
            specs = self._extract_amazon_specs(soup)
            category = self._determine_category(name, specs)
            
            return {
                'name': name,
                'price': price,
                'rating': rating,
                'specs': specs,
                'category': category,
                'platform': 'amazon',
                'url': url
            }
            
        except Exception as e:
            logger.error(f"Error scraping Amazon product: {str(e)}")
            return None
    
    def _scrape_flipkart(self, url):
        """Scrape Flipkart product"""
        try:
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract product information
            name = self._extract_flipkart_name(soup)
            price = self._extract_flipkart_price(soup)
            rating = self._extract_flipkart_rating(soup)
            specs = self._extract_flipkart_specs(soup)
            category = self._determine_category(name, specs)
            
            return {
                'name': name,
                'price': price,
                'rating': rating,
                'specs': specs,
                'category': category,
                'platform': 'flipkart',
                'url': url
            }
            
        except Exception as e:
            logger.error(f"Error scraping Flipkart product: {str(e)}")
            return None
    
    def _scrape_myntra(self, url):
        """Scrape Myntra product"""
        try:
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract product information
            name = self._extract_myntra_name(soup)
            price = self._extract_myntra_price(soup)
            rating = self._extract_myntra_rating(soup)
            specs = self._extract_myntra_specs(soup)
            category = self._determine_category(name, specs)
            
            return {
                'name': name,
                'price': price,
                'rating': rating,
                'specs': specs,
                'category': category,
                'platform': 'myntra',
                'url': url
            }
            
        except Exception as e:
            logger.error(f"Error scraping Myntra product: {str(e)}")
            return None
    
    def _scrape_generic(self, url):
        """Generic scraper for unknown platforms"""
        try:
            soup = None
            if webdriver is not None and self.chrome_options is not None:
                # Use Selenium for JavaScript-heavy sites when available
                driver = webdriver.Chrome(options=self.chrome_options)
                driver.get(url)
                time.sleep(3)  # Wait for page to load
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                driver.quit()
            else:
                # Fallback to simple requests + BeautifulSoup parsing
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic information
            name = self._extract_generic_name(soup)
            price = self._extract_generic_price(soup)
            rating = self._extract_generic_rating(soup)
            specs = self._extract_generic_specs(soup)
            category = self._determine_category(name, specs)
            
            return {
                'name': name,
                'price': price,
                'rating': rating,
                'specs': specs,
                'category': category,
                'platform': 'generic',
                'url': url
            }
            
        except Exception as e:
            logger.error(f"Error scraping generic product: {str(e)}")
            return None
    
    def _extract_amazon_name(self, soup):
        """Extract product name from Amazon"""
        selectors = [
            '#productTitle',
            '.product-title',
            'h1'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
        return "Unknown Product"
    
    def _extract_amazon_price(self, soup):
        """Extract price from Amazon"""
        price_selectors = [
            '.a-price-whole',
            '.a-offscreen',
            '[data-a-price-amount]'
        ]
        
        for selector in price_selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text().strip()
                price = self._parse_price(price_text)
                if price:
                    return price
        return 0
    
    def _extract_amazon_rating(self, soup):
        """Extract rating from Amazon"""
        rating_element = soup.select_one('[data-hook="average-star-rating"] .a-offscreen')
        if rating_element:
            rating_text = rating_element.get_text().strip()
            match = re.search(r'(\d+\.?\d*)', rating_text)
            if match:
                return float(match.group(1))
        return 4.0  # Default rating
    
    def _extract_amazon_specs(self, soup):
        """Extract specifications from Amazon"""
        specs = {}
        
        # Feature bullets
        feature_bullets = soup.select('#feature-bullets ul li')
        for bullet in feature_bullets:
            text = bullet.get_text().strip()
            if ':' in text:
                key, value = text.split(':', 1)
                specs[key.strip()] = value.strip()
        
        # Technical details table
        tech_table = soup.select('#tech tbody tr')
        for row in tech_table:
            cells = row.select('td')
            if len(cells) == 2:
                key = cells[0].get_text().strip()
                value = cells[1].get_text().strip()
                specs[key] = value
        
        return specs
    
    def _extract_flipkart_name(self, soup):
        """Extract product name from Flipkart"""
        selectors = [
            '.B_NuCI',
            'h1',
            '._35KyD6'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
        return "Unknown Product"
    
    def _extract_flipkart_price(self, soup):
        """Extract price from Flipkart"""
        price_selectors = [
            '._30jeq3',
            '._1_WHN1',
            '[class*="price"]'
        ]
        
        for selector in price_selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text().strip()
                price = self._parse_price(price_text)
                if price:
                    return price
        return 0
    
    def _extract_flipkart_rating(self, soup):
        """Extract rating from Flipkart"""
        rating_element = soup.select_one('._3LWZlK')
        if rating_element:
            rating_text = rating_element.get_text().strip()
            match = re.search(r'(\d+\.?\d*)', rating_text)
            if match:
                return float(match.group(1))
        return 4.0
    
    def _extract_flipkart_specs(self, soup):
        """Extract specifications from Flipkart"""
        specs = {}
        
        # Specifications table
        spec_tables = soup.select('._1s_Smc table tr')
        for row in spec_tables:
            cells = row.select('td')
            if len(cells) == 2:
                key = cells[0].get_text().strip()
                value = cells[1].get_text().strip()
                specs[key] = value
        
        return specs
    
    def _extract_myntra_name(self, soup):
        """Extract product name from Myntra"""
        selectors = [
            '.pdp-name',
            'h1',
            '.product-title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
        return "Unknown Product"
    
    def _extract_myntra_price(self, soup):
        """Extract price from Myntra"""
        price_selectors = [
            '.pdp-price',
            '[class*="price"]'
        ]
        
        for selector in price_selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text().strip()
                price = self._parse_price(price_text)
                if price:
                    return price
        return 0
    
    def _extract_myntra_rating(self, soup):
        """Extract rating from Myntra"""
        rating_element = soup.select_one('.index-overallRating')
        if rating_element:
            rating_text = rating_element.get_text().strip()
            match = re.search(r'(\d+\.?\d*)', rating_text)
            if match:
                return float(match.group(1))
        return 4.0
    
    def _extract_myntra_specs(self, soup):
        """Extract specifications from Myntra"""
        specs = {}
        
        # Product details
        detail_items = soup.select('.index-row')
        for item in detail_items:
            key_elem = item.select_one('.index-rowKey')
            value_elem = item.select_one('.index-rowValue')
            if key_elem and value_elem:
                key = key_elem.get_text().strip()
                value = value_elem.get_text().strip()
                specs[key] = value
        
        return specs
    
    def _extract_generic_name(self, soup):
        """Extract product name from generic site"""
        selectors = [
            'h1',
            '.product-title',
            '.product-name',
            '[class*="title"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
        return "Unknown Product"
    
    def _extract_generic_price(self, soup):
        """Extract price from generic site"""
        price_text = soup.get_text()
        
        # Look for common price patterns
        price_patterns = [
            r'₹[\s]*([0-9,]+)',
            r'Rs\.?[\s]*([0-9,]+)',
            r'INR[\s]*([0-9,]+)',
            r'Price:[\s]*₹?[\s]*([0-9,]+)'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, price_text)
            if match:
                price_str = match.group(1).replace(',', '')
                try:
                    return int(price_str)
                except ValueError:
                    continue
        
        return 0
    
    def _extract_generic_rating(self, soup):
        """Extract rating from generic site"""
        text = soup.get_text()
        
        # Look for rating patterns
        rating_patterns = [
            r'(\d+\.?\d*)\s*/\s*5',
            r'Rating:[\s]*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*stars?'
        ]
        
        for pattern in rating_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        
        return 4.0
    
    def _extract_generic_specs(self, soup):
        """Extract specifications from generic site"""
        specs = {}
        
        # Look for common specification patterns
        text = soup.get_text()
        
        # Common spec patterns
        spec_patterns = [
            r'Battery[\s]*:[\s]*([^\\n]+)',
            r'Display[\s]*:[\s]*([^\\n]+)',
            r'RAM[\s]*:[\s]*([^\\n]+)',
            r'Storage[\s]*:[\s]*([^\\n]+)',
            r'Camera[\s]*:[\s]*([^\\n]+)'
        ]
        
        for pattern in spec_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                key = pattern.split('[')[0]
                value = match.group(1).strip()
                specs[key] = value
        
        return specs
    
    def _parse_price(self, price_text):
        """Parse price from text"""
        # Remove currency symbols and commas
        price_clean = re.sub(r'[₹Rs.,]', '', price_text)
        
        # Extract number
        match = re.search(r'(\d+)', price_clean)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass
        
        return 0
    
    def _determine_category(self, name, specs):
        """Determine product category based on name and specs"""
        name_lower = name.lower()
        specs_text = ' '.join(specs.values()).lower()
        combined_text = f"{name_lower} {specs_text}"
        
        categories = {
            'headphones': ['headphone', 'earphone', 'earbud', 'audio', 'sound'],
            'smartphone': ['phone', 'mobile', 'smartphone', 'android', 'ios'],
            'laptop': ['laptop', 'notebook', 'computer', 'pc'],
            'trimmer': ['trimmer', 'shaver', 'grooming'],
            'mixer': ['mixer', 'grinder', 'blender'],
            'charger': ['charger', 'adapter', 'cable'],
            'clothing': ['shirt', 'pant', 'dress', 'jacket', 'wear'],
            'shoes': ['shoe', 'sneaker', 'boot', 'sandal']
        }
        
        for category, keywords in categories.items():
            if any(keyword in combined_text for keyword in keywords):
                return category
        
        return 'general'
