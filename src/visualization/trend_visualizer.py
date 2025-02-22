import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import os
from .data_validator import DataValidator
import logging

class TrendVisualizer:
    def __init__(self):
        self.output_dir = 'data/analysis/figures'
        os.makedirs(self.output_dir, exist_ok=True)
        self.validator = DataValidator()
        self.logger = logging.getLogger(__name__)
        
        # Style settings
        plt.style.use('default')
        sns.set_theme()
    
    def validate_and_prepare(self, data):
        """Validate and prepare data for visualization"""
        try:
            # Check data quality
            validation = self.validator.check_data_quality(data)
            
            if not validation['is_valid']:
                self.logger.warning("Data quality issues found:")
                for issue in validation['issues']:
                    self.logger.warning(f"- {issue}")
                return None
            
            # Log statistics
            self.logger.info("Data statistics:")
            for key, value in validation['stats'].items():
                self.logger.info(f"- {key}: {value}")
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error in data preparation: {e}")
            return None
    
    def create_sentiment_trends(self, data):
        """Visualize sentiment trends with error handling"""
        try:
            data = self.validate_and_prepare(data)
            if data is None:
                return
            
            plt.figure(figsize=(12, 6))
            
            # Plot with error handling
            for col, style in [
                ('reddit_sentiment', ('o', 'Reddit')), 
                ('news_sentiment', ('s', 'News'))
            ]:
                if col in data.columns:
                    values = data[col].rolling(window=3).mean()  # Add smoothing
                    plt.plot(data.index, values, 
                            label=f"{style[1]} Sentiment (3-day MA)",
                            marker=style[0])
            
            plt.title('Sentiment Trends Over Time')
            plt.xlabel('Date')
            plt.ylabel('Sentiment Score')
            plt.legend()
            plt.grid(True)
            plt.xticks(rotation=45)
            
            # Add confidence intervals
            if 'reddit_sentiment' in data.columns:
                std = data['reddit_sentiment'].rolling(window=3).std()
                mean = data['reddit_sentiment'].rolling(window=3).mean()
                plt.fill_between(data.index, mean-std, mean+std, alpha=0.2)
            
            plt.tight_layout()
            
            # Save with timestamp and quality settings
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            plt.savefig(
                f"{self.output_dir}/sentiment_trends_{timestamp}.png",
                dpi=300,
                bbox_inches='tight'
            )
            plt.close()
            
        except Exception as e:
            self.logger.error(f"Error creating sentiment trends: {e}")
    
    def create_market_analysis(self, data):
        """Visualize market trends"""
        if 'market_change' in data.columns:
            plt.figure(figsize=(12, 6))
            
            # Market changes
            plt.plot(data.index, data['market_change'].rolling(window=3).mean(), 
                    label='3-Day Moving Average')
            plt.scatter(data.index, data['market_change'], 
                       alpha=0.5, label='Daily Change')
            
            plt.title('Market Trend Analysis')
            plt.xlabel('Date')
            plt.ylabel('Percentage Change')
            plt.legend()
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Save plot
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            plt.savefig(f"{self.output_dir}/market_trends_{timestamp}.png")
            plt.close()
    
    def create_correlation_matrix(self, data):
        """Create correlation heatmap"""
        plt.figure(figsize=(10, 8))
        
        correlation = data.corr()
        mask = np.triu(np.ones_like(correlation, dtype=bool))
        
        sns.heatmap(correlation, mask=mask, annot=True, 
                   cmap='coolwarm', center=0, square=True)
        plt.title('Correlation Matrix')
        plt.tight_layout()
        
        # Save plot
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        plt.savefig(f"{self.output_dir}/correlation_matrix_{timestamp}.png")
        plt.close() 