def test_imports():
    try:
        from src.data_collection.collectors import RedditDataCollector
        from src.data_collection.collectors import NewsCollector
        from src.data_collection.collectors import MarketDataCollector
        from src.data_collection.scrapers import TrendyolScraper
        
        print("✓ All imports successful!")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

if __name__ == "__main__":
    test_imports() 