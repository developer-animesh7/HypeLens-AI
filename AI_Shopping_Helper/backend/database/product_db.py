"""
Product database operations
"""

from backend.database.db_connection import DatabaseConnection
import json
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class ProductDatabase:
    """Handles product-related database operations"""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def find_alternatives(self, category: str, target_score: float, max_price: float, limit: int = 10) -> List[Dict]:
        """
        Find alternative products with similar quality but lower price
        
        Args:
            category (str): Product category
            target_score (float): Target quality score
            max_price (float): Maximum price
            limit (int): Maximum number of results
            
        Returns:
            List[Dict]: List of alternative products
        """
        try:
            # Find products in the same category with similar or better scores and lower prices
            query = """
            SELECT id, name, category, price, rating, platform, url, specs, 
                   quality_score, final_score, image_url, description
            FROM products 
            WHERE category = :category 
                AND price <= :max_price 
                AND final_score >= :min_score
            ORDER BY final_score DESC, price ASC
            LIMIT :limit
            """
            
            # Allow some tolerance in score matching (±10%)
            min_score = target_score * 0.9
            
            params = {
                "category": category,
                "max_price": max_price,
                "min_score": min_score,
                "limit": limit,
            }
            results = self.db.execute_query(query, params)
            
            # Process results
            alternatives = []
            for row in results:
                product = dict(row)
                
                # Parse JSON specs
                if product['specs']:
                    try:
                        product['specs'] = json.loads(product['specs'])
                    except json.JSONDecodeError:
                        product['specs'] = {}
                
                alternatives.append(product)
            
            return alternatives
            
        except Exception as e:
            logger.error(f"Error finding alternatives: {str(e)}")
            return []
    
    def get_categories(self) -> List[Dict]:
        """Get all available categories"""
        try:
            query = "SELECT name, display_name, description FROM categories ORDER BY display_name"
            results = self.db.execute_query(query)
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Error fetching categories: {str(e)}")
            return []
    
    def get_products_by_category(self, category: str, page: int = 1, limit: int = 20) -> List[Dict]:
        """Get products by category with pagination"""
        try:
            offset = (page - 1) * limit
            
            query = """
            SELECT id, name, category, price, rating, platform, url, 
                   quality_score, final_score, image_url
            FROM products 
            WHERE category = :category 
            ORDER BY final_score DESC, price ASC
            LIMIT :limit OFFSET :offset
            """
            
            results = self.db.execute_query(query, {"category": category, "limit": limit, "offset": offset})
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Error fetching products by category: {str(e)}")
            return []
    
    def add_product(self, product_data: Dict) -> Optional[int]:
        """
        Add a new product to the database
        
        Args:
            product_data (dict): Product information
            
        Returns:
            int: Product ID if successful, None otherwise
        """
        try:
            query = """
            INSERT INTO products (name, category, price, rating, platform, url, specs, 
                                quality_score, final_score, image_url, description)
            VALUES (:name, :category, :price, :rating, :platform, :url, :specs, :quality_score, :final_score, :image_url, :description)
            RETURNING id
            """
            
            # Prepare data
            insert_data = {
                'name': product_data.get('name', ''),
                'category': product_data.get('category', 'general'),
                'price': product_data.get('price', 0),
                'rating': product_data.get('rating', 4.0),
                'platform': product_data.get('platform', ''),
                'url': product_data.get('url', ''),
                'specs': json.dumps(product_data.get('specs', {})),
                'quality_score': product_data.get('quality_score', 0),
                'final_score': product_data.get('final_score', 0),
                'image_url': product_data.get('image_url', ''),
                'description': product_data.get('description', ''),
            }
            rows = self.db.execute_query(query, insert_data)
            if rows:
                return rows[0].get('id') if isinstance(rows[0], dict) else dict(rows[0]).get('id')
            return None
            
        except Exception as e:
            logger.error(f"Error adding product: {str(e)}")
            return None
    
    def update_product(self, product_id: int, product_data: Dict) -> bool:
        """Update an existing product"""
        try:
            # Build dynamic update query
            update_fields = []
            params = {}
            
            allowed_fields = ['name', 'category', 'price', 'rating', 'platform', 'url', 
                            'specs', 'quality_score', 'final_score', 'image_url', 'description']
            
            for field in allowed_fields:
                if field in product_data:
                    update_fields.append(f"{field} = :{field}")
                    if field == 'specs':
                        params[field] = json.dumps(product_data[field])
                    else:
                        params[field] = product_data[field]
            
            if not update_fields:
                return False
            
            params['id'] = product_id
            query = f"UPDATE products SET {', '.join(update_fields)} WHERE id = :id"
            
            rows_affected = self.db.execute_update(query, params)
            return rows_affected > 0
            
        except Exception as e:
            logger.error(f"Error updating product: {str(e)}")
            return False
    
    def delete_product(self, product_id: int) -> bool:
        """Delete a product"""
        try:
            query = "DELETE FROM products WHERE id = :id"
            rows_affected = self.db.execute_update(query, {"id": product_id})
            return rows_affected > 0
            
        except Exception as e:
            logger.error(f"Error deleting product: {str(e)}")
            return False
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Get a product by ID"""
        try:
            query = """
            SELECT id, name, category, price, rating, platform, url, specs, 
                   quality_score, final_score, image_url, description,
                   created_at, updated_at
            FROM products 
            WHERE id = :id
            """
            
            results = self.db.execute_query(query, {"id": product_id})
            
            if results:
                product = dict(results[0])
                # Parse JSON specs
                if product['specs']:
                    try:
                        product['specs'] = json.loads(product['specs'])
                    except json.JSONDecodeError:
                        product['specs'] = {}
                return product
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching product by ID: {str(e)}")
            return None
    
    def search_products(self, query: str, category: str = None, limit: int = 20) -> List[Dict]:
        """Search products by name or description"""
        try:
            search_query = """
            SELECT id, name, category, price, rating, platform, url, 
                   quality_score, final_score, image_url
            FROM products 
            WHERE (name LIKE :q OR description LIKE :q)
            """
            
            params = {"q": f"%{query}%"}
            
            if category:
                search_query += " AND category = :category"
                params["category"] = category
            
            search_query += " ORDER BY final_score DESC, price ASC LIMIT :limit"
            params["limit"] = limit
            
            results = self.db.execute_query(search_query, params)
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Error searching products: {str(e)}")
            return []
    
    def store_feedback(self, feedback_data: Dict) -> Optional[int]:
        """Store user feedback"""
        try:
            query = """
            INSERT INTO user_feedback (product_id, user_rating, is_helpful, comments, user_ip)
            VALUES (:product_id, :user_rating, :is_helpful, :comments, :user_ip)
            RETURNING id
            """
            
            insert_data = {
                'product_id': feedback_data.get('product_id'),
                'user_rating': feedback_data.get('rating'),
                'is_helpful': feedback_data.get('helpful'),
                'comments': feedback_data.get('comments', ''),
                'user_ip': feedback_data.get('user_ip', ''),
            }
            rows = self.db.execute_query(query, insert_data)
            if rows:
                return rows[0].get('id') if isinstance(rows[0], dict) else dict(rows[0]).get('id')
            return None
            
        except Exception as e:
            logger.error(f"Error storing feedback: {str(e)}")
            return None
    
    def get_product_stats(self) -> Dict:
        """Get database statistics"""
        try:
            # Total products
            total_query = "SELECT COUNT(*) as total FROM products"
            total_result = self.db.execute_query(total_query)
            total_products = total_result[0]['total']
            
            # Products by category
            category_query = """
            SELECT category, COUNT(*) as count 
            FROM products 
            GROUP BY category 
            ORDER BY count DESC
            """
            category_results = self.db.execute_query(category_query)
            
            # Average prices by category
            price_query = """
            SELECT category, AVG(price) as avg_price, MIN(price) as min_price, MAX(price) as max_price
            FROM products 
            GROUP BY category
            """
            price_results = self.db.execute_query(price_query)
            
            return {
                'total_products': total_products,
                'categories': [dict(row) for row in category_results],
                'price_stats': [dict(row) for row in price_results]
            }
            
        except Exception as e:
            logger.error(f"Error fetching product stats: {str(e)}")
            return {}
    
    def batch_insert_products(self, products: List[Dict]) -> int:
        """Batch insert multiple products"""
        try:
            query = """
            INSERT INTO products (name, category, price, rating, platform, url, specs, 
                                quality_score, final_score, image_url, description)
            VALUES (:name, :category, :price, :rating, :platform, :url, :specs, :quality_score, :final_score, :image_url, :description)
            """
            
            # Prepare data
            insert_data = []
            for product in products:
                data = {
                    'name': product.get('name', ''),
                    'category': product.get('category', 'general'),
                    'price': product.get('price', 0),
                    'rating': product.get('rating', 4.0),
                    'platform': product.get('platform', ''),
                    'url': product.get('url', ''),
                    'specs': json.dumps(product.get('specs', {})),
                    'quality_score': product.get('quality_score', 0),
                    'final_score': product.get('final_score', 0),
                    'image_url': product.get('image_url', ''),
                    'description': product.get('description', ''),
                }
                insert_data.append(data)
            
            rows_affected = self.db.execute_many(query, insert_data)
            return rows_affected
            
        except Exception as e:
            logger.error(f"Error batch inserting products: {str(e)}")
            return 0
