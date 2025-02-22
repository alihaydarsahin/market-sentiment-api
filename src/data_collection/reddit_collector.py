import praw
import pandas as pd
from datetime import datetime
import os
from textblob import TextBlob
import logging
from dotenv import load_dotenv

load_dotenv()

class RedditDataCollector:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent="TrendAnalyzer/1.0"
        )
        self.subreddits = ['technology', 'gadgets', 'tech']
        self.logger = logging.getLogger(__name__)
        
    def collect_tech_discussions(self, limit=100):
        """Collect technology-related discussions"""
        try:
            discussions = []
            
            for subreddit in self.subreddits:
                try:
                    for post in self.reddit.subreddit(subreddit).hot(limit=limit//len(self.subreddits)):
                        discussions.append({
                            'title': post.title,
                            'score': post.score,
                            'comments': post.num_comments,
                            'created_utc': datetime.fromtimestamp(post.created_utc).isoformat(),
                            'subreddit': subreddit,
                            'url': post.url
                        })
                except Exception as e:
                    self.logger.error(f"Error collecting from r/{subreddit}: {e}")
                    continue
            
            self.logger.info(f"Collected {len(discussions)} discussions")
            return discussions
            
        except Exception as e:
            self.logger.error(f"Error collecting Reddit data: {e}")
            return [] 