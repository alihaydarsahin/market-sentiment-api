import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
import logging
from textblob import TextBlob
import json
import numpy as np

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

class NewsAnalyzerLight:
    def __init__(self):
        self.figure_size = (10, 5)  # Smaller figures
        
    def load_news_data(self):
        """Load data in chunks"""
        try:
            raw_files = os.listdir("data/raw")
            news_files = [f for f in raw_files if f.startswith("news_data_")]
            
            if not news_files:
                logger.error("No news data found!")
                return None
                
            latest_file = sorted(news_files)[-1]
            
            # Read in chunks
            chunks = []
            for chunk in pd.read_csv(f"data/raw/{latest_file}", chunksize=100):
                chunk = chunk[['title', 'description', 'url', 'publishedAt']]
                chunks.append(chunk)
            
            df = pd.concat(chunks, ignore_index=True)
            df['publishedAt'] = pd.to_datetime(df['publishedAt'])
            
            # Determine category
            df['category'] = df.apply(self.get_category, axis=1)
            
            # Interaction score
            df['interaction_score'] = np.random.randint(10, 1000, size=len(df))
            
            logger.info(f"Loaded {len(df)} articles")
            return df
            
        except Exception as e:
            logger.error(f"Data loading error: {e}")
            return None
    
    def get_category(self, row):
        """Simple category determination"""
        text = f"{row['title']} {row['description']}".lower()
        
        if any(word in text for word in ['economy', 'dollar', 'euro', 'stock']):
            return 'economy'
        elif any(word in text for word in ['technology', 'software', 'robot']):
            return 'technology'
        elif any(word in text for word in ['politics', 'election', 'parliament']):
            return 'politics'
        else:
            return 'other'
    
    def analyze_by_category(self, df):
        """Basic category-based analysis"""
        try:
            # Sentiment analysis (in chunks)
            sentiments = []
            for i in range(0, len(df), 100):
                chunk = df.iloc[i:i+100]
                chunk_sentiments = chunk['title'].apply(
                    lambda x: TextBlob(str(x)).sentiment.polarity
                )
                sentiments.extend(chunk_sentiments)
            
            df['sentiment'] = sentiments
            
            # Category statistics
            stats = df.groupby('category').agg({
                'sentiment': ['mean', 'count'],
                'interaction_score': 'mean'
            }).round(3)
            
            # Simple bar plot
            plt.figure(figsize=self.figure_size)
            stats['sentiment']['mean'].plot(kind='bar')
            plt.title('Average Sentiment by Category')
            plt.xlabel('Category')
            plt.ylabel('Sentiment Score')
            plt.tight_layout()
            plt.savefig('data/figures/category_sentiment.png', dpi=100)
            plt.close()
            
            return stats.to_dict()
            
        except Exception as e:
            logger.error(f"Category analysis error: {e}")
            return None
    
    def analyze_top_news(self, df):
        """Analyze top 5 news articles"""
        try:
            top_5 = df.nlargest(5, 'interaction_score')[
                ['title', 'category', 'sentiment']
            ]
            
            return top_5.to_dict('records')
            
        except Exception as e:
            logger.error(f"Popular news analysis error: {e}")
            return None
    
    def save_report(self, category_stats, top_news):
        """Save simple report"""
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'category_analysis': category_stats,
                'top_news': top_news
            }
            
            with open('data/analysis/news_report.json', 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=4, ensure_ascii=False)
            
            logger.info("Report saved successfully")
            
        except Exception as e:
            logger.error(f"Report saving error: {e}")

def main():
    try:
        analyzer = NewsAnalyzerLight()
        
        # Load data
        df = analyzer.load_news_data()
        if df is None:
            return
        
        # Basic analysis
        category_stats = analyzer.analyze_by_category(df)
        top_news = analyzer.analyze_top_news(df)
        
        # Save report
        analyzer.save_report(category_stats, top_news)
        
        logger.info("Analysis completed!")
        
    except Exception as e:
        logger.error(f"Program error: {e}")

if __name__ == "__main__":
    main() 