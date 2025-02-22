import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
import logging
from collections import Counter
import re
from textblob import TextBlob
import json
import numpy as np
import seaborn as sns

# Create directories
os.makedirs("data/logs", exist_ok=True)
os.makedirs("data/figures", exist_ok=True)
os.makedirs("data/analysis", exist_ok=True)

# Logging settings
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/news_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NewsAnalyzer:
    def __init__(self):
        self.figure_size = (12, 6)
        self.colors = ['#2ecc71', '#3498db', '#e74c3c', '#f1c40f', '#9b59b6']
        
    def load_news_data(self):
        """Load and preprocess latest news data"""
        try:
            raw_files = os.listdir("data/raw")
            news_files = [f for f in raw_files if f.startswith("news_data_")]
            
            if not news_files:
                logger.error("No news data found!")
                return None
                
            latest_file = sorted(news_files)[-1]
            df = pd.read_csv(f"data/raw/{latest_file}")
            
            # Convert date column
            df['publishedAt'] = pd.to_datetime(df['publishedAt'])
            
            # Extract categories
            def extract_category(row):
                text = f"{row['title']} {row['description']}".lower()
                
                categories = {
                    'economy': ['economy', 'dollar', 'euro', 'stock', 'market', 'finance', 
                              'trade', 'business', 'investment', 'bank'],
                    
                    'technology': ['technology', 'software', 'ai', 'robot', 'computer', 
                                 'internet', 'mobile', 'cyber', 'digital', 'blockchain',
                                 'startup', 'innovation', 'app', 'data', 'online'],
                    
                    'politics': ['politics', 'election', 'parliament', 'minister', 'president',
                               'party', 'government', 'policy', 'diplomatic', 'law'],
                    
                    'sports': ['sports', 'football', 'basketball', 'match', 'tournament',
                             'championship', 'league', 'transfer', 'team', 'player'],
                    
                    'health': ['health', 'hospital', 'doctor', 'treatment', 'medicine',
                             'covid', 'virus', 'vaccine', 'disease', 'medical'],
                }
                
                # Calculate score for each category
                category_scores = {}
                for cat, keywords in categories.items():
                    score = sum(1 for keyword in keywords if keyword in text)
                    if score > 0:
                        category_scores[cat] = score
                
                # Return highest scoring category
                if category_scores:
                    return max(category_scores.items(), key=lambda x: x[1])[0]
                return 'other'
            
            df['category'] = df.apply(extract_category, axis=1)
            
            # Calculate interaction score
            if 'url' in df.columns:
                df['interaction_score'] = df['url'].apply(self.get_interaction_score)
            
            logger.info(f"Loaded {len(df)} articles")
            return df
            
        except Exception as e:
            logger.error(f"Data loading error: {e}")
            return None
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of text"""
        try:
            analysis = TextBlob(text)
            return {
                'polarity': analysis.sentiment.polarity,
                'subjectivity': analysis.sentiment.subjectivity
            }
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return None
    
    def save_report(self, analysis_results):
        """Save analysis report"""
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'analysis_results': analysis_results
            }
            
            with open('data/analysis/news_report.json', 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=4, ensure_ascii=False)
            
            logger.info("Report saved successfully")
            
        except Exception as e:
            logger.error(f"Report saving error: {e}")

def main():
    try:
        analyzer = NewsAnalyzer()
        
        # Load data
        df = analyzer.load_news_data()
        if df is None:
            return
        
        # Basic analysis
        results = {
            'total_articles': len(df),
            'categories': df['category'].value_counts().to_dict(),
            'date_range': {
                'start': df['publishedAt'].min().isoformat(),
                'end': df['publishedAt'].max().isoformat()
            }
        }
        
        # Save report
        analyzer.save_report(results)
        
        logger.info("Analysis completed!")
        
    except Exception as e:
        logger.error(f"Program error: {e}")

if __name__ == "__main__":
    main() 