import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import time
import logging
import random

# Create directories
os.makedirs("data/logs", exist_ok=True)
os.makedirs("data/raw", exist_ok=True)

# Logging settings
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/news_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NewsWebScraper:
    def __init__(self, max_retries=3, retry_delay=5):
        self.url = "https://news.google.com/search?q=technology&hl=en-US&gl=US&ceid=US:en"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def _get_soup(self, retries=0):
        """Get page content and convert to BeautifulSoup object"""
        try:
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
        except requests.RequestException as e:
            logger.error(f"Page fetch error: {e}")
            if retries < self.max_retries:
                wait_time = self.retry_delay * (retries + 1)
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                return self._get_soup(retries + 1)
            return None
    
    def clean_data(self, news_list):
        """Clean and validate data"""
        cleaned_news = []
        for news in news_list:
            try:
                # Check required fields
                if not all(key in news for key in ["headline", "link"]):
                    continue
                
                # Check if headline is empty
                if not news["headline"].strip():
                    continue
                
                # Check link format
                if not news["link"].startswith("https://"):
                    continue
                
                cleaned_news.append(news)
            except Exception as e:
                logger.error(f"Data cleaning error: {e}")
                continue
        
        return cleaned_news
    
    def scrape_google_news(self):
        try:
            soup = self._get_soup()
            if not soup:
                logger.error("Could not get page content")
                return []
            
            articles = soup.find_all("article")
            logger.info(f"Found {len(articles)} articles")
            
            news_data = []
            for article in articles:
                try:
                    headline = article.find("a").text.strip()
                    link = "https://news.google.com" + article.find("a")["href"][1:]
                    time_element = article.find("time")
                    publish_date = time_element["datetime"] if time_element else None
                    
                    news_data.append({
                        "headline": headline,
                        "link": link,
                        "publish_date": publish_date,
                        "scrape_time": datetime.now().isoformat()
                    })
                except AttributeError as e:
                    logger.error(f"Article parsing error: {e}")
                    continue
            
            return news_data
            
        except Exception as e:
            logger.error(f"News scraping error: {e}")
            return []
    
    def save_news(self, news_list):
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
            filename = f"data/raw/scraped_news_{timestamp}.csv"
            
            # Create DataFrame and save
            df = pd.DataFrame(cleaned_news)
            df.to_csv(filename, index=False)
            logger.info(f"Saved {len(cleaned_news)} news to {filename}")
            
        except Exception as e:
            logger.error(f"File saving error: {e}")

if __name__ == "__main__":
    try:
        scraper = NewsWebScraper()
        scraped_news = scraper.scrape_google_news()
        scraper.save_news(scraped_news)
        logger.info("News scraping completed!")
        
    except Exception as e:
        logger.error(f"Program error: {e}") 