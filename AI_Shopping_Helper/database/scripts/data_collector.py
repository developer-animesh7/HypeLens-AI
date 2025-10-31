"""
Data scraping utilities and scripts for building the product database
"""

import asyncio
import aiohttp
from backend.scraping.product_scraper import ProductScraper
from backend.ai_scoring.quality_scorer import QualityScorer
from backend.database.product_db import ProductDatabase
import logging
import time
from typing import List, Dict

logger = logging.getLogger(__name__)

class DataCollector:
    """Collects and processes product data for the database"""
    
    def __init__(self):
        self.scraper = ProductScraper()
        self.scorer = QualityScorer()
        self.db = ProductDatabase()
    
    async def collect_category_data(self, category: str, urls: List[str]) -> int:
        """
        Collect data for a specific category
        
        Args:
            category (str): Product category
            urls (list): List of product URLs to scrape
            
        Returns:
            int: Number of products successfully added
        """
        success_count = 0
        
        logger.info(f"Starting data collection for category: {category}")
        
        for i, url in enumerate(urls):
            try:
                logger.info(f"Processing URL {i+1}/{len(urls)}: {url}")
                
                # Scrape product data
                product_data = self.scraper.scrape_product(url)
                
                if not product_data:
                    logger.warning(f"Failed to scrape product from: {url}")
                    continue
                
                # Calculate quality scores
                quality_score = self.scorer.calculate_quality_score(
                    product_data['specs'], 
                    product_data['category']
                )
                
                final_score = self.scorer.calculate_final_score(
                    quality_score, 
                    product_data.get('rating', 4.0)
                )
                
                # Add scores to product data
                product_data['quality_score'] = quality_score
                product_data['final_score'] = final_score
                
                # Add to database
                product_id = self.db.add_product(product_data)
                
                if product_id:
                    success_count += 1
                    logger.info(f"Successfully added product: {product_data['name']}")
                else:
                    logger.warning(f"Failed to add product to database: {product_data['name']}")
                
                # Rate limiting - wait between requests
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error processing URL {url}: {str(e)}")
                continue
        
        logger.info(f"Data collection completed. Successfully added {success_count} products.")
        return success_count

# Sample URLs for different categories (for initial data collection)
SAMPLE_URLS = {
    'headphones': [
        # Add real URLs here for data collection
        'https://www.amazon.in/boat-rockerz-450-wireless-headphones',
        'https://www.flipkart.com/noise-colorfit-pro-4-bluetooth-calling',
        'https://www.amazon.in/sony-wh-ch720n-wireless-headphones',
    ],
    'smartphone': [
        'https://www.amazon.in/redmi-note-12-pro-smartphone',
        'https://www.flipkart.com/samsung-galaxy-m34-5g',
        'https://www.amazon.in/oneplus-nord-ce-3-lite',
    ],
    'trimmer': [
        'https://www.amazon.in/philips-bt3211-beard-trimmer',
        'https://www.flipkart.com/mi-beard-trimmer-1c',
        'https://www.amazon.in/havells-bt6203-grooming-kit',
    ],
    'mixer': [
        'https://www.amazon.in/preethi-blue-leaf-diamond-mixer',
        'https://www.flipkart.com/butterfly-rapid-mixer-grinder',
        'https://www.amazon.in/bajaj-rex-mixer-grinder',
    ]
}

async def populate_database():
    """Populate database with sample products"""
    collector = DataCollector()
    
    total_added = 0
    
    for category, urls in SAMPLE_URLS.items():
        try:
            count = await collector.collect_category_data(category, urls)
            total_added += count
            logger.info(f"Added {count} products for category: {category}")
            
            # Wait between categories
            await asyncio.sleep(5)
            
        except Exception as e:
            logger.error(f"Error collecting data for category {category}: {str(e)}")
    
    logger.info(f"Database population completed. Total products added: {total_added}")

if __name__ == "__main__":
    # Run the data collection
    asyncio.run(populate_database())
