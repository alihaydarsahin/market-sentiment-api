import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import matplotlib.pyplot as plt
import seaborn as sns
import json

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/data_quality.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataQualityChecker:
    def __init__(self):
        self.data_dir = 'data/processed'
        self.raw_dir = 'data/raw'
        self.figures_dir = 'data/analysis/figures'
        self.analysis_dir = 'data/analysis'
        self.logs_dir = 'data/logs'
        
        # Create directories if they don't exist
        for dir_path in [self.data_dir, self.raw_dir, self.figures_dir, self.logs_dir]:
            os.makedirs(dir_path, exist_ok=True)
    
    def find_data_files(self, source_type):
        """Find all data files for a given source type across directories"""
        data_files = []
        
        # Check in raw directory
        if os.path.exists(self.raw_dir):
            data_files.extend([
                os.path.join(self.raw_dir, f) 
                for f in os.listdir(self.raw_dir) 
                if source_type in f.lower()
            ])
        
        # Check in processed directory
        if os.path.exists(self.data_dir):
            data_files.extend([
                os.path.join(self.data_dir, f) 
                for f in os.listdir(self.data_dir) 
                if source_type in f.lower()
            ])
        
        # Check in analysis directory
        if os.path.exists(self.analysis_dir):
            for root, _, files in os.walk(self.analysis_dir):
                data_files.extend([
                    os.path.join(root, f) 
                    for f in files 
                    if source_type in f.lower() and f.endswith('.csv')
                ])
        
        return sorted(data_files)
    
    def extract_date_from_path(self, file_path):
        """Extract date from file path using multiple patterns"""
        try:
            # Try different date patterns in the filename
            filename = os.path.basename(file_path)
            parts = filename.replace('.csv', '').split('_')
            
            # Look for 8-digit pattern (YYYYMMDD)
            date_parts = [p for p in parts if len(p) == 8 and p.isdigit()]
            if date_parts:
                return datetime.strptime(date_parts[0], '%Y%m%d')
            
            # Look for directory name with date pattern
            dir_name = os.path.basename(os.path.dirname(file_path))
            if 'reddit_data_' in dir_name:
                date_str = dir_name.split('reddit_data_')[1]
                return datetime.strptime(date_str, '%Y%m%d_%H%M')
            
            return None
            
        except Exception as e:
            logger.debug(f"Could not extract date from {file_path}: {e}")
            return None
    
    def check_data_freshness(self):
        """Check if data is up to date"""
        try:
            freshness = {
                'reddit': {'latest_file': None, 'days_old': None, 'is_fresh': False},
                'news': {'latest_file': None, 'days_old': None, 'is_fresh': False},
                'market': {'latest_file': None, 'days_old': None, 'is_fresh': False}
            }
            
            for source in freshness.keys():
                files = self.find_data_files(source)
                if files:
                    latest_file = files[-1]
                    file_date = self.extract_date_from_path(latest_file)
                    
                    if file_date:
                        days_old = (datetime.now() - file_date).days
                        freshness[source] = {
                            'latest_file': latest_file,
                            'days_old': days_old,
                            'is_fresh': days_old <= 1
                        }
                        logger.info(f"Found {source} data: {os.path.basename(latest_file)}, {days_old} days old")
                    else:
                        logger.warning(f"Could not determine date for {latest_file}")
            
            return freshness
            
        except Exception as e:
            logger.error(f"Error checking data freshness: {e}")
            return None
    
    def analyze_sentiment_distribution(self):
        """Analyze sentiment distribution and detect anomalies"""
        try:
            # Check if processed directory exists and has files
            if not os.path.exists(self.data_dir):
                logger.warning(f"Processed data directory not found: {self.data_dir}")
                return None
            
            combined_files = [f for f in os.listdir(self.data_dir) 
                            if f.startswith('combined_data_')]
            
            if not combined_files:
                logger.warning("No combined data files found")
                return None
                
            latest_file = sorted(combined_files)[-1]
            data = pd.read_csv(os.path.join(self.data_dir, latest_file))
            
            sentiment_stats = {}
            for col in ['reddit_sentiment', 'news_sentiment']:
                if col in data.columns:
                    non_null_data = data[col].dropna()
                    stats = {
                        'mean': non_null_data.mean() if len(non_null_data) > 0 else None,
                        'std': non_null_data.std() if len(non_null_data) > 0 else None,
                        'missing': data[col].isnull().sum(),
                        'missing_pct': (data[col].isnull().sum() / len(data)) * 100
                    }
                    
                    # Plot distribution if we have non-null values
                    if len(non_null_data) > 0:
                        plt.figure(figsize=(10, 6))
                        sns.histplot(data=non_null_data, bins=30)
                        plt.title(f'{col} Distribution')
                        plt.savefig(os.path.join(self.figures_dir, f'{col}_dist.png'))
                        plt.close()
                    
                    sentiment_stats[col] = stats
            
            return sentiment_stats
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment distribution: {e}")
            return None
    
    def check_data_consistency(self):
        """Check data consistency across different sources"""
        try:
            if not os.path.exists(self.data_dir):
                logger.warning(f"Processed data directory not found: {self.data_dir}")
                return None
            
            combined_files = [f for f in os.listdir(self.data_dir) 
                            if f.startswith('combined_data_')]
            
            if not combined_files:
                logger.warning("No combined data files found")
                return None
                
            latest_file = sorted(combined_files)[-1]
            data = pd.read_csv(os.path.join(self.data_dir, latest_file))
            
            # Ensure we have a date column
            date_col = 'date' if 'date' in data.columns else 'Unnamed: 0'
            if date_col not in data.columns:
                logger.error("No date column found in data")
                return None
            
            # Convert date column to datetime
            data[date_col] = pd.to_datetime(data[date_col])
            
            # Check date consistency
            date_gaps = pd.date_range(
                start=data[date_col].min(),
                end=data[date_col].max()
            ).difference(data[date_col])
            
            # Check value ranges for non-date columns
            value_ranges = {}
            for col in data.columns:
                if col != date_col:
                    non_null_data = data[col].dropna()
                    if len(non_null_data) > 0:
                        value_ranges[col] = {
                            'min': float(non_null_data.min()),
                            'max': float(non_null_data.max()),
                            'within_range': all([
                                non_null_data.min() >= -1 if 'sentiment' in col else True,
                                non_null_data.max() <= 1 if 'sentiment' in col else True
                            ])
                        }
            
            return {
                'missing_dates': len(date_gaps),
                'date_gaps': [d.strftime('%Y-%m-%d') for d in date_gaps],
                'value_ranges': value_ranges
            }
            
        except Exception as e:
            logger.error(f"Error checking data consistency: {e}")
            return None
    
    def get_latest_data(self):
        """
        Get the latest combined data file with improved error handling and date-based sorting.
        
        Returns:
            pd.DataFrame | None: The latest data as a DataFrame, or None if no data or error occurs
        """
        try:
            # Check if directory exists
            if not os.path.exists(self.data_dir):
                logger.error(f"Data directory {self.data_dir} does not exist")
                return None
            
            # Get all combined data files
            combined_files = [f for f in os.listdir(self.data_dir) if f.startswith('combined_data_')]
            
            if not combined_files:
                logger.warning("No combined data files found in directory")
                return None
            
            # Sort by date in filename (assuming format: combined_data_YYYYMMDD.csv)
            try:
                latest_file = max(combined_files, key=lambda f: f.split('_')[-1].replace('.csv', ''))
            except Exception as e:
                logger.error(f"Error finding latest file: {e}")
                return None
            
            file_path = os.path.join(self.data_dir, latest_file)
            
            # Verify file exists and is readable
            if not os.path.isfile(file_path):
                logger.error(f"File {file_path} does not exist")
                return None
            
            # Read the CSV file with proper error handling
            try:
                data = pd.read_csv(file_path)
                if data.empty:
                    logger.warning(f"File {latest_file} is empty")
                    return None
                
                logger.info(f"Successfully loaded data from {latest_file}")
                return data
                
            except pd.errors.EmptyDataError:
                logger.error(f"File {latest_file} is empty")
                return None
            except pd.errors.ParserError:
                logger.error(f"Error parsing CSV file {latest_file}")
                return None
            except Exception as e:
                logger.error(f"Unexpected error reading {latest_file}: {e}")
                return None
            
        except Exception as e:
            logger.error(f"Unexpected error in get_latest_data: {e}")
            return None
    
    def generate_quality_report(self):
        """Generate comprehensive data quality report"""
        try:
            freshness = self.check_data_freshness() or {}
            sentiment_stats = self.analyze_sentiment_distribution() or {}
            consistency = self.check_data_consistency() or {}
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'freshness': freshness,
                'sentiment_stats': sentiment_stats,
                'consistency': consistency
            }
            
            # Save report
            report_path = os.path.join(
                self.figures_dir,
                f'data_quality_report_{datetime.now().strftime("%Y%m%d_%H%M")}.json'
            )
            
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=4, default=str)
            
            # Log summary
            logger.info("\nData Quality Report Summary:")
            logger.info(f"Data freshness: {len([f for f in freshness.values() if f['is_fresh']])}/3 sources are fresh")
            logger.info(f"Sentiment analysis: {len(sentiment_stats)} sources analyzed")
            logger.info(f"Data consistency: {consistency.get('missing_dates', 'N/A')} missing dates")
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating quality report: {e}")
            return None

if __name__ == '__main__':
    checker = DataQualityChecker()
    report = checker.generate_quality_report()
    
    if report:
        logger.info("Data quality report generated successfully!")
    else:
        logger.error("Failed to generate data quality report!") 