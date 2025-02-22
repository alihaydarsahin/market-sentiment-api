import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import logging
import os
from datetime import datetime

# Create directories
os.makedirs("data/logs", exist_ok=True)
os.makedirs("data/figures", exist_ok=True)

# Logging settings
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/trendyol_tor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TrendyolTorScraper:
    def __init__(self):
        self.base_url = "https://www.trendyol.com"
        self.session = requests.Session()
        
        # Tor proxy settings
        self.proxies = {
            'http': 'socks5h://127.0.0.1:9150',
            'https': 'socks5h://127.0.0.1:9150'
        }
        
        # Realistic headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/122.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.trendyol.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1'
        }
        
        # Check Tor connection
        if not self.check_tor():
            raise Exception("Tor connection failed! Make sure Tor Browser is running.")
        
        # Get initial cookies
        try:
            self.session.get(
                self.base_url,
                headers=self.headers,
                proxies=self.proxies,
                timeout=30
            )
            time.sleep(2)
        except Exception as e:
            logger.error(f"Initial connection error: {e}")
    
    def get_products(self, category, limit=10):
        """Collect products"""
        products = []
        page = 1
        
        while len(products) < limit:
            try:
                url = f"{self.base_url}/sr?q={category}&pi={page}"
                logger.info(f"Loading page {page}: {url}")
                
                response = self.session.get(
                    url,
                    headers=self.headers,
                    proxies=self.proxies,
                    timeout=30
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to load page: {response.status_code}")
                    break
                    
                soup = BeautifulSoup(response.content, 'html.parser')
                product_cards = soup.select('div.p-card-wrppr')
                
                if not product_cards:
                    logger.warning("No products found on page")
                    break
                    
                for card in product_cards:
                    try:
                        product = {
                            'name': card.select_one('span.prdct-desc-cntnr-name').text.strip(),
                            'price': card.select_one('div.prc-box-dscntd').text.strip(),
                            'brand': card.select_one('span.prdct-desc-cntnr-ttl').text.strip(),
                            'category': category,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        # Link ekle
                        link = card.select_one('a')
                        if link and link.get('href'):
                            product['link'] = self.base_url + link['href']
                        
                        products.append(product)
                        logger.info(f"Added product: {product['name'][:50]}...")
                        
                        if len(products) >= limit:
                            break
                            
                    except Exception as e:
                        logger.warning(f"Failed to extract product data: {e}")
                        continue
                
                # Random delay between requests
                wait_time = random.uniform(3, 7)
                logger.info(f"Waiting: {wait_time:.2f} seconds")
                time.sleep(wait_time)
                page += 1
                
            except Exception as e:
                logger.error(f"Page error: {e}")
                time.sleep(5)
                continue
                
        return products[:limit]
    
    def save_products(self, products, category):
        """Save products"""
        try:
            if not products:
                logger.warning("No products to save!")
                return
                
            df = pd.DataFrame(products)
            filename = f"data/raw/trendyol_{category}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
            df.to_csv(filename, index=False)
            logger.info(f"Saved {len(products)} products to {filename}")
            
        except Exception as e:
            logger.error(f"Save error: {e}")

    def check_tor(self):
        """Check Tor connection"""
        try:
            response = requests.get(
                'https://api.ipify.org?format=json',
                proxies=self.proxies,
                timeout=30
            )
            ip = response.json()['ip']
            logger.info(f"Tor IP: {ip}")
            return True
        except Exception as e:
            logger.error(f"Tor connection error: {e}")
            return False

def main():
    try:
        print("Make sure Tor Browser is running...")
        time.sleep(2)
        
        scraper = TrendyolTorScraper()
        print("Starting scraping... Press Ctrl+C to stop")
        
        # Test category
        category = "laptop"
        products = scraper.get_products(category, limit=10)
        
        if products:
            scraper.save_products(products, category)
            
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        logger.error(f"Program error: {e}")

if __name__ == "__main__":
    main() 