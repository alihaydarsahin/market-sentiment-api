import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
import os
from datetime import datetime
from stem import Signal
from stem.control import Controller
from requests.exceptions import RequestException
import random
import signal
from base_scraper import BaseScraper
from utils.request_handler import RequestHandler
from urllib.robotparser import RobotFileParser

# Klasörleri oluştur
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/logs", exist_ok=True)

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/trendyol_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TrendyolScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.trendyol.com"
        self.request_handler = RequestHandler()
        self.session = requests.Session()
        self.rp = RobotFileParser()
        self.rp.set_url(f"{self.base_url}/robots.txt")
        self.check_robots_txt()
        
        # Headers ekleyelim
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        }
        
    def check_robots_txt(self):
        """robots.txt kontrolü"""
        try:
            self.rp.read()
            logger.info("robots.txt okundu")
            
            # Önemli path'leri kontrol et
            paths_to_check = [
                '/sr',  # arama sayfası
                '/product',  # ürün sayfası
                '/brand'  # marka sayfası
            ]
            
            for path in paths_to_check:
                can_fetch = self.rp.can_fetch("*", f"{self.base_url}{path}")
                logger.info(f"Path {path}: {'İzin var' if can_fetch else 'İZİN YOK'}")
                
            # Crawl delay kontrolü
            delay = self.rp.crawl_delay("*")
            if delay:
                logger.info(f"Minimum bekleme süresi: {delay} saniye")
                
        except Exception as e:
            logger.error(f"robots.txt okuma hatası: {e}")
        
    def scrape(self, category, limit=10):
        """Ürünleri çek"""
        products = []
        page = 1
        
        while len(products) < limit:
            try:
                # URL'yi oluştur ve logla
                url = f"{self.base_url}/sr?q={category}&pi={page}"
                logger.info(f"Sayfa {page} deneniyor: {url}")
                
                # Request yap
                response = self.session.get(url, headers=self.headers, timeout=10)
                logger.info(f"Status Code: {response.status_code}")
                
                if response.status_code != 200:
                    logger.error(f"Sayfa yüklenemedi: {url}")
                    break
                
                # HTML'i parse et
                soup = BeautifulSoup(response.content, 'html.parser')
                items = soup.select('div[data-id]')
                logger.info(f"Bulunan ürün sayısı: {len(items)}")
                
                if not items:
                    logger.warning("Ürün bulunamadı, selector'ları kontrol et")
                    # HTML'i kaydet
                    with open(f"debug_page_{page}.html", "w", encoding="utf-8") as f:
                        f.write(str(soup))
                    break
                
                for item in items:
                    try:
                        # Farklı selector'ları dene
                        name = item.select_one('span.prdct-desc-cntnr-name, div.product-down h3.p-card-title')
                        price = item.select_one('div.prc-box-dscntd, div.product-price')
                        
                        if name and price:
                            product = {
                                'name': name.text.strip(),
                                'price': price.text.strip(),
                                'timestamp': datetime.now().isoformat()
                            }
                            products.append(product)
                            print(f"Ürün eklendi: {product['name'][:50]}... - {product['price']}")
                            logger.info(f"Ürün eklendi: {product['name'][:30]}")
                        
                    except Exception as e:
                        logger.warning(f"Ürün verisi çekilemedi: {e}")
                
                # Sayfa arası bekle
                wait_time = random.uniform(2, 5)
                logger.info(f"Bekleniyor: {wait_time:.2f} saniye")
                time.sleep(wait_time)
                page += 1
                
            except Exception as e:
                logger.error(f"Beklenmeyen hata: {e}")
                break
        
        return products[:limit]
    
    def parse(self, content):
        """Sayfa içeriğini ayrıştır"""
        products = []
        soup = BeautifulSoup(content, 'html.parser')
        
        for item in soup.select('div[data-id]'):
            try:
                product = {
                    'name': self._get_text(item, 'span.prdct-desc-cntnr-name, div.product-down h3.p-card-title'),
                    'price': self._get_text(item, 'div.prc-box-dscntd, div.product-price'),
                    'brand': self._get_text(item, 'span.prdct-desc-cntnr-ttl, div.brand'),
                    'rating': self._get_text(item, 'div.ratings, div.product-rating'),
                    'timestamp': datetime.now().isoformat()
                }
                
                if product['name'] and product['price']:
                    products.append(product)
                    print(f"Ürün eklendi: {product['name'][:50]}... - {product['price']}")
                    
            except Exception as e:
                logging.warning(f"Ürün ayrıştırma hatası: {e}")
                
        return products
    
    def _get_text(self, item, selector):
        """Seçiciden metin al"""
        element = item.select_one(selector)
        return element.text.strip() if element else None

    def save_data(self, products, category):
        """Verileri CSV olarak kaydet"""
        try:
            df = pd.DataFrame(products)
            filename = f"data/raw/trendyol_{category}_{datetime.now().strftime('%Y%m%d')}.csv"
            df.to_csv(filename, index=False)
            logger.info(f"{len(products)} ürün kaydedildi: {filename}")
            
        except Exception as e:
            logger.error(f"Veri kaydedilemedi: {e}")

def main():
    try:
        scraper = TrendyolScraper()
        print("Scraping başlatılıyor... (10 ürün için) Durdurmak için Ctrl+C")
        
        # Sadece kategori adını gönder
        products = scraper.scrape("laptop", limit=10)  # URL yerine sadece "laptop"
        
        if products:
            scraper.save_data(products, "laptop")
            
    except KeyboardInterrupt:
        print("\nKullanıcı tarafından durduruldu")
    except Exception as e:
        logger.error(f"Program hatası: {e}")

if __name__ == "__main__":
    main() 