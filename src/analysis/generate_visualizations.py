import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
import numpy as np
from wordcloud import WordCloud

def load_latest_data():
    """Load the most recent data files"""
    data = {}
    data_dirs = {
        'reddit': 'data/raw/reddit',
        'market': 'data/raw/market',
        'github': 'data/raw/github',
        'news': 'data/raw/news'
    }
    
    for source, dir_path in data_dirs.items():
        try:
            files = sorted([f for f in os.listdir(dir_path) if f.endswith('.csv')])
            if files:
                latest_file = files[-1]
                data[source] = pd.read_csv(f"{dir_path}/{latest_file}")
                print(f"Loaded: {source} - {latest_file}")
        except Exception as e:
            print(f"Error: Failed to load {source} data - {e}")
    
    return data

def create_visualizations(data):
    """Create all visualizations"""
    os.makedirs('data/analysis/figures', exist_ok=True)
    
    # 1. Advanced Sentiment Analysis
    if 'reddit' in data and 'news' in data:
        create_sentiment_analysis(data)
    
    # 2. Market Trends and Correlations
    if 'market' in data:
        create_market_analysis(data)
    
    # 3. Technology Trends
    if 'github' in data and 'news' in data:
        create_tech_trends(data)
    
    # 4. Interaction Analysis
    create_interaction_analysis(data)
    
    # 5. Time Series Analysis
    create_time_series_analysis(data)

def create_sentiment_analysis(data):
    """Advanced sentiment analysis visualizations"""
    # 1. Detailed Sentiment Analysis
    plt.figure(figsize=(20, 15))
    
    # Sentiment Distribution with KDE
    plt.subplot(3, 2, 1)
    sns.histplot(data['reddit']['sentiment_polarity'], kde=True, bins=50, color='blue', alpha=0.6)
    plt.axvline(data['reddit']['sentiment_polarity'].mean(), color='red', linestyle='--', label='Mean')
    plt.title('Reddit Sentiment Distribution with Density')
    plt.legend()
    
    # Sentiment Over Time
    plt.subplot(3, 2, 2)
    data['reddit']['date'] = pd.to_datetime(data['reddit']['created_utc']).dt.date
    daily_sentiment = data['reddit'].groupby('date')['sentiment_polarity'].mean()
    sns.lineplot(data=daily_sentiment, marker='o')
    plt.title('Sentiment Trend Over Time')
    plt.xticks(rotation=45)
    
    # Sentiment by Subreddit with Violin Plot
    plt.subplot(3, 2, 3)
    sns.violinplot(data=data['reddit'], x='subreddit', y='sentiment_polarity')
    plt.xticks(rotation=45)
    plt.title('Sentiment Distribution by Subreddit')
    
    # Correlation Matrix
    plt.subplot(3, 2, 4)
    corr_matrix = data['reddit'][['sentiment_polarity', 'score', 'comments']].corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
    plt.title('Correlation Between Metrics')
    
    # Top Positive and Negative Posts
    plt.subplot(3, 2, 5)
    top_posts = data['reddit'].nlargest(10, 'sentiment_polarity')['score']
    sns.barplot(x=top_posts.index, y=top_posts.values)
    plt.title('Top 10 Positive Posts (by Score)')
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig('data/analysis/figures/detailed_sentiment.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_market_analysis(data):
    """Enhanced market analysis visualizations"""
    market_df = data['market']
    
    # Create multiple subplots for different analyses
    fig = plt.figure(figsize=(20, 15))
    
    # 1. Price Trends
    ax1 = plt.subplot(3, 2, 1)
    for symbol in market_df['symbol'].unique():
        symbol_data = market_df[market_df['symbol'] == symbol]
        ax1.plot(pd.to_datetime(symbol_data['date']), 
                symbol_data['close'], 
                label=symbol)
    ax1.set_title('Stock Price Trends')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price')
    ax1.legend()
    ax1.grid(True)
    
    # 2. Volume Analysis
    ax2 = plt.subplot(3, 2, 2)
    volume_by_symbol = market_df.groupby('symbol')['volume'].mean().sort_values(ascending=False)
    sns.barplot(x=volume_by_symbol.index, y=volume_by_symbol.values, ax=ax2)
    ax2.set_title('Average Trading Volume by Symbol')
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45)
    
    # 3. Price Change Distribution
    ax3 = plt.subplot(3, 2, 3)
    market_df['price_change'] = market_df.groupby('symbol')['close'].pct_change()
    sns.histplot(data=market_df, x='price_change', bins=50, kde=True, ax=ax3)
    ax3.set_title('Distribution of Daily Price Changes')
    
    # 4. Volume vs Price Change
    ax4 = plt.subplot(3, 2, 4)
    sns.scatterplot(data=market_df, x='price_change', y='volume', hue='symbol', ax=ax4)
    ax4.set_title('Volume vs Price Change')
    
    # 5. Volatility Analysis
    ax5 = plt.subplot(3, 2, 5)
    volatility = market_df.groupby('symbol')['price_change'].std()
    sns.barplot(x=volatility.index, y=volatility.values, ax=ax5)
    ax5.set_title('Stock Volatility Comparison')
    ax5.set_xticklabels(ax5.get_xticklabels(), rotation=45)
    
    plt.tight_layout()
    plt.savefig('data/analysis/figures/market_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_tech_trends(data):
    """Enhanced technology trends visualizations"""
    fig = plt.figure(figsize=(20, 15))
    
    # 1. Language Trends
    ax1 = plt.subplot(3, 2, 1)
    lang_counts = data['github']['language'].value_counts()
    plt.pie(lang_counts.values[:5], labels=lang_counts.index[:5], autopct='%1.1f%%')
    plt.title('Top 5 Programming Languages')
    
    # 2. Topic Evolution
    ax2 = plt.subplot(3, 2, 2)
    data['news']['date'] = pd.to_datetime(data['news']['publishedAt']).dt.date
    topic_evolution = data['news'].pivot_table(
        index='date', 
        columns='topic', 
        aggfunc='size',
        fill_value=0
    )
    sns.heatmap(topic_evolution, cmap='YlOrRd')
    plt.title('Topic Evolution Over Time')
    
    # 3. Technology Adoption Curve
    ax3 = plt.subplot(3, 2, 3)
    tech_adoption = data['github'].groupby(['language', 'created_at'])['stars'].mean().unstack()
    sns.lineplot(data=tech_adoption)
    plt.title('Technology Adoption Trends')
    plt.xticks(rotation=45)
    
    # 4. Cross-Platform Analysis
    ax4 = plt.subplot(3, 2, 4)
    platform_metrics = pd.DataFrame({
        'GitHub Stars': data['github'].groupby('language')['stars'].mean(),
        'News Mentions': data['news'].groupby('topic').size()
    }).fillna(0)
    sns.scatterplot(data=platform_metrics, x='GitHub Stars', y='News Mentions')
    plt.title('Cross-Platform Technology Impact')
    
    plt.tight_layout()
    plt.savefig('data/analysis/figures/tech_trends_detailed.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_interaction_analysis(data):
    """Interaction analysis visualizations"""
    if 'reddit' in data:
        plt.figure(figsize=(15, 6))
        
        interaction_data = data['reddit'].groupby('subreddit').agg({
            'score': 'mean',
            'comments': 'mean',
            'sentiment_polarity': 'mean'
        })
        
        interaction_data = (interaction_data - interaction_data.mean()) / interaction_data.std()
        
        sns.heatmap(interaction_data, annot=True, cmap='RdYlBu', center=0)
        plt.title('Subreddit Interaction Analysis')
        plt.tight_layout()
        plt.savefig('data/analysis/figures/interaction_analysis.png')
        plt.close()

def create_time_series_analysis(data):
    """Time series analysis visualizations"""
    plt.figure(figsize=(15, 10))
    
    if 'reddit' in data:
        plt.subplot(2, 1, 1)
        data['reddit']['hour'] = pd.to_datetime(data['reddit']['created_utc']).dt.hour
        hourly_activity = data['reddit']['hour'].value_counts().sort_index()
        plt.plot(hourly_activity.index, hourly_activity.values, marker='o')
        plt.title('Daily Reddit Activity')
        plt.xlabel('Hour')
        plt.ylabel('Number of Posts')
        plt.grid(True)
    
    if 'news' in data:
        plt.subplot(2, 1, 2)
        data['news']['day'] = pd.to_datetime(data['news']['publishedAt']).dt.day_name()
        daily_sentiment = data['news'].groupby('day')['sentiment_score'].mean()
        plt.plot(daily_sentiment.index, daily_sentiment.values, marker='s', color='green')
        plt.title('Weekly News Sentiment Trend')
        plt.xticks(rotation=45)
        plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('data/analysis/figures/time_series.png')
    plt.close()

def create_advanced_time_series(data):
    """Advanced time series analysis"""
    fig = plt.figure(figsize=(20, 15))
    
    # 1. Activity Patterns
    ax1 = plt.subplot(3, 2, 1)
    data['reddit']['hour'] = pd.to_datetime(data['reddit']['created_utc']).dt.hour
    data['reddit']['day'] = pd.to_datetime(data['reddit']['created_utc']).dt.day_name()
    activity_matrix = data['reddit'].pivot_table(
        index='day',
        columns='hour',
        values='score',
        aggfunc='count'
    ).fillna(0)
    sns.heatmap(activity_matrix, cmap='YlOrRd')
    plt.title('Activity Heatmap by Day and Hour')
    
    # 2. Engagement Metrics Over Time
    ax2 = plt.subplot(3, 2, 2)
    daily_metrics = data['reddit'].groupby('date').agg({
        'score': 'mean',
        'comments': 'mean',
        'sentiment_polarity': 'mean'
    })
    sns.lineplot(data=daily_metrics)
    plt.title('Daily Engagement Metrics')
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig('data/analysis/figures/advanced_time_series.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    print("Loading data...")
    data = load_latest_data()
    
    print("\nGenerating visualizations...")
    create_visualizations(data)
    
    print("\nVisualization generation complete!")
    print("Check data/analysis/figures/ for the generated plots")

if __name__ == "__main__":
    main() 