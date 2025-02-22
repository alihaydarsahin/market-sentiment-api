import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob
import os
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataAnalyzer:
    def __init__(self):
        self.data_paths = {
            'reddit': 'data/raw/reddit',
            'market': 'data/raw/market',
            'github': 'data/raw/github',
            'news': 'data/raw/news'
        }
        # Create analysis directory
        os.makedirs('data/analysis/figures', exist_ok=True)
    
    def load_latest_data(self):
        """Load most recent data from each source"""
        data = {}
        for source, path in self.data_paths.items():
            try:
                # Get latest file
                files = os.listdir(path)
                if not files:
                    continue
                latest_file = sorted(files)[-1]
                
                # Load data
                df = pd.read_csv(f"{path}/{latest_file}")
                data[source] = df
                
            except Exception as e:
                logger.error(f"Error loading {source} data: {e}")
        
        return data
    
    def analyze_sentiment(self, data):
        """Analyze sentiment across Reddit and News data"""
        sentiment_analysis = {}
        
        # Reddit sentiment
        if 'reddit' in data:
            reddit_df = data['reddit']
            sentiment_analysis['reddit'] = {
                'mean_sentiment': reddit_df['sentiment_polarity'].mean(),
                'sentiment_trend': reddit_df.groupby('subreddit')['sentiment_polarity'].mean().to_dict(),
                'most_positive_topics': reddit_df.nlargest(5, 'sentiment_polarity')[['title', 'sentiment_polarity']].to_dict('records')
            }
        
        # News sentiment
        if 'news' in data:
            news_df = data['news']
            sentiment_analysis['news'] = {
                'mean_sentiment': news_df['sentiment_score'].mean(),
                'sentiment_by_source': news_df.groupby('source')['sentiment_score'].mean().to_dict()
            }
        
        return sentiment_analysis
    
    def analyze_correlations(self, data):
        """Analyze correlations between sentiment and market data"""
        if 'market' not in data or ('reddit' not in data and 'news' not in data):
            return {}
        
        market_df = data['market']
        correlations = {}
        
        # Prepare market data
        market_daily = market_df.groupby('date')['close'].mean().reset_index()
        
        # Correlate with Reddit sentiment
        if 'reddit' in data:
            reddit_df = data['reddit']
            reddit_daily = reddit_df.groupby(pd.to_datetime(reddit_df['created_utc']).dt.date)['sentiment_polarity'].mean()
            correlations['reddit_market'] = market_daily['close'].corr(reddit_daily)
        
        # Correlate with news sentiment
        if 'news' in data:
            news_df = data['news']
            news_daily = news_df.groupby(pd.to_datetime(news_df['publishedAt']).dt.date)['sentiment_score'].mean()
            correlations['news_market'] = market_daily['close'].corr(news_daily)
        
        return correlations
    
    def get_top_topics(self, data):
        """Get trending topics from Reddit and GitHub"""
        topics = {}
        
        # Reddit topics
        if 'reddit' in data:
            reddit_df = data['reddit']
            topics['reddit'] = reddit_df.groupby('subreddit').size().nlargest(5).to_dict()
        
        # GitHub topics
        if 'github' in data:
            github_df = data['github']
            topics['github'] = github_df.groupby('language').size().nlargest(5).to_dict()
        
        return topics
    
    def analyze_market_impact(self, data):
        """Analyze market impact of sentiment"""
        if 'market' not in data:
            return {}
        
        market_df = data['market']
        impact = {
            'price_changes': market_df.groupby('symbol')['change_pct'].mean().to_dict(),
            'volume_changes': market_df.groupby('symbol')['volume'].pct_change().mean().to_dict()
        }
        
        return impact
    
    def analyze_trends(self):
        """Analyze trends across all data sources"""
        data = self.load_latest_data()
        
        analysis = {
            'sentiment': self.analyze_sentiment(data),
            'correlations': self.analyze_correlations(data),
            'top_topics': self.get_top_topics(data),
            'market_impact': self.analyze_market_impact(data)
        }
        
        return analysis
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        analysis = self.analyze_trends()
        
        # Create visualizations
        self.plot_sentiment_trends(analysis['sentiment'])
        self.plot_correlation_matrix(analysis['correlations'])
        self.plot_top_topics(analysis['top_topics'])
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        report_path = f"data/analysis/trend_report_{timestamp}.json"
        
        with open(report_path, 'w') as f:
            json.dump(analysis, f, indent=4)

    def plot_sentiment_trends(self, sentiment_data):
        """Plot sentiment trends"""
        plt.figure(figsize=(12, 6))
        
        if 'reddit' in sentiment_data and sentiment_data['reddit']['sentiment_trend']:
            subreddits = sentiment_data['reddit']['sentiment_trend'].keys()
            sentiments = sentiment_data['reddit']['sentiment_trend'].values()
            plt.bar(subreddits, sentiments, alpha=0.6, label='Reddit')
            plt.legend()  # Only add legend if we have data
        else:
            plt.text(0.5, 0.5, 'No sentiment data available', 
                    horizontalalignment='center',
                    verticalalignment='center')
        
        plt.title('Sentiment Analysis by Source')
        plt.xlabel('Source')
        plt.ylabel('Sentiment Score')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save plot
        plt.savefig('data/analysis/figures/sentiment_trends.png')
        plt.close()
    
    def plot_correlation_matrix(self, correlation_data):
        """Plot correlation matrix"""
        if not correlation_data:
            return
        
        corr_matrix = pd.DataFrame(correlation_data).fillna(0)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
        plt.title('Correlations between Sources')
        plt.tight_layout()
        
        # Save plot
        plt.savefig('data/analysis/figures/correlation_matrix.png')
        plt.close()
    
    def plot_top_topics(self, topics_data):
        """Plot top topics"""
        plt.figure(figsize=(12, 6))
        
        if 'reddit' in topics_data:
            topics = topics_data['reddit'].keys()
            counts = topics_data['reddit'].values()
            plt.bar(topics, counts, alpha=0.6, label='Reddit Topics')
        
        plt.title('Top Topics by Platform')
        plt.xlabel('Topic')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        
        # Save plot
        plt.savefig('data/analysis/figures/top_topics.png')
        plt.close()

def main():
    analyzer = DataAnalyzer()
    analyzer.generate_report()
    logger.info("Analysis complete! Check data/analysis folder for results.")

if __name__ == "__main__":
    main() 