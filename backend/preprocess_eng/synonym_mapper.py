"""
Synonym Mapper - Maps synonyms using WordNet and custom e-commerce dictionary
Expands query with relevant synonyms for better product matching
"""

import logging
from typing import List, Set

logger = logging.getLogger(__name__)

# Try to import NLTK
try:
    import nltk
    from nltk.corpus import wordnet as wn
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    logger.warning("NLTK not installed. Synonym mapping will use custom dictionary only.")


class SynonymMapper:
    """Maps words to their synonyms for query expansion"""
    
    # Custom Indian e-commerce synonym dictionary
    ECOMMERCE_SYNONYMS = {
        # Devices
        'mobile': ['phone', 'smartphone', 'cellphone', 'handset'],
        'phone': ['mobile', 'smartphone', 'cellphone', 'handset'],
        'smartphone': ['mobile', 'phone', 'cellphone', 'handset'],
        'laptop': ['notebook', 'computer', 'pc'],
        'notebook': ['laptop', 'computer'],
        'tablet': ['ipad', 'tab'],
        'tv': ['television', 'smart tv', 'led tv'],
        
        # Features
        'wireless': ['bluetooth', 'wifi', 'cordless'],
        'bluetooth': ['wireless', 'bt'],
        'wired': ['cable', 'corded'],
        'touchscreen': ['touch screen', 'touch display'],
        
        # Storage
        'storage': ['memory', 'space', 'capacity'],
        'memory': ['ram', 'storage'],
        'ssd': ['solid state', 'flash storage'],
        'hdd': ['hard disk', 'hard drive'],
        
        # Display
        'display': ['screen', 'monitor', 'panel'],
        'screen': ['display', 'monitor'],
        'amoled': ['oled', 'super amoled'],
        'lcd': ['led', 'ips'],
        
        # Camera
        'camera': ['cam', 'lens', 'sensor'],
        'megapixel': ['mp', 'mpixel'],
        'selfie': ['front camera', 'front cam'],
        
        # Battery
        'battery': ['mah', 'power', 'backup'],
        'charger': ['adapter', 'charging'],
        'fast charging': ['quick charge', 'rapid charge', 'turbo charge'],
        
        # Audio
        'headphone': ['headset', 'earphone', 'earbuds'],
        'earphone': ['headphone', 'earbuds', 'earpiece'],
        'earbuds': ['earpods', 'tws', 'true wireless'],
        'speaker': ['audio', 'sound'],
        
        # Quality
        'cheap': ['budget', 'affordable', 'inexpensive', 'economical'],
        'expensive': ['premium', 'high-end', 'costly'],
        'best': ['top', 'excellent', 'great', 'finest'],
        'good': ['nice', 'decent', 'quality'],
        'new': ['latest', 'newest', 'recent'],
        
        # Brands (common misspellings)
        'oneplus': ['one plus', '1+'],
        'realme': ['real me'],
        'poco': ['pocophone'],
        
        # Indian terms
        'lakh': ['100000', '1 lakh', '100k'],
        'offer': ['deal', 'discount', 'sale'],
        'flipkart': ['fk', 'flip kart'],
        'amazon': ['amzn'],
    }
    
    def __init__(self, max_synonyms=3):
        """
        Initialize Synonym Mapper
        
        Args:
            max_synonyms (int): Maximum number of synonyms to return per word
        """
        self.max_synonyms = max_synonyms
        self.nltk_available = NLTK_AVAILABLE
        
        if self.nltk_available:
            self._ensure_wordnet()
    
    def _ensure_wordnet(self):
        """Ensure WordNet is downloaded"""
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            logger.info("Downloading WordNet corpus...")
            try:
                nltk.download('wordnet', quiet=True)
                nltk.download('omw-1.4', quiet=True)  # Open Multilingual WordNet
            except Exception as e:
                logger.error(f"Failed to download WordNet: {e}")
                self.nltk_available = False
    
    def get_synonyms(self, word: str, use_wordnet=True) -> Set[str]:
        """
        Get synonyms for a word
        
        Args:
            word (str): Input word
            use_wordnet (bool): Also use WordNet (in addition to custom dict)
            
        Returns:
            Set[str]: Set of synonyms
        """
        word = word.lower().strip()
        synonyms = set()
        
        # Get from custom dictionary
        if word in self.ECOMMERCE_SYNONYMS:
            synonyms.update(self.ECOMMERCE_SYNONYMS[word])
        
        # Get from WordNet
        if use_wordnet and self.nltk_available:
            wn_synonyms = self._get_wordnet_synonyms(word)
            synonyms.update(wn_synonyms)
        
        # Limit number of synonyms
        synonyms = list(synonyms)[:self.max_synonyms]
        
        if synonyms:
            logger.debug(f"Synonyms for '{word}': {synonyms}")
        
        return set(synonyms)
    
    def _get_wordnet_synonyms(self, word: str) -> Set[str]:
        """
        Get synonyms from WordNet
        
        Args:
            word (str): Input word
            
        Returns:
            Set[str]: Set of synonyms from WordNet
        """
        synonyms = set()
        
        try:
            for synset in wn.synsets(word):
                for lemma in synset.lemmas():
                    synonym = lemma.name().replace('_', ' ').lower()
                    if synonym != word:
                        synonyms.add(synonym)
        except Exception as e:
            logger.warning(f"WordNet lookup failed for '{word}': {e}")
        
        return synonyms
    
    def expand_query(self, text: str, preserve_original=True) -> str:
        """
        Expand query with synonyms
        
        Args:
            text (str): Input query
            preserve_original (bool): Keep original words in expanded query
            
        Returns:
            str: Expanded query with synonyms
        """
        words = text.lower().split()
        expanded_words = []
        
        for word in words:
            if preserve_original:
                expanded_words.append(word)
            
            # Add synonyms
            synonyms = self.get_synonyms(word)
            expanded_words.extend(synonyms)
        
        expanded = ' '.join(expanded_words)
        
        if expanded != text.lower():
            logger.info(f"Query expanded: '{text}' -> '{expanded[:100]}...'")
        
        return expanded
    
    def expand_tokens(self, tokens: List[str]) -> List[str]:
        """
        Expand list of tokens with synonyms
        
        Args:
            tokens (List[str]): List of tokens
            
        Returns:
            List[str]: Expanded list with synonyms
        """
        expanded = []
        
        for token in tokens:
            expanded.append(token)
            synonyms = self.get_synonyms(token)
            expanded.extend(synonyms)
        
        return expanded
    
    def add_custom_synonyms(self, word: str, synonyms: List[str]):
        """
        Add custom synonyms to dictionary
        
        Args:
            word (str): Word
            synonyms (List[str]): List of synonyms
        """
        word = word.lower()
        if word not in self.ECOMMERCE_SYNONYMS:
            self.ECOMMERCE_SYNONYMS[word] = []
        
        self.ECOMMERCE_SYNONYMS[word].extend(synonyms)
        logger.info(f"Added synonyms for '{word}': {synonyms}")
