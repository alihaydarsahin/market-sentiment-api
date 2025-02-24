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
from wordcloud import WordCloud
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import yfinance as yf

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

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
        self.stop_words = set(stopwords.words('english'))
        self.tech_companies = ['Apple', 'Microsoft', 'Google', 'Amazon', 'Meta', 'Tesla']
        
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
            
            # Extract categories and entities
            df['category'] = df.apply(self.extract_category, axis=1)
            df['entities'] = df.apply(self.extract_entities, axis=1)
            df['keywords'] = df.apply(self.extract_keywords, axis=1)
            
            # Perform sentiment analysis
            df['sentiment'] = df.apply(self.analyze_sentiment, axis=1)
            
            logger.info(f"Loaded and processed {len(df)} articles")
            return df
            
        except Exception as e:
            logger.error(f"Data loading error: {e}")
            return None
    
    def extract_category(self, row):
        """Enhanced category extraction with machine learning topics"""
        text = f"{row['title']} {row['description']}".lower()
        
        categories = {
            'ai_ml': ['artificial intelligence', 'machine learning', 'deep learning', 'neural network', 
                     'ai model', 'chatgpt', 'large language model', 'computer vision'],
            
            'blockchain': ['blockchain', 'cryptocurrency', 'bitcoin', 'ethereum', 'web3', 
                         'defi', 'nft', 'smart contract'],
            
            'cloud_tech': ['cloud computing', 'aws', 'azure', 'google cloud', 'saas', 
                          'cloud native', 'kubernetes', 'docker'],
            
            'cybersecurity': ['cybersecurity', 'security breach', 'hacking', 'malware', 
                            'ransomware', 'data privacy', 'encryption'],
            
            'ecommerce': ['e-commerce', 'online shopping', 'digital retail', 'marketplace',
                         'online store', 'digital commerce', 'retail tech'],
            
            'fintech': ['fintech', 'digital payment', 'mobile banking', 'digital wallet',
                       'online payment', 'financial technology']
        }
        
        # Calculate score for each category
        category_scores = {}
        for cat, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                category_scores[cat] = score
        
        return max(category_scores.items(), key=lambda x: x[1])[0] if category_scores else 'other'
    
    def extract_entities(self, row):
        """Extract named entities from text"""
        text = f"{row['title']} {row['description']}"
        tokens = word_tokenize(text)
        pos_tags = nltk.pos_tag(tokens)
        
        entities = []
        for word, tag in pos_tags:
            if tag.startswith(('NNP', 'NNPS')):  # Proper nouns
                entities.append(word)
        
        return list(set(entities))
    
    def extract_keywords(self, row):
        """Extract important keywords using TF-IDF"""
        text = f"{row['title']} {row['description']}"
        tokens = word_tokenize(text.lower())
        
        # Remove stopwords and short words
        keywords = [word for word in tokens 
                   if word not in self.stop_words and len(word) > 2]
        
        return list(set(keywords))
    
    def analyze_sentiment(self, row):
        """Enhanced sentiment analysis"""
        try:
            text = f"{row['title']} {row['description']}"
            analysis = TextBlob(text)
            
            return {
                'polarity': analysis.sentiment.polarity,
                'subjectivity': analysis.sentiment.subjectivity,
                'is_positive': analysis.sentiment.polarity > 0,
                'is_objective': analysis.sentiment.subjectivity < 0.5
            }
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return None
    
    def analyze_tech_impact(self, df):
        """Analyze impact on tech companies"""
        tech_mentions = {company: 0 for company in self.tech_companies}
        tech_sentiment = {company: [] for company in self.tech_companies}
        
        for _, row in df.iterrows():
            text = f"{row['title']} {row['description']}".lower()
            for company in self.tech_companies:
                if company.lower() in text:
                    tech_mentions[company] += 1
                    if row['sentiment']:
                        tech_sentiment[company].append(row['sentiment']['polarity'])
        
        # Calculate average sentiment
        tech_avg_sentiment = {}
        for company in self.tech_companies:
            if tech_sentiment[company]:
                tech_avg_sentiment[company] = np.mean(tech_sentiment[company])
        
        return tech_mentions, tech_avg_sentiment
    
    def create_visualizations(self, df):
        """Create comprehensive visualizations"""
        # 1. Sentiment Distribution
        plt.figure(figsize=self.figure_size)
        sentiments = [s['polarity'] for s in df['sentiment'] if s]
        sns.histplot(sentiments, bins=30)
        plt.title('News Sentiment Distribution')
        plt.xlabel('Sentiment Score')
        plt.savefig('data/figures/sentiment_distribution.png')
        plt.close()
        
        # 2. Category Distribution
        plt.figure(figsize=self.figure_size)
        df['category'].value_counts().plot(kind='bar')
        plt.title('News Category Distribution')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('data/figures/category_distribution.png')
        plt.close()
        
        # 3. Word Cloud
        plt.figure(figsize=(10, 10))
        text = ' '.join([' '.join(k) for k in df['keywords'] if isinstance(k, list)])
        wordcloud = WordCloud(width=800, height=800, background_color='white').generate(text)
        plt.imshow(wordcloud)
        plt.axis('off')
        plt.title('News Keywords Word Cloud')
        plt.savefig('data/figures/news_wordcloud.png')
        plt.close()
        
        # 4. Tech Company Analysis
        tech_mentions, tech_sentiment = self.analyze_tech_impact(df)
        
        plt.figure(figsize=self.figure_size)
        companies = list(tech_mentions.keys())
        mentions = list(tech_mentions.values())
        sentiments = [tech_sentiment.get(company, 0) for company in companies]
        
        x = range(len(companies))
        plt.bar(x, mentions)
        plt.xticks(x, companies, rotation=45)
        plt.title('Tech Company Mentions in News')
        plt.tight_layout()
        plt.savefig('data/figures/tech_mentions.png')
        plt.close()
    
    def generate_report(self, df):
        """Generate comprehensive analysis report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'analysis_period': {
                'start': df['publishedAt'].min().isoformat(),
                'end': df['publishedAt'].max().isoformat()
            },
            'summary_stats': {
                'total_articles': len(df),
                'categories': df['category'].value_counts().to_dict(),
                'avg_sentiment': np.mean([s['polarity'] for s in df['sentiment'] if s]),
                'sentiment_distribution': {
                    'positive': len([s for s in df['sentiment'] if s and s['is_positive']]),
                    'negative': len([s for s in df['sentiment'] if s and not s['is_positive']])
                }
            },
            'tech_analysis': {
                'mentions': self.analyze_tech_impact(df)[0],
                'sentiment': self.analyze_tech_impact(df)[1]
            },
            'trending_topics': self.get_trending_topics(df)
        }
        
        # Save report
        with open('data/analysis/news_analysis_report.json', 'w') as f:
            json.dump(report, f, indent=4)
        
        return report
    
    def get_trending_topics(self, df):
        """Identify trending topics"""
        all_keywords = []
        for keywords in df['keywords']:
            if isinstance(keywords, list):
                all_keywords.extend(keywords)
        
        return Counter(all_keywords).most_common(10)

def main():
    try:
        analyzer = NewsAnalyzer()
        
        # Load and analyze data
        df = analyzer.load_news_data()
        if df is None:
            return
        
        # Create visualizations
        analyzer.create_visualizations(df)
        
        # Generate report
        report = analyzer.generate_report(df)
        
        logger.info("Analysis completed successfully!")
        logger.info(f"Report saved to: data/analysis/news_analysis_report.json")
        
    except Exception as e:
        logger.error(f"Program error: {e}")

if __name__ == "__main__":
    main() 