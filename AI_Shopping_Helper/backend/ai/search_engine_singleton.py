"""
Singleton pattern for HybridSearchEngine to ensure model loads only once
"""
from typing import Optional
from backend.ai.hybrid_search import HybridSearchEngine


class SearchEngineSingleton:
    """
    Singleton to ensure HybridSearchEngine (with CLIP model) loads only ONCE
    """
    _instance: Optional[HybridSearchEngine] = None
    _initialized: bool = False
    
    @classmethod
    def get_instance(cls) -> HybridSearchEngine:
        """Get or create the singleton HybridSearchEngine instance"""
        if cls._instance is None:
            print("Initializing HybridSearchEngine singleton (loading CLIP model)...")
            cls._instance = HybridSearchEngine()
            cls._initialized = True
            print("HybridSearchEngine singleton ready!")
        return cls._instance
    
    @classmethod
    def is_initialized(cls) -> bool:
        """Check if the singleton has been initialized"""
        return cls._initialized


# Convenience function
def get_search_engine() -> HybridSearchEngine:
    """Get the singleton search engine instance"""
    return SearchEngineSingleton.get_instance()
