import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
import logging

# Create required directories at startup
os.makedirs("data/logs", exist_ok=True)
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/figures", exist_ok=True)

# Logging settings
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TrendAnalyzer:
    def __init__(self):
        self.figure_size = (15, 6)
        
    def load_data(self):
        """Load data"""
        try:
            # Find latest created files
            raw_files = os.listdir("data/raw")
            news_files = [f for f in raw_files if f.startswith("news_data_")]
            scraped_files = [f for f in raw_files if f.startswith("scraped_news_")]
            trendyol_files = [f for f in raw_files if f.startswith("trendyol_products_")]
            
            # Select latest files
            latest_news = sorted(news_files)[-1] if news_files else None
            latest_scraped = sorted(scraped_files)[-1] if scraped_files else None
            latest_trendyol = sorted(trendyol_files)[-1] if trendyol_files else None
            
            # Load data
            data = {}
            if latest_news:
                data['news_api'] = pd.read_csv(f"data/raw/{latest_news}")
                logger.info(f"API news loaded: {len(data['news_api'])} items")
                
            if latest_scraped:
                data['scraped_news'] = pd.read_csv(f"data/raw/{latest_scraped}")
                logger.info(f"Scraped news loaded: {len(data['scraped_news'])} items")
                
            if latest_trendyol:
                data['trendyol'] = pd.read_csv(f"data/raw/{latest_trendyol}")
                logger.info(f"Trendyol products loaded: {len(data['trendyol'])} items")
                
            return data
            
        except Exception as e:
            logger.error(f"Data loading error: {e}")
            return None
            
    def analyze_news_trends(self, news_data):
        """Analyze news trends"""
        try:
            # Date conversion
            news_data['publishedAt'] = pd.to_datetime(news_data['publishedAt'])
            
            # Daily news count
            daily_news = news_data['publishedAt'].dt.date.value_counts().sort_index()
            
            # Trend graph
            plt.figure(figsize=self.figure_size)
            daily_news.plot(kind='line', marker='o')
            plt.title('Daily News Count Trend')
            plt.xlabel('Date')
            plt.ylabel('News Count')
            plt.grid(True)
            plt.xticks(rotation=45)
            
            # Save graph
            plt.savefig('data/figures/news_trend.png')
            plt.close()
            
            logger.info("News trend analysis completed")
            return daily_news
            
        except Exception as e:
            logger.error(f"News trend analysis error: {e}")
            return None
            
    def analyze_ecommerce(self, product_data):
        """Analyze e-commerce data"""
        try:
            # Category-based price analysis
            plt.figure(figsize=self.figure_size)
            categories = product_data['category'].unique()
            
            # Use simple bar plot instead of box plot
            stats = product_data.groupby('category')['price'].agg(['mean', 'std']).round(2)
            stats['mean'].plot(kind='bar')
            plt.title('Average Prices by Category')
            plt.xlabel('Category')
            plt.ylabel('Average Price (TL)')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Save graph
            plt.savefig('data/figures/price_analysis.png')
            plt.close()
            
            # Brand analysis
            plt.figure(figsize=self.figure_size)
            product_data['brand'].value_counts().head(10).plot(kind='bar')
            plt.title('Top 10 Popular Brands')
            plt.xlabel('Brand')
            plt.ylabel('Product Count')
            plt.grid(True)
            plt.tight_layout()
            
            # Save graph
            plt.savefig('data/figures/brand_analysis.png')
            plt.close()
            
            return stats
            
        except Exception as e:
            logger.error(f"E-commerce analysis error: {e}")
            return None

def main():
    try:
        analyzer = TrendAnalyzer()
        
        # Load data
        data = analyzer.load_data()
        if not data:
            logger.error("Data could not be loaded!")
            return
            
        # News analysis
        if 'news_api' in data:
            news_trends = analyzer.analyze_news_trends(data['news_api'])
            print("\nNews Trend:")
            print(news_trends)
            
        # E-commerce analysis
        if 'trendyol' in data:
            ecommerce_stats = analyzer.analyze_ecommerce(data['trendyol'])
            print("\nE-commerce Statistics:")
            print(ecommerce_stats)
            
        logger.info("Analysis completed! Graphs saved to data/figures directory.")
        
    except Exception as e:
        logger.error(f"Program error: {e}")

if __name__ == "__main__":
    main() 