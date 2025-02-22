import requests
import logging
import time
import random
from abc import ABC, abstractmethod
from datetime import datetime
import pandas as pd

class BaseScraper(ABC):
    def __init__(self):
        self.session = requests.Session()
        self.base_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15'
        ]
        
    def _get_random_user_agent(self):
        """Rastgele user agent seç"""
        return random.choice(self.user_agents)
    
    def _prepare_headers(self, url):
        """Request header'larını hazırla"""
        headers = self.base_headers.copy()
        headers.update({
            'User-Agent': self._get_random_user_agent(),
            'Referer': url,
            'Host': url.split('/')[2]
        })
        return headers
    
    def make_request(self, url, method='GET', **kwargs):
        """Güvenli request yap"""
        try:
            headers = self._prepare_headers(url)
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                timeout=30,
                **kwargs
            )
            return response
            
        except Exception as e:
            logging.error(f"Request hatası: {e}")
            time.sleep(random.uniform(5, 10))
            return None
    
    @abstractmethod
    def scrape(self):
        """Ana scraping metodu - override edilmeli"""
        pass
    
    @abstractmethod
    def parse(self, content):
        """İçerik ayrıştırma metodu - override edilmeli"""
        pass
    
    def save_data(self, data, filename):
        """Verileri kaydet"""
        try:
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False)
            logging.info(f"{len(data)} kayıt kaydedildi: {filename}")
        except Exception as e:
            logging.error(f"Kaydetme hatası: {e}") 