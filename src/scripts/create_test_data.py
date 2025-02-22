import os
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

def create_test_data():
    """Create test data for market sentiment analysis"""
    # Create required directories
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    
    # Generate date range for test data
    dates = pd.date_range(start='2025-01-01', end='2025-02-20', freq='D')
    
    # Create realistic test data with market indicators
    data = pd.DataFrame({
        'date': dates,
        'reddit_sentiment': np.clip(np.random.normal(0.2, 0.3, len(dates)), -1, 1),
        'news_sentiment': np.clip(np.random.normal(0.1, 0.2, len(dates)), -1, 1),
        'market_change': np.random.normal(0.05, 0.1, len(dates)),
        'volume': np.random.randint(1000, 10000, len(dates)),
        'interaction_score': np.random.randint(50, 500, len(dates))
    })
    
    # Save data with timestamp
    filename = f'combined_data_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
    data.to_csv(f'data/processed/{filename}', index=False)
    print(f"Test data created successfully: {filename}")
    
    return data

if __name__ == '__main__':
    create_test_data()     