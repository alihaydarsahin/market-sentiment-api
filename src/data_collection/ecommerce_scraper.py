import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import time
import random
import logging

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/ecommerce_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EcommerceScraper:
    def __init__(self, max_retries=3, retry_delay=5):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "tr,en-US;q=0.7,en;q=0.3",
        }
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.allowed_fields = {
            "name", "price", "brand", "platform", "link", "timestamp",
            "category", "rating", "review_count"
        }
        
        # Log ve data klasörlerini oluştur
        os.makedirs("data/logs", exist_ok=True)
        os.makedirs("data/raw", exist_ok=True)

    def _get_soup(self, url, retries=0):
        try:
            logger.info(f"URL'ye erişiliyor: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Sayfa çekme hatası: {e}")
            if retries < self.max_retries:
                wait_time = self.retry_delay * (retries + 1)
                logger.info(f"{wait_time} saniye sonra tekrar denenecek...")
                time.sleep(wait_time)
                return self._get_soup(url, retries + 1)
            return None

    def clean_product_data(self, product_data):
        """Ürün verisini temizle ve doğrula"""
        try:
            # Fiyatı sayısal formata çevir
            price = product_data.get("price", "").replace("TL", "").strip()
            try:
                price = float(price.replace(",", "."))
                product_data["price"] = price
            except ValueError:
                logger.warning(f"Geçersiz fiyat formatı: {price}")
                return None

            # Boş alanları kontrol et
            if not product_data.get("name") or not product_data.get("price"):
                return None

            # İzin verilen alanları filtrele
            return {k: v for k, v in product_data.items() if k in self.allowed_fields}
        except Exception as e:
            logger.error(f"Veri temizleme hatası: {e}")
            return None

    def scrape_trendyol(self, search_term, max_pages=3):
        products = []
        base_url = "https://www.trendyol.com/sr?q={}&pi={}"
        
        for page in range(1, max_pages + 1):
            url = base_url.format(search_term, page)
            soup = self._get_soup(url)
            if not soup:
                continue
                
            product_cards = soup.find_all("div", class_="p-card-wrppr")
            logger.info(f"Sayfa {page}: {len(product_cards)} ürün bulundu")
            
            for card in product_cards:
                try:
                    product_data = {
                        "platform": "Trendyol",
                        "name": card.find("span", class_="prdct-desc-cntnr-name").text.strip(),
                        "price": card.find("div", class_="prc-box-dscntd").text.strip(),
                        "brand": card.find("span", class_="prdct-desc-cntnr-ttl").text.strip(),
                        "category": search_term,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    link = card.find("a")["href"]
                    if link:
                        product_data["link"] = "https://www.trendyol.com" + link
                    
                    cleaned_data = self.clean_product_data(product_data)
                    if cleaned_data:
                        products.append(cleaned_data)
                        
                except AttributeError as e:
                    logger.error(f"Ürün ayrıştırma hatası: {e}")
                    continue
                    
            time.sleep(random.uniform(1, 3))
            
        return products

    def scrape_hepsiburada(self, search_term, max_pages=3):
        products = []
        base_url = "https://www.hepsiburada.com/ara?q={}&sayfa={}"
        
        for page in range(1, max_pages + 1):
            url = base_url.format(search_term, page)
            soup = self._get_soup(url)
            if not soup:
                continue
                
            product_cards = soup.find_all("li", class_="productListContent-zAP0Y5msy8OHn5z7T_K_")
            
            for card in product_cards:
                try:
                    # Sadece ürün bilgilerini topluyoruz
                    product_data = {
                        "platform": "Hepsiburada",
                        "name": card.find("h3", class_="product-title").text.strip(),
                        "price": card.find("div", class_="price-value").text.strip(),
                        "brand": card.find("h3", class_="product-title").text.split()[0],
                        "category": search_term,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Link bilgisini güvenli şekilde ekleme
                    link = card.find("a")["href"]
                    if link:
                        if not link.startswith("http"):
                            link = "https://www.hepsiburada.com" + link
                        product_data["link"] = link
                    
                    # Sadece izin verilen alanları kaydet
                    safe_product = {k: v for k, v in product_data.items() 
                                  if k in self.allowed_fields}
                    products.append(safe_product)
                    
                except AttributeError as e:
                    print(f"Ürün ayrıştırma hatası: {e}")
                    continue
                    
            time.sleep(random.uniform(1, 3))
            
        return products

    def save_products(self, products, platform):
        if not products:
            logger.warning("Kaydedilecek ürün bulunamadı!")
            return
            
        try:
            safe_platform = "".join(c for c in platform.lower() if c.isalnum())
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"data/raw/{safe_platform}_products_{timestamp}.csv"
            
            df = pd.DataFrame(products)
            allowed_columns = [col for col in df.columns if col in self.allowed_fields]
            df = df[allowed_columns]
            
            df.to_csv(filename, index=False)
            logger.info(f"{len(products)} ürün {filename} dosyasına kaydedildi")
            
        except Exception as e:
            logger.error(f"Dosya kaydetme hatası: {e}")

class TrendyolScraper:
    def __init__(self):
        self.base_url = "https://www.trendyol.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124"
        }
        self.logger = logging.getLogger(__name__)

    def get_products(self, search_term, limit=100):
        """Get products from Trendyol"""
        try:
            products = []
            page = 1
            
            while len(products) < limit:
                url = f"{self.base_url}/sr?q={search_term}&pi={page}"
                
                try:
                    response = requests.get(url, headers=self.headers, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    items = soup.select('div.p-card-wrppr')
                    
                    if not items:
                        self.logger.warning(f"No items found on page {page}")
                        break
                    
                    for item in items:
                        if len(products) >= limit:
                            break
                        
                        try:
                            name_elem = item.select_one('.prdct-desc-cntnr-name')
                            price_elem = item.select_one('.prc-box-dscntd')
                            brand_elem = item.select_one('.prdct-desc-cntnr-ttl')
                            link_elem = item.select_one('a')
                            
                            if all([name_elem, price_elem, brand_elem, link_elem]):
                                product = {
                                    'name': name_elem.text.strip(),
                                    'price': price_elem.text.strip(),
                                    'brand': brand_elem.text.strip(),
                                    'link': self.base_url + link_elem['href'],
                                    'date': datetime.now().isoformat()  # Changed from timestamp to date
                                }
                                products.append(product)
                                self.logger.debug(f"Added product: {product['name'][:30]}...")
                        
                        except Exception as e:
                            self.logger.error(f"Error parsing product: {e}")
                            continue
                    
                    page += 1
                    time.sleep(random.uniform(2, 4))  # Increased delay
                    
                except requests.RequestException as e:
                    self.logger.error(f"Request error on page {page}: {e}")
                    break
            
            self.logger.info(f"Collected {len(products)} products")
            return products
            
        except Exception as e:
            self.logger.error(f"Error collecting products: {e}")
            return []

if __name__ == "__main__":
    try:
        scraper = EcommerceScraper()
        search_terms = ["laptop", "telefon", "tablet"]
        
        for term in search_terms:
            logger.info(f"\n{term.upper()} için ürünler toplanıyor...")
            
            trendyol_products = scraper.scrape_trendyol(term)
            scraper.save_products(trendyol_products, "Trendyol")
            
            # Hepsiburada için de eklenecek
            # hepsiburada_products = scraper.scrape_hepsiburada(term)
            # scraper.save_products(hepsiburada_products, "Hepsiburada")
            
            logger.info(f"{term} için veri toplama tamamlandı!")
            
    except Exception as e:
        logger.error(f"Program çalışırken hata oluştu: {e}") 