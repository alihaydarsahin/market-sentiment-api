import unittest
from unittest.mock import patch, MagicMock
from src.data_collection.scrapers import EcommerceScraper

class TestUnifiedScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = EcommerceScraper()

    @patch('src.data_collection.scrapers.requests.get')
    def test_scrape_news(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = '<html><body><article><h2>Test News</h2><a href="http://test.com">Link</a></article></body></html>'
        mock_get.return_value = mock_response
        articles = self.scraper.scrape_news('http://test.com')
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]['title'], 'Test News')

    @patch('src.data_collection.scrapers.requests.get')
    def test_scrape_trendyol(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = '<html><body><div class="product-item"><h3>Test Product</h3><span class="price">100</span></div></body></html>'
        mock_get.return_value = mock_response
        products = self.scraper.scrape_trendyol('http://test.com')
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]['name'], 'Test Product')

    @patch('src.data_collection.scrapers.requests.get')
    def test_scrape_ecommerce(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = '<html><body><div class="product"><h2>Test Product</h2><span class="price">100</span></div></body></html>'
        mock_get.return_value = mock_response
        products = self.scraper.scrape_trendyol('http://test.com')
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]['name'], 'Test Product')

if __name__ == '__main__':
    unittest.main() 