import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class NewsCollector:
    def __init__(self):
        self.api_key = os.getenv('NEWS_API_KEY')
        self.base_url = "https://newsapi.org/v2/everything"
        self.logger = logging.getLogger(__name__)
        
    def collect_news(self):
        """Collect news articles"""
        try:
            params = {
                'q': 'technology OR ecommerce OR retail',
                'language': 'en',
                'sortBy': 'publishedAt',
                'apiKey': self.api_key,
                'pageSize': 100
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            articles = response.json()['articles']
            self.logger.info(f"Collected {len(articles)} news articles")
            
            return articles
            
        except Exception as e:
            self.logger.error(f"Error collecting news: {e}")
            return [] 