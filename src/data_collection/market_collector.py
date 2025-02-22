import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging

class MarketDataCollector:
    def __init__(self):
        self.tech_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
        self.logger = logging.getLogger(__name__)
        
    def collect_stock_data(self, days=30):
        """Collect stock market data"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            data = []
            for symbol in self.tech_symbols:
                stock = yf.Ticker(symbol)
                hist = stock.history(start=start_date, end=end_date)
                
                for date, row in hist.iterrows():
                    data.append({
                        'symbol': symbol,
                        'date': date.date().isoformat(),
                        'open': row['Open'],
                        'close': row['Close'],
                        'volume': row['Volume'],
                        'change_pct': ((row['Close'] - row['Open']) / row['Open']) * 100
                    })
            
            self.logger.info(f"Collected {len(data)} stock data points")
            return data
            
        except Exception as e:
            self.logger.error(f"Error collecting stock data: {e}")
            return []

    def collect_crypto_data(self):
        """Collect crypto prices from multiple sources"""
        # CoinGecko API - No key needed, generous limits
        return self.get_crypto_prices(['bitcoin', 'ethereum'])
        
    def collect_github_trends(self):
        """Get technology trends from GitHub"""
        # GitHub API - 5000 requests/hour without auth
        return self.get_github_trending_repos() 