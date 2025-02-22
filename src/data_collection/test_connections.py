import os
import logging
from dotenv import load_dotenv
import praw
from github import Github
import requests
import yfinance as yf

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_reddit():
    """Test Reddit API connection"""
    try:
        reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent="TechTrendAnalyzer/1.0"
        )
        # Test by getting 1 post from r/technology
        posts = list(reddit.subreddit('technology').hot(limit=1))
        logger.info("✅ Reddit API: Connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Reddit API: {str(e)}")
        return False

def test_github():
    """Test GitHub API connection"""
    try:
        github = Github(os.getenv('GITHUB_TOKEN'))
        # Test by getting rate limit info
        github.get_rate_limit()
        logger.info("✅ GitHub API: Connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ GitHub API: {str(e)}")
        return False

def test_news_api():
    """Test News API connection"""
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": "technology",
            "pageSize": 1,
            "apiKey": os.getenv('NEWS_API_KEY')
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        logger.info("✅ News API: Connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ News API: {str(e)}")
        return False

def test_alpha_vantage():
    """Test Alpha Vantage API connection"""
    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": "MSFT",
            "apikey": os.getenv('ALPHA_VANTAGE_KEY')
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        logger.info("✅ Alpha Vantage API: Connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Alpha Vantage API: {str(e)}")
        return False

def test_yfinance():
    """Test Yahoo Finance connection"""
    try:
        msft = yf.Ticker("MSFT")
        msft.info
        logger.info("✅ Yahoo Finance: Connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Yahoo Finance: {str(e)}")
        return False

def main():
    logger.info("Testing API connections...")
    
    results = {
        "Reddit": test_reddit(),
        "GitHub": test_github(),
        "News API": test_news_api(),
        "Alpha Vantage": test_alpha_vantage(),
        "Yahoo Finance": test_yfinance()
    }
    
    logger.info("\nTest Results Summary:")
    for api, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{api}: {status}")

if __name__ == "__main__":
    main() 