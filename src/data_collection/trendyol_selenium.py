from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import random
import logging
import os
from datetime import datetime

# Create directories
os.makedirs("data/logs", exist_ok=True)
os.makedirs("data/raw", exist_ok=True)

# Logging settings
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/trendyol_selenium.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TrendyolSeleniumScraper:
    def __init__(self):
        self.base_url = "https://www.trendyol.com"
        self.setup_driver()
        
    def setup_driver(self):
        """Configure Selenium driver"""
        try:
            options = Options()
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--start-maximized')
            # options.add_argument('--headless')  # Optional headless mode
            
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 10)
            logger.info("Chrome driver started successfully")
            
        except Exception as e:
            logger.error(f"Driver initialization error: {e}")
            raise
    
    def get_products(self, category, limit=10):
        """Collect products"""
        products = []
        page = 1
        
        try:
            while len(products) < limit:
                url = f"{self.base_url}/sr?q={category}&pi={page}"
                logger.info(f"Loading page {page}: {url}")
                
                self.driver.get(url)
                time.sleep(random.uniform(2, 4))  # Random delay
                
                # Wait for product cards
                product_cards = self.wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.p-card-wrppr"))
                )
                
                if not product_cards:
                    logger.warning("No products found on page")
                    break
                
                for card in product_cards:
                    try:
                        product = {
                            'name': card.find_element(By.CSS_SELECTOR, "span.prdct-desc-cntnr-name").text,
                            'price': card.find_element(By.CSS_SELECTOR, "div.prc-box-dscntd").text,
                            'brand': card.find_element(By.CSS_SELECTOR, "span.prdct-desc-cntnr-ttl").text,
                            'category': category,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        products.append(product)
                        logger.info(f"Added product: {product['name'][:50]}...")
                        
                        if len(products) >= limit:
                            break
                            
                    except Exception as e:
                        logger.warning(f"Failed to extract product data: {e}")
                        continue
                
                page += 1
                time.sleep(random.uniform(1, 3))
                
        except Exception as e:
            logger.error(f"Data collection error: {e}")
            
        finally:
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
    
    def close(self):
        """Close driver"""
        try:
            self.driver.quit()
            logger.info("Driver closed")
        except:
            pass

def main():
    try:
        scraper = TrendyolSeleniumScraper()
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
    finally:
        scraper.close()

if __name__ == "__main__":
    main() 