from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import random
import logging
import os
from datetime import datetime

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/trendyol_selenium_tor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TrendyolSeleniumScraper:
    def __init__(self):
        self.base_url = "https://www.trendyol.com"
        self.setup_driver()
        
    def setup_driver(self):
        """Tor Browser'ı Selenium ile kullan"""
        try:
            # Tor Browser profil ve binary yolları
            tor_profile = r"C:\Users\CASPER\Desktop\Tor Browser\Browser\TorBrowser\Data\Browser\profile.default"
            tor_binary = r"C:\Users\CASPER\Desktop\Tor Browser\Browser\firefox.exe"
            
            options = Options()
            options.binary_location = tor_binary
            
            # Tor proxy ayarları
            options.set_preference('network.proxy.type', 1)
            options.set_preference('network.proxy.socks', '127.0.0.1')
            options.set_preference('network.proxy.socks_port', 9150)
            options.set_preference('network.proxy.socks_remote_dns', True)
            
            # Tor profili kullan
            options.set_preference('profile', tor_profile)
            
            # Gizlilik ayarları
            options.set_preference('privacy.resistFingerprinting', True)
            options.set_preference('webgl.disabled', True)
            options.set_preference('media.peerconnection.enabled', False)
            options.set_preference('dom.webdriver.enabled', False)
            options.set_preference('useAutomationExtension', False)
            
            service = Service(executable_path='geckodriver.exe')
            self.driver = webdriver.Firefox(service=service, options=options)
            
            # IP kontrolü yap
            self.check_ip()
            
            self.wait = WebDriverWait(self.driver, 10)
            logger.info("Tor Browser başarıyla başlatıldı")
            
        except Exception as e:
            logger.error(f"Driver başlatma hatası: {e}")
            raise
    
    def check_ip(self):
        """IP adresini kontrol et"""
        try:
            self.driver.get("https://api.ipify.org")
            time.sleep(2)
            ip = self.driver.find_element(By.TAG_NAME, "pre").text
            logger.info(f"Şu anki IP: {ip}")
            
            # IP'nin Tor ağından gelip gelmediğini kontrol et
            self.driver.get("https://check.torproject.org")
            time.sleep(2)
            
            if "Congratulations" in self.driver.page_source:
                logger.info("Tor ağı başarıyla kullanılıyor!")
            else:
                logger.warning("DİKKAT: Tor ağı kullanılmıyor!")
            
        except Exception as e:
            logger.error(f"IP kontrol hatası: {e}")
    
    def get_new_ip(self):
        """Yeni Tor IP adresi al"""
        try:
            old_ip = self.check_ip()
            logger.info(f"Eski IP: {old_ip}")
            
            # Tor Browser'ı yeniden başlat
            self.driver.quit()
            time.sleep(2)
            self.setup_driver()
            
            new_ip = self.check_ip()
            logger.info(f"Yeni IP: {new_ip}")
            
        except Exception as e:
            logger.error(f"IP değiştirme hatası: {e}")
    
    def get_products(self, category, limit=10):
        """Ürünleri topla"""
        products = []
        page = 1
        
        try:
            # Önce ana sayfaya git
            self.driver.get(self.base_url)
            time.sleep(random.uniform(3, 5))
            
            # Arama yap
            search_url = f"{self.base_url}/sr?q={category}"
            self.driver.get(search_url)
            time.sleep(random.uniform(2, 4))
            
            # İnsan gibi scroll yap
            self.human_like_scroll()
            
            # Ürünleri topla
            cards = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.p-card-wrppr"))
            )
            
            for card in cards:
                try:
                    # Scroll to element
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", card)
                    time.sleep(0.5)
                    
                    product = {
                        'name': card.find_element(By.CSS_SELECTOR, "span.prdct-desc-cntnr-name").text,
                        'price': card.find_element(By.CSS_SELECTOR, "div.prc-box-dscntd").text,
                        'brand': card.find_element(By.CSS_SELECTOR, "span.prdct-desc-cntnr-ttl").text,
                        'category': category,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Link
                    link = card.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                    if link:
                        product['link'] = link
                    
                    products.append(product)
                    logger.info(f"Ürün eklendi: {product['name'][:50]}...")
                    
                    if len(products) >= limit:
                        break
                        
                except Exception as e:
                    logger.warning(f"Ürün verisi çekilemedi: {e}")
                    continue
            
            page += 1
            time.sleep(random.uniform(3, 5))
            
        except Exception as e:
            logger.error(f"Veri çekme hatası: {e}")
            
        return products[:limit]
    
    def save_products(self, products, category):
        """Ürünleri kaydet"""
        try:
            if not products:
                logger.warning("Kaydedilecek ürün yok!")
                return
                
            df = pd.DataFrame(products)
            filename = f"data/raw/trendyol_{category}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
            df.to_csv(filename, index=False)
            logger.info(f"{len(products)} ürün kaydedildi: {filename}")
            
        except Exception as e:
            logger.error(f"Kaydetme hatası: {e}")
    
    def close(self):
        """Driver'ı kapat"""
        try:
            self.driver.quit()
            logger.info("Driver kapatıldı")
        except:
            pass

    def human_like_scroll(self):
        """İnsan gibi scroll hareketi"""
        total_height = self.driver.execute_script("return document.body.scrollHeight")
        viewport_height = self.driver.execute_script("return window.innerHeight")
        current_position = 0
        
        while current_position < total_height:
            scroll_amount = random.randint(100, 300)
            current_position += scroll_amount
            self.driver.execute_script(f"window.scrollTo(0, {current_position});")
            time.sleep(random.uniform(0.5, 1.5))

def main():
    try:
        print("Tor Browser'ı açtığınızdan emin olun...")
        time.sleep(2)
        
        scraper = TrendyolSeleniumScraper()
        print("Scraping başlatılıyor... Durdurmak için Ctrl+C")
        
        # Test kategorisi
        category = "laptop"
        products = scraper.get_products(category, limit=10)
        
        if products:
            scraper.save_products(products, category)
            
    except KeyboardInterrupt:
        print("\nKullanıcı tarafından durduruldu")
    except Exception as e:
        logger.error(f"Program hatası: {e}")
    finally:
        if 'scraper' in locals():
            scraper.close()

if __name__ == "__main__":
    main() 