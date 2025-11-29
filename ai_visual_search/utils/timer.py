"""Timer utility for performance monitoring"""

import time
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@contextmanager
def timer(operation_name: str):
    """Context manager for timing operations"""
    start = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start
        logger.info(f"⏱️  {operation_name}: {elapsed:.3f}s")


class Timer:
    """Simple timer class"""
    
    def __init__(self):
        self.start_time = None
    
    def start(self):
        """Start timer"""
        self.start_time = time.time()
    
    def elapsed(self) -> float:
        """Get elapsed time in seconds"""
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time
    
    def reset(self):
        """Reset timer"""
        self.start_time = time.time()
