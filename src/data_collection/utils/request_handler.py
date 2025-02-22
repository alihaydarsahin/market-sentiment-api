import time
import random
import logging
from urllib.parse import urljoin

class RequestHandler:
    def __init__(self):
        self.delay = (3, 7)  # Request arası bekleme süresi
        self.retry_count = 3  # Hata durumunda tekrar deneme sayısı
        
    def wait(self):
        """İki request arası bekle"""
        time.sleep(random.uniform(*self.delay))
    
    def handle_response(self, response):
        """Response durumunu kontrol et"""
        if response and response.status_code == 200:
            return True
        return False
    
    def build_url(self, base_url, path, params=None):
        """URL oluştur"""
        url = urljoin(base_url, path)
        if params:
            param_list = []
            for key, value in params.items():
                param_list.append(f"{key}={value}")
            url = f"{url}{'&' if '?' in url else '?'}{'&'.join(param_list)}"
        return url 