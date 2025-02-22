import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json
import matplotlib.pyplot as plt
import seaborn as sns

def generate_reddit_data():
    """Generate sample Reddit data"""
    subreddits = ['technology', 'programming', 'MachineLearning', 'artificial']
    data = []
    
    for _ in range(100):
        data.append({
            'title': f"Sample Post {_}",
            'score': np.random.randint(1, 1000),
            'comments': np.random.randint(1, 100),
            'url': f"https://reddit.com/r/{np.random.choice(subreddits)}/post_{_}",
            'created_utc': datetime.now() - timedelta(hours=np.random.randint(1, 48)),
            'subreddit': np.random.choice(subreddits),
            'sentiment_polarity': np.random.uniform(-1, 1),
            'sentiment_subjectivity': np.random.uniform(0, 1)
        })
    
    return pd.DataFrame(data)

def generate_market_data():
    """Generate sample market data"""
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
    data = []
    
    for symbol in symbols:
        for i in range(30):
            date = datetime.now() - timedelta(days=i)
            data.append({
                'symbol': symbol,
                'date': date.strftime('%Y-%m-%d'),
                'open': np.random.uniform(100, 200),
                'close': np.random.uniform(100, 200),
                'volume': np.random.randint(1000000, 5000000),
                'change_pct': np.random.uniform(-5, 5)
            })
    
    return pd.DataFrame(data)

def generate_github_data():
    """Generate sample GitHub data"""
    languages = ['Python', 'JavaScript', 'Java', 'TypeScript', 'Go']
    topics = ['AI', 'Machine Learning', 'Web Development', 'Data Science', 'Cloud']
    data = []
    
    for _ in range(50):
        data.append({
            'repo_name': f"sample-repo-{_}",
            'stars': np.random.randint(10, 10000),
            'forks': np.random.randint(1, 1000),
            'language': np.random.choice(languages),
            'topics': np.random.choice(topics, 2).tolist(),
            'description': f"Sample repository description {_}",
            'created_at': datetime.now() - timedelta(days=np.random.randint(1, 365))
        })
    
    return pd.DataFrame(data)

def generate_news_data():
    """Generate sample news data"""
    sources = ['TechCrunch', 'Wired', 'The Verge', 'CNBC', 'Bloomberg']
    topics = ['AI', 'Cryptocurrency', 'Startups', 'Tech Giants', 'Innovation']
    data = []
    
    for _ in range(100):
        topic = np.random.choice(topics)
        data.append({
            'title': f"{topic}: Sample News Title {_}",
            'description': f"Sample news description about {topic}",
            'source': np.random.choice(sources),
            'url': f"https://sample-news.com/article_{_}",
            'publishedAt': datetime.now() - timedelta(hours=np.random.randint(1, 72)),
            'sentiment_score': np.random.uniform(-1, 1),
            'topic': topic
        })
    
    return pd.DataFrame(data)

def generate_analysis_summary():
    """Generate analysis summary file"""
    summary = {
        'timestamp': datetime.now().isoformat(),
        'analysis_period': {
            'start': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'end': datetime.now().strftime('%Y-%m-%d')
        },
        'key_findings': {
            'sentiment': {
                'overall_sentiment': round(np.random.uniform(-1, 1), 2),
                'trend_direction': np.random.choice(['positive', 'negative', 'neutral']),
                'confidence': round(np.random.uniform(0.6, 0.9), 2)
            },
            'top_trends': [
                {'topic': 'AI', 'mentions': np.random.randint(100, 1000)},
                {'topic': 'Crypto', 'mentions': np.random.randint(100, 1000)},
                {'topic': 'Cloud', 'mentions': np.random.randint(100, 1000)}
            ],
            'market_correlation': round(np.random.uniform(-1, 1), 2)
        }
    }
    
    # Save summary
    os.makedirs('data/analysis', exist_ok=True)
    with open('data/analysis/analysis_summary.json', 'w') as f:
        json.dump(summary, f, indent=4)

def save_sample_data():
    """Save all sample data"""
    # Create directories
    for dir_name in ['reddit', 'market', 'github', 'news']:
        os.makedirs(f'data/raw/{dir_name}', exist_ok=True)
    os.makedirs('data/analysis/figures', exist_ok=True)
    
    # Generate and save data
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    
    reddit_df = generate_reddit_data()
    reddit_df.to_csv(f'data/raw/reddit/reddit_data_{timestamp}.csv', index=False)
    
    market_df = generate_market_data()
    market_df.to_csv(f'data/raw/market/market_data_{timestamp}.csv', index=False)
    
    github_df = generate_github_data()
    github_df.to_csv(f'data/raw/github/github_data_{timestamp}.csv', index=False)
    
    news_df = generate_news_data()
    news_df.to_csv(f'data/raw/news/news_data_{timestamp}.csv', index=False)
    
    # Generate summary
    generate_analysis_summary()
    
    # Create sample visualizations
    create_sample_visualizations(reddit_df, market_df, github_df, news_df)
    
    print(f"Sample data and visualizations generated for timestamp: {timestamp}")

def create_sample_visualizations(reddit_df, market_df, github_df, news_df):
    """Create sample visualizations"""
    # 1. Sentiment Distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(reddit_df['sentiment_polarity'], bins=30)
    plt.title('Reddit Sentiment Distribution')
    plt.xlabel('Sentiment Score')
    plt.savefig('data/analysis/figures/sentiment_distribution.png')
    plt.close()
    
    # 2. Technology Trends
    plt.figure(figsize=(12, 6))
    topic_counts = news_df['topic'].value_counts()
    sns.barplot(x=topic_counts.index, y=topic_counts.values)
    plt.title('Technology Trends from News')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('data/analysis/figures/tech_trends.png')
    plt.close()
    
    # 3. Programming Language Popularity
    plt.figure(figsize=(10, 6))
    lang_counts = github_df['language'].value_counts()
    plt.pie(lang_counts.values, labels=lang_counts.index, autopct='%1.1f%%')
    plt.title('Programming Language Distribution')
    plt.savefig('data/analysis/figures/language_distribution.png')
    plt.close()
    
    # 4. Market Trends
    plt.figure(figsize=(12, 6))
    for symbol in market_df['symbol'].unique():
        symbol_data = market_df[market_df['symbol'] == symbol]
        plt.plot(pd.to_datetime(symbol_data['date']), symbol_data['close'], label=symbol)
    plt.title('Stock Price Trends')
    plt.xlabel('Date')
    plt.ylabel('Closing Price')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('data/analysis/figures/market_trends.png')
    plt.close()

if __name__ == "__main__":
    save_sample_data() 