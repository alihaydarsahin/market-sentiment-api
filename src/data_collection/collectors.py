import praw
import yfinance as yf
import requests
from datetime import datetime, timedelta
import logging
import os
import json
import pandas as pd
import time
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Optional imports - handle gracefully if not installed
try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False

try:
    from github import Github
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False

try:
    import fredapi
    import pandas_datareader as pdr
    ECONOMIC_AVAILABLE = True
except ImportError:
    ECONOMIC_AVAILABLE = False

# Load environment variables
load_dotenv()

class BaseCollector:
    def __init__(self, log_file: str):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.setup_logging(log_file)

    def setup_logging(self, log_file: str):
        """Setup logging configuration"""
        log_dir = 'data/logs'
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, log_file)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler()
            ]
        )

    def save_data_to_csv(self, data: List[Dict[str, Any]], filename_prefix: str):
        """Save data to CSV file with timestamp"""
        if not data:
            self.logger.warning(f"No {filename_prefix} data to save!")
            return
        
        try:
            # Create directory if it doesn't exist
            os.makedirs('data/raw', exist_ok=True)
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"data/raw/{filename_prefix}_{timestamp}.csv"
            
            # Create DataFrame and save
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False)
            self.logger.info(f"Saved {len(data)} records to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving data to CSV: {e}")

class DataCollector(BaseCollector):
    def __init__(self):
        super().__init__('data_collector.log')
        self.setup_apis()

    def setup_apis(self):
        """Setup API connections"""
        # Reddit API setup
        reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
        reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        if reddit_client_id and reddit_client_secret:
            self.reddit = praw.Reddit(
                client_id=reddit_client_id,
                client_secret=reddit_client_secret,
                user_agent="TrendAnalyzer/1.0"
            )
        else:
            self.logger.warning("Reddit API credentials not found")
            self.reddit = None
        
        # News API setup
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.news_base_url = "https://newsapi.org/v2/everything"
        
        # Market data setup
        self.tech_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
        self.subreddits = ['technology', 'gadgets', 'tech']
        
        # Social media setup
        if TWEEPY_AVAILABLE:
            twitter_api_key = os.getenv('TWITTER_API_KEY')
            twitter_api_secret = os.getenv('TWITTER_API_SECRET')
            if twitter_api_key and twitter_api_secret:
                auth = tweepy.OAuthHandler(twitter_api_key, twitter_api_secret)
                self.twitter_api = tweepy.API(auth)
            else:
                self.logger.warning("Twitter API credentials not found")
                self.twitter_api = None
        else:
            self.logger.warning("tweepy package not installed, Twitter functionality not available")
            self.twitter_api = None
            
        # Economic data setup
        if ECONOMIC_AVAILABLE:
            fred_api_key = os.getenv('FRED_API_KEY')
            if fred_api_key:
                self.fred = fredapi.Fred(api_key=fred_api_key)
                self.economic_indicators = {
                    'GDP': 'GDP',
                    'Inflation': 'CPIAUCSL',
                    'Unemployment': 'UNRATE',
                    'Consumer_Confidence': 'UMCSENT'
                }
            else:
                self.logger.warning("FRED API key not found")
                self.fred = None
        else:
            self.logger.warning("fredapi package not installed, economic data functionality not available")
            self.fred = None

    def collect_reddit_data(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Collect technology-related discussions from Reddit"""
        if not self.reddit:
            self.logger.error("Reddit API not initialized")
            return []
            
        try:
            discussions = []
            for subreddit in self.subreddits:
                for post in self.reddit.subreddit(subreddit).hot(limit=limit//len(self.subreddits)):
                    discussions.append({
                        'title': post.title,
                        'score': post.score,
                        'comments': post.num_comments,
                        'created_utc': datetime.fromtimestamp(post.created_utc).isoformat(),
                        'subreddit': subreddit,
                        'url': post.url,
                        'source': 'reddit'
                    })
            self.logger.info(f"Collected {len(discussions)} Reddit discussions")
            return discussions
        except Exception as e:
            self.logger.error(f"Error collecting Reddit data: {e}")
            return []

    def collect_market_data(self, days: int = 30) -> List[Dict[str, Any]]:
        """Collect stock market data"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            data = []
            
            for symbol in self.tech_symbols:
                stock = yf.Ticker(symbol)
                hist = stock.history(start=start_date, end=end_date)
                
                for date, row in hist.iterrows():
                    data.append({
                        'symbol': symbol,
                        'date': date.date().isoformat(),
                        'open': row['Open'],
                        'close': row['Close'],
                        'volume': row['Volume'],
                        'change_pct': ((row['Close'] - row['Open']) / row['Open']) * 100,
                        'source': 'market'
                    })
            
            self.logger.info(f"Collected {len(data)} stock data points")
            return data
        except Exception as e:
            self.logger.error(f"Error collecting stock data: {e}")
            return []

    def collect_news_data(self, max_retries: int = 3, retry_delay: int = 5) -> List[Dict[str, Any]]:
        """Collect news articles"""
        if not self.news_api_key:
            self.logger.error("News API key not found")
            return []
            
        params = {
            'q': 'technology OR ecommerce OR retail',
            'language': 'en',
            'sortBy': 'publishedAt',
            'apiKey': self.news_api_key,
            'pageSize': 100
        }
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Fetching news... Attempt {attempt + 1}/{max_retries}")
                response = requests.get(self.news_base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                if not isinstance(data, dict) or "articles" not in data:
                    self.logger.error("Invalid API response")
                    continue
                
                articles = data["articles"]
                
                # Clean and format articles
                cleaned_articles = []
                for article in articles:
                    # Check required fields
                    required_fields = ["title", "description", "url", "publishedAt"]
                    if not all(field in article for field in required_fields):
                        continue
                    
                    # Clean and format data
                    cleaned_article = {
                        "title": article["title"].strip(),
                        "description": article["description"].strip() if article["description"] else "",
                        "url": article["url"],
                        "publishedAt": article["publishedAt"],
                        "source": article["source"]["name"] if "source" in article else "Unknown",
                        "data_source": "news_api"
                    }
                    
                    cleaned_articles.append(cleaned_article)
                
                self.logger.info(f"Collected {len(cleaned_articles)} news articles")
                return cleaned_articles
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Error fetching data: {e}")
                if attempt < max_retries - 1:
                    self.logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                continue
            except json.JSONDecodeError as e:
                self.logger.error(f"JSON parsing error: {e}")
                continue
                
        self.logger.error("Maximum retry attempts reached")
        return []

    def collect_social_trends(self) -> List[Dict[str, Any]]:
        """Collect technology-related trending topics from social media"""
        if not self.twitter_api:
            self.logger.error("Twitter API not initialized")
            return []
            
        try:
            # Get worldwide trends
            trends = self.twitter_api.get_place_trends(1)  # 1 = worldwide
            
            # Filter tech-related trends
            tech_keywords = ['tech', 'technology', 'ai', 'crypto', 'digital']
            tech_trends = []
            
            for trend in trends[0]['trends']:
                if any(keyword in trend['name'].lower() for keyword in tech_keywords):
                    tech_trends.append({
                        'name': trend['name'],
                        'url': trend['url'],
                        'tweet_volume': trend['tweet_volume'],
                        'source': 'twitter',
                        'timestamp': datetime.now().isoformat()
                    })
            
            self.logger.info(f"Collected {len(tech_trends)} social media trends")
            return tech_trends
        except Exception as e:
            self.logger.error(f"Error collecting social trends: {e}")
            return []

    def collect_economic_data(self) -> Dict[str, Any]:
        """Collect major economic indicators"""
        if not self.fred:
            self.logger.error("FRED API not initialized")
            return {}
            
        data = {}
        for name, series_id in self.economic_indicators.items():
            try:
                series = self.fred.get_series(series_id)
                data[name] = series.to_dict()
            except Exception as e:
                self.logger.error(f"Error collecting {name}: {e}")
        
        self.logger.info(f"Collected economic data for {len(data)} indicators")
        return data

    def collect_all_data(self) -> Dict[str, Any]:
        """Collect all available data types"""
        data = {
            'reddit': self.collect_reddit_data(),
            'market': self.collect_market_data(),
            'news': self.collect_news_data(),
            'social': self.collect_social_trends(),
            'economic': self.collect_economic_data()
        }
        
        self.logger.info("Collected all data types")
        return data 