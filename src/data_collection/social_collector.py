import tweepy
import logging
from datetime import datetime

# Setup logging
logger = logging.getLogger(__name__)

class SocialMediaCollector:
    def __init__(self, twitter_api_key, twitter_api_secret):
        auth = tweepy.OAuthHandler(twitter_api_key, twitter_api_secret)
        self.api = tweepy.API(auth)
        
    def collect_tech_trends(self):
        """Collect technology-related trending topics"""
        try:
            # Get worldwide trends
            trends = self.api.get_place_trends(1)  # 1 = worldwide
            
            # Filter tech-related trends
            tech_keywords = ['tech', 'technology', 'ai', 'crypto', 'digital']
            tech_trends = [
                trend for trend in trends[0]['trends']
                if any(keyword in trend['name'].lower() for keyword in tech_keywords)
            ]
            
            return tech_trends
        except Exception as e:
            logger.error(f"Error collecting trends: {e}")
            return [] 