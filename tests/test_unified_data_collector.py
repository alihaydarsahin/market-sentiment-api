import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.data_collection.collectors import DataCollector

class TestUnifiedDataCollector(unittest.TestCase):
    def setUp(self):
        self.collector = DataCollector()

    @patch('src.data_collection.collectors.praw.Reddit')
    def test_collect_reddit_data(self, mock_reddit):
        mock_reddit_instance = mock_reddit.return_value
        mock_reddit_instance.subreddit.return_value.hot.return_value = [
            MagicMock(title='Test Post', score=100, num_comments=10, created_utc=1609459200, url='http://test.com')
        ]
        discussions = self.collector.collect_reddit_data(limit=1)
        self.assertEqual(len(discussions), 1)
        self.assertEqual(discussions[0]['title'], 'Test Post')

    @patch('src.data_collection.collectors.yf.Ticker')
    def test_collect_market_data(self, mock_ticker):
        mock_ticker_instance = mock_ticker.return_value
        mock_ticker_instance.history.return_value.iterrows.return_value = iter([
            (datetime(2021, 1, 1), MagicMock(Open=100, Close=110, Volume=1000))
        ])
        data = self.collector.collect_market_data(days=1)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['open'], 100)

    @patch('src.data_collection.collectors.requests.get')
    def test_collect_news_data(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {'articles': [{'title': 'Test News'}]}
        mock_get.return_value = mock_response
        articles = self.collector.collect_news_data()
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]['title'], 'Test News')

if __name__ == '__main__':
    unittest.main() 