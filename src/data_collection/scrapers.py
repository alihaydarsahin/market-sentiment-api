import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from datetime import datetime
import os
from typing import List, Dict, Any

class BaseScraper:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = 'data/logs'
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f'{self.__class__.__name__}.log')
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

class EcommerceScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape_trendyol(self, url: str) -> List[Dict[str, Any]]:
        """Scrape product data from Trendyol"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            products = []
            
            for product in soup.find_all('div', class_='product-item'):
                name = product.find('h3').text.strip()
                price = product.find('span', class_='price').text.strip()
                products.append({
                    'name': name,
                    'price': price,
                    'source': 'trendyol',
                    'timestamp': datetime.now().isoformat()
                })
            
            self.logger.info(f"Scraped {len(products)} products from Trendyol")
            return products
        except Exception as e:
            self.logger.error(f"Error scraping Trendyol: {e}")
            return []

    def scrape_news(self, url: str) -> List[Dict[str, Any]]:
        """Scrape news articles from a given URL"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []
            
            for article in soup.find_all('article'):
                title = article.find('h2').text.strip()
                link = article.find('a')['href']
                articles.append({
                    'title': title,
                    'link': link,
                    'source': 'news',
                    'timestamp': datetime.now().isoformat()
                })
            
            self.logger.info(f"Scraped {len(articles)} news articles")
            return articles
        except Exception as e:
            self.logger.error(f"Error scraping news: {e}")
            return []

class SeleniumScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')

    def scrape_with_selenium(self, url: str, wait_time: int = 10) -> List[Dict[str, Any]]:
        """Scrape data using Selenium"""
        try:
            driver = webdriver.Chrome(options=self.options)
            driver.get(url)
            
            # Wait for content to load
            WebDriverWait(driver, wait_time).until(
                EC.presence_of_element_located((By.CLASS_NAME, "product-item"))
            )
            
            products = []
            elements = driver.find_elements(By.CLASS_NAME, "product-item")
            
            for element in elements:
                name = element.find_element(By.CLASS_NAME, "product-name").text
                price = element.find_element(By.CLASS_NAME, "product-price").text
                products.append({
                    'name': name,
                    'price': price,
                    'source': 'selenium',
                    'timestamp': datetime.now().isoformat()
                })
            
            driver.quit()
            self.logger.info(f"Scraped {len(products)} products using Selenium")
            return products
        except Exception as e:
            self.logger.error(f"Error scraping with Selenium: {e}")
            if 'driver' in locals():
                driver.quit()
            return [] 