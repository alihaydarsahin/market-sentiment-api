def test_imports():
    try:
        from src.data_collection.reddit_collector import RedditDataCollector
        from src.data_collection.news_collector import NewsCollector
        from src.data_collection.market_collector import MarketDataCollector
        from src.data_collection.ecommerce_scraper import TrendyolScraper
        
        print("✓ All imports successful!")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

if __name__ == "__main__":
    test_imports() 