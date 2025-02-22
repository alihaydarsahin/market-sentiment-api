import schedule
import time
import logging
from datetime import datetime
import os
import pandas as pd

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BatchDataCollector:
    def __init__(self):
        # Create data directories
        os.makedirs("data/raw/market", exist_ok=True)
        os.makedirs("data/raw/reddit", exist_ok=True)
        os.makedirs("data/raw/github", exist_ok=True)
        
        # Initialize collectors
        self.market_collector = MarketDataCollector()
        self.reddit_collector = RedditDataCollector()
        self.github_collector = GitHubTrendCollector()
        
    def collect_market_data(self):
        """Hourly market data collection"""
        try:
            # Stock data
            stock_data = self.market_collector.collect_stock_data(days=1)
            
            # Crypto data
            crypto_data = self.market_collector.collect_crypto_data()
            
            # Save data
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            pd.DataFrame(stock_data).to_csv(f"data/raw/market/stocks_{timestamp}.csv")
            pd.DataFrame(crypto_data).to_csv(f"data/raw/market/crypto_{timestamp}.csv")
            
            logger.info("Market data collected successfully")
            
        except Exception as e:
            logger.error(f"Market data collection error: {e}")
    
    def collect_reddit_data(self):
        """6-hour Reddit data collection"""
        try:
            discussions = self.reddit_collector.collect_tech_discussions()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            
            pd.DataFrame(discussions).to_csv(
                f"data/raw/reddit/discussions_{timestamp}.csv"
            )
            logger.info("Reddit data collected successfully")
            
        except Exception as e:
            logger.error(f"Reddit data collection error: {e}")
    
    def collect_github_data(self):
        """Daily GitHub trends collection"""
        try:
            trends = self.github_collector.collect_tech_trends()
            timestamp = datetime.now().strftime('%Y%m%d')
            
            pd.DataFrame(trends).to_csv(
                f"data/raw/github/trends_{timestamp}.csv"
            )
            logger.info("GitHub trends collected successfully")
            
        except Exception as e:
            logger.error(f"GitHub data collection error: {e}")
    
    def schedule_jobs(self):
        """Schedule all data collection jobs"""
        # Market data - every hour
        schedule.every(1).hours.do(self.collect_market_data)
        
        # Reddit data - every 6 hours
        schedule.every(6).hours.do(self.collect_reddit_data)
        
        # GitHub data - once per day at midnight
        schedule.every().day.at("00:00").do(self.collect_github_data)
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("Data collection stopped by user")
                break
            except Exception as e:
                logger.error(f"Scheduling error: {e}")
                time.sleep(300)  # Wait 5 minutes on error

def main():
    collector = BatchDataCollector()
    
    # Initial collection
    collector.collect_market_data()
    collector.collect_reddit_data()
    collector.collect_github_data()
    
    # Start scheduled collection
    collector.schedule_jobs()

if __name__ == "__main__":
    main() 