import os
import logging
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

# Import our collectors
from .reddit_collector import RedditDataCollector
from .market_collector import MarketDataCollector
from .github_collector import GitHubTrendCollector
from .news_collector import NewsCollector

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class DataCollectorManager:
    def __init__(self):
        # Create data directories
        self.data_dirs = {
            'market': 'data/raw/market',
            'reddit': 'data/raw/reddit',
            'github': 'data/raw/github',
            'news': 'data/raw/news'
        }
        self._create_directories()
        
        # Initialize collectors with API keys
        self.collectors = {
            'reddit': RedditDataCollector(),
            'github': GitHubTrendCollector(),
            'market': MarketDataCollector(),
            'news': NewsCollector()
        }
    
    def _create_directories(self):
        """Create necessary data directories"""
        for dir_path in self.data_dirs.values():
            os.makedirs(dir_path, exist_ok=True)
    
    def collect_all_data(self):
        """Collect data from all sources"""
        collection_results = {}
        
        for source, collector in self.collectors.items():
            try:
                logger.info(f"Collecting {source} data...")
                data = collector.collect_data()
                self._save_data(data, source)
                collection_results[source] = len(data) if data else 0
                
            except Exception as e:
                logger.error(f"Error collecting {source} data: {e}")
                collection_results[source] = 0
        
        return collection_results
    
    def _save_data(self, data, source):
        """Save collected data"""
        if not data:
            logger.warning(f"No data to save for {source}")
            return
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        filename = f"{self.data_dirs[source.split('_')[0]]}/{source}_{timestamp}.csv"
        
        try:
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False)
            logger.info(f"Saved {len(df)} records to {filename}")
        except Exception as e:
            logger.error(f"Error saving {source} data: {e}")

def main():
    collector = DataCollectorManager()
    results = collector.collect_all_data()
    
    logger.info("\nCollection Summary:")
    for source, count in results.items():
        logger.info(f"{source}: {count} items collected")

if __name__ == "__main__":
    main() 