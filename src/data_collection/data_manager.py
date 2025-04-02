import schedule
import time
import logging
from datetime import datetime
import os
import pandas as pd
from typing import Dict, Any, List, Optional
import json
from dotenv import load_dotenv

# Import our collector
from collectors import DataCollector

# Load environment variables
load_dotenv()

class DataManager:
    """
    Unified data manager that handles both scheduled batch collection
    and manual collection of data from various sources.
    """
    def __init__(self):
        # Setup logging
        self.setup_logging()
        
        # Create data directories
        self.data_dirs = {
            'market': 'data/raw/market',
            'reddit': 'data/raw/reddit',
            'news': 'data/raw/news',
            'social': 'data/raw/social',
            'economic': 'data/raw/economic'
        }
        self.create_directories(list(self.data_dirs.values()))
        
        # Initialize collector
        self.collector = DataCollector()
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = 'data/logs'
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'data_manager.log')
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def create_directories(self, directories: List[str]):
        """Create necessary directories if they don't exist"""
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
                self.logger.info(f"Directory created/verified: {directory}")
            except Exception as e:
                self.logger.error(f"Error creating directory {directory}: {e}")
    
    def collect_all_data(self) -> Dict[str, int]:
        """Collect data from all sources"""
        collection_results = {}
        
        # Collect all data types
        all_data = self.collector.collect_all_data()
        
        # Save each data type
        for source, data in all_data.items():
            try:
                if isinstance(data, dict) and not any(isinstance(v, list) for v in data.values()):
                    # For economic data or other dict types
                    self._save_data_json(data, source)
                    collection_results[source] = len(data)
                elif isinstance(data, list):
                    # For regular list of dicts data
                    self._save_data_csv(data, source)
                    collection_results[source] = len(data)
                else:
                    self.logger.warning(f"Unsupported data format for {source}")
                    collection_results[source] = 0
            except Exception as e:
                self.logger.error(f"Error saving {source} data: {e}")
                collection_results[source] = 0
        
        return collection_results
    
    def _save_data_csv(self, data: List[Dict[str, Any]], source: str):
        """Save collected data to CSV"""
        if not data:
            self.logger.warning(f"No data to save for {source}")
            return
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        filename = f"{self.data_dirs[source]}/{source}_{timestamp}.csv"
        
        try:
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False)
            self.logger.info(f"Saved {len(df)} records to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving {source} data to CSV: {e}")
    
    def _save_data_json(self, data: Dict[str, Any], source: str):
        """Save collected data to JSON"""
        if not data:
            self.logger.warning(f"No data to save for {source}")
            return
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        filename = f"{self.data_dirs[source]}/{source}_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            self.logger.info(f"Saved {len(data)} items to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving {source} data to JSON: {e}")
    
    def collect_market_data(self):
        """Collect and save market data"""
        try:
            data = self.collector.collect_market_data()
            self._save_data_csv(data, 'market')
            self.logger.info("Market data collected successfully")
        except Exception as e:
            self.logger.error(f"Market data collection error: {e}")
    
    def collect_reddit_data(self):
        """Collect and save Reddit data"""
        try:
            data = self.collector.collect_reddit_data()
            self._save_data_csv(data, 'reddit')
            self.logger.info("Reddit data collected successfully")
        except Exception as e:
            self.logger.error(f"Reddit data collection error: {e}")
    
    def collect_news_data(self):
        """Collect and save news data"""
        try:
            data = self.collector.collect_news_data()
            self._save_data_csv(data, 'news')
            self.logger.info("News data collected successfully")
        except Exception as e:
            self.logger.error(f"News data collection error: {e}")
    
    def collect_social_data(self):
        """Collect and save social media data"""
        try:
            data = self.collector.collect_social_trends()
            self._save_data_csv(data, 'social')
            self.logger.info("Social media data collected successfully")
        except Exception as e:
            self.logger.error(f"Social media data collection error: {e}")
    
    def collect_economic_data(self):
        """Collect and save economic data"""
        try:
            data = self.collector.collect_economic_data()
            self._save_data_json(data, 'economic')
            self.logger.info("Economic data collected successfully")
        except Exception as e:
            self.logger.error(f"Economic data collection error: {e}")
    
    def schedule_jobs(self):
        """Schedule all data collection jobs"""
        # Market data - every hour
        schedule.every(1).hours.do(self.collect_market_data)
        
        # Reddit data - every 6 hours
        schedule.every(6).hours.do(self.collect_reddit_data)
        
        # News data - every 4 hours
        schedule.every(4).hours.do(self.collect_news_data)
        
        # Social media data - every 12 hours
        schedule.every(12).hours.do(self.collect_social_data)
        
        # Economic data - once per day at midnight
        schedule.every().day.at("00:00").do(self.collect_economic_data)
        
        self.logger.info("Scheduled jobs set up. Starting scheduler...")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                self.logger.info("Data collection stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Scheduling error: {e}")
                time.sleep(300)  # Wait 5 minutes on error

def main():
    manager = DataManager()
    
    # Run immediate collection of all data
    results = manager.collect_all_data()
    
    print("\nCollection Summary:")
    for source, count in results.items():
        print(f"{source}: {count} items collected")
    
    # Ask if the user wants to run scheduled collection
    response = input("\nDo you want to start scheduled collection? (y/n): ")
    if response.lower() == 'y':
        manager.schedule_jobs()
    else:
        print("Scheduled collection not started. Exiting.")

if __name__ == "__main__":
    main() 