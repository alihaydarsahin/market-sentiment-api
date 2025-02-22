import requests
import pandas as pd
import time
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import logging
import json

# Create directories
os.makedirs("data/logs", exist_ok=True)
os.makedirs("data/raw", exist_ok=True)

# Logging settings
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/api_collector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load .env file
load_dotenv()

# Get API key securely
API_KEY = os.getenv('NEWS_API_KEY')
if not API_KEY:
    logger.error("NEWS_API_KEY not found! Please check your .env file.")
    raise ValueError("NEWS_API_KEY not found! Please check your .env file.")

class NewsAPICollector:
    def __init__(self, max_retries=3, retry_delay=5):
        self.base_url = "https://newsapi.org/v2/everything"
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.params = {
            "q": "technology OR business OR economy",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 100,
            "apiKey": API_KEY
        }
        
    def validate_response(self, data):
        """Validate API response"""
        if not isinstance(data, dict):
            return False
        if "articles" not in data:
            return False
        if not isinstance(data["articles"], list):
            return False
        return True
    
    def fetch_news(self):
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching news... Attempt {attempt + 1}/{self.max_retries}")
                response = requests.get(self.base_url, params=self.params)
                response.raise_for_status()
                
                data = response.json()
                if not self.validate_response(data):
                    logger.error("Invalid API response")
                    continue
                
                articles = data["articles"]
                logger.info(f"Successfully fetched {len(articles)} articles")
                return articles
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching data: {e}")
                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                continue
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {e}")
                continue
                
        logger.error("Maximum retry attempts reached")
        return []
    
    def clean_data(self, news_list):
        """Clean and validate data"""
        cleaned_news = []
        for article in news_list:
            try:
                # Check required fields
                required_fields = ["title", "description", "url", "publishedAt"]
                if not all(field in article for field in required_fields):
                    continue
                
                # Clean and format data
                cleaned_article = {
                    "title": article["title"].strip(),
                    "description": article["description"].strip() if article["description"] else "",
                    "url": article["url"],
                    "publishedAt": article["publishedAt"],
                    "source": article["source"]["name"] if "source" in article else "Unknown"
                }
                
                cleaned_news.append(cleaned_article)
            except Exception as e:
                logger.error(f"Data cleaning error: {e}")
                continue
                
        return cleaned_news
    
    def save_news_to_csv(self, news_list):
        """Save news data to CSV"""
        if not news_list:
            logger.warning("No news to save!")
            return
        
        try:
            # Clean data
            cleaned_news = self.clean_data(news_list)
            if not cleaned_news:
                logger.warning("No news left after cleaning!")
                return
            
            # Create filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"data/raw/news_data_{timestamp}.csv"
            
            # Create DataFrame and save
            df = pd.DataFrame(cleaned_news)
            df.to_csv(filename, index=False)
            logger.info(f"Saved {len(cleaned_news)} articles to {filename}")
            
        except Exception as e:
            logger.error(f"File saving error: {e}")

if __name__ == "__main__":
    try:
        collector = NewsAPICollector()
        # Son 7 günün haberlerini al
        from_date = datetime.now() - timedelta(days=7)
        collector.params["from"] = from_date.strftime('%Y-%m-%d')
        
        news_data = collector.fetch_news()
        collector.save_news_to_csv(news_data)
        logger.info("Haber toplama işlemi tamamlandı!")
        
    except Exception as e:
        logger.error(f"Program çalışırken hata oluştu: {e}") 