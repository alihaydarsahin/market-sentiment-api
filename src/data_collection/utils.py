import os
import logging
import time
import random
from urllib.parse import urljoin
from typing import List, Dict, Any, Union, Tuple, Optional


def create_directories(directories: List[str]) -> None:
    """Create all necessary directories"""
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"Created directory: {directory}")
        except Exception as e:
            print(f"Error creating directory {directory}: {e}")


def setup_logging(log_file: str) -> None:
    """Set up logging configuration"""
    # Create log directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
        
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


class RequestHandler:
    """
    Handle HTTP requests with built-in rate limiting,
    retry functionality, and URL building capabilities.
    """
    def __init__(self, delay: Tuple[float, float] = (3, 7), retry_count: int = 3):
        """
        Args:
            delay: Tuple of (min_delay, max_delay) in seconds between requests
            retry_count: Number of retry attempts on failure
        """
        self.delay = delay
        self.retry_count = retry_count
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def wait(self) -> None:
        """Wait between requests to respect rate limits"""
        time.sleep(random.uniform(*self.delay))
    
    def handle_response(self, response) -> bool:
        """Check response status
        
        Args:
            response: The HTTP response object
            
        Returns:
            bool: True if response is valid, False otherwise
        """
        if response and response.status_code == 200:
            return True
        return False
    
    def build_url(self, base_url: str, path: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Build URL with parameters
        
        Args:
            base_url: Base URL
            path: Path to append to base URL
            params: Dictionary of query parameters
            
        Returns:
            str: Complete URL with query parameters
        """
        url = urljoin(base_url, path)
        if params:
            param_list = []
            for key, value in params.items():
                param_list.append(f"{key}={value}")
            url = f"{url}{'&' if '?' in url else '?'}{'&'.join(param_list)}"
        return url 