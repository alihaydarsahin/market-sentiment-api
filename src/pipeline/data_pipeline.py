import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import logging
from textblob import TextBlob

# Use absolute imports instead of relative imports
from src.data_collection.reddit_collector import RedditDataCollector
from src.data_collection.news_collector import NewsCollector
from src.data_collection.market_collector import MarketDataCollector
from src.data_collection.ecommerce_scraper import TrendyolScraper
from src.visualization.trend_visualizer import TrendVisualizer
from src.models.advanced_predictor import AdvancedPredictor

class DataPipeline:
    def __init__(self):
        self.collectors = {
            'reddit': RedditDataCollector(),
            'news': NewsCollector(),
            'market': MarketDataCollector(),
            'ecommerce': TrendyolScraper()
        }
        
        # Setup directories
        self.dirs = {
            'raw': 'data/raw',
            'processed': 'data/processed',
            'analysis': 'data/analysis'
        }
        self.logger = logging.getLogger(__name__)
        self._setup_directories()
        
        # Add to existing initialization
        self.visualizer = TrendVisualizer()
        self.predictor = AdvancedPredictor()
        
    def _setup_directories(self):
        """Create necessary directories"""
        for dir_path in self.dirs.values():
            os.makedirs(dir_path, exist_ok=True)
            self.logger.info(f"Created/verified directory: {dir_path}")
    
    def collect_data(self):
        """Collect data from all sources"""
        data = {}
        
        # Collect Reddit data
        data['reddit'] = self.collectors['reddit'].collect_tech_discussions()
        
        # Collect News data
        data['news'] = self.collectors['news'].collect_news()
        
        # Collect Market data
        data['market'] = self.collectors['market'].collect_stock_data()
        
        # Collect E-commerce data
        data['ecommerce'] = self.collectors['ecommerce'].get_products("laptop", limit=100)
        
        return data
    
    def process_data(self, data):
        """Process and combine all data"""
        processed = {}
        
        # Process Reddit data
        if 'reddit' in data and data['reddit']:
            reddit_df = pd.DataFrame(data['reddit'])
            reddit_df['date'] = pd.to_datetime(reddit_df['created_utc'])
            reddit_df['source'] = 'reddit'
            processed['reddit'] = reddit_df
        
        # Process News data
        if 'news' in data and data['news']:
            news_df = pd.DataFrame(data['news'])
            news_df['date'] = pd.to_datetime(news_df['publishedAt'])
            news_df['source'] = 'news'
            processed['news'] = news_df
        
        # Process Market data
        if 'market' in data and data['market']:
            market_df = pd.DataFrame(data['market'])
            market_df['date'] = pd.to_datetime(market_df['date'])
            processed['market'] = market_df
        
        # Process E-commerce data
        if 'ecommerce' in data and data['ecommerce']:
            ecommerce_df = pd.DataFrame(data['ecommerce'])
            ecommerce_df['date'] = pd.to_datetime(
                ecommerce_df.get('timestamp', ecommerce_df.get('date', datetime.now()))
            )
            processed['ecommerce'] = ecommerce_df
        
        return processed
    
    def analyze_sentiment(self, processed_data):
        """Analyze sentiment in text data"""
        for source in ['reddit', 'news']:
            if source in processed_data:
                df = processed_data[source]
                
                # Analyze sentiment for titles
                df['sentiment'] = df['title'].apply(
                    lambda x: TextBlob(str(x)).sentiment.polarity
                )
                
                # Calculate daily sentiment
                daily_sentiment = df.groupby('date')['sentiment'].mean()
                processed_data[f'{source}_sentiment'] = daily_sentiment
        
        return processed_data
    
    def combine_data(self, processed_data):
        """Combine all processed data for analysis"""
        try:
            # Get all dates from the data
            all_dates = []
            if 'reddit' in processed_data:
                all_dates.extend(processed_data['reddit']['date'].dt.date)
            if 'news' in processed_data:
                all_dates.extend(processed_data['news']['date'].dt.date)
            if 'market' in processed_data:
                all_dates.extend(processed_data['market']['date'].dt.date)
            
            # Create date range from min to max date
            if all_dates:
                start_date = min(all_dates)
                end_date = max(all_dates)
                dates = pd.date_range(start=start_date, end=end_date, freq='D')
                
                # Create combined DataFrame
                combined = pd.DataFrame(index=dates)
                
                # Add sentiment data
                if 'reddit_sentiment' in processed_data:
                    combined['reddit_sentiment'] = processed_data['reddit_sentiment']
                
                if 'news_sentiment' in processed_data:
                    combined['news_sentiment'] = processed_data['news_sentiment']
                
                # Add market data
                if 'market' in processed_data:
                    market_data = processed_data['market']
                    daily_changes = market_data.groupby('date')['change_pct'].mean()
                    combined['market_change'] = daily_changes
                
                # Fill missing values with forward and backward fill
                combined = combined.fillna(method='ffill').fillna(method='bfill')
                
                return combined
                
            else:
                self.logger.warning("No dates found in processed data")
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Error combining data: {e}")
            return pd.DataFrame()

    def run_pipeline(self):
        """Run the complete pipeline"""
        try:
            # 1. Collect data
            print("Collecting data...")
            raw_data = self.collect_data()
            
            # 2. Process data
            print("Processing data...")
            processed_data = self.process_data(raw_data)
            
            # 3. Analyze sentiment
            print("Analyzing sentiment...")
            processed_data = self.analyze_sentiment(processed_data)
            
            # 4. Combine data
            print("Combining data...")
            combined_data = self.combine_data(processed_data)
            
            # 5. Save results
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            combined_data.to_csv(f"{self.dirs['processed']}/combined_data_{timestamp}.csv")
            
            # Validate data quality before visualization
            print("\nValidating data quality...")
            validation = self.visualizer.validator.check_data_quality(combined_data)
            if not validation['is_valid']:
                print("Data quality issues found:")
                for issue in validation['issues']:
                    print(f"- {issue}")
            
            # Create visualizations with improved error handling
            print("\nCreating visualizations...")
            self.visualizer.create_sentiment_trends(combined_data)
            self.visualizer.create_market_analysis(combined_data)
            self.visualizer.create_correlation_matrix(combined_data)
            
            # Train models with improved features
            print("\nTraining prediction models...")
            model_scores = self.predictor.train_models(combined_data)
            
            if model_scores:
                print("\nModel Performance Summary:")
                for model, scores in model_scores.items():
                    print(f"\n{model.upper()}:")
                    for metric, value in scores.items():
                        print(f"- {metric}: {value:.4f}")
                
                # Make ensemble predictions
                predictions = self.predictor.ensemble_predict(combined_data)
                if predictions is not None:
                    print("\nEnsemble Predictions for next week:")
                    print(predictions.tail(7))
            
            return combined_data
            
        except Exception as e:
            self.logger.error(f"Pipeline error: {e}")
            return None

def main():
    pipeline = DataPipeline()
    combined_data = pipeline.run_pipeline()
    
    if combined_data is not None:
        print("\nData Preview:")
        print(combined_data.head())
        print("\nData Shape:", combined_data.shape)

if __name__ == "__main__":
    main() 