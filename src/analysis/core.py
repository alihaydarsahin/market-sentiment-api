"""
Core Analysis Module - Provides base classes for data analysis
"""

import os
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import json
from textblob import TextBlob
import nltk

from .utils import (
    setup_logging, create_directories, load_data, save_data,
    find_common_dates, error_handler, timed, run_with_timeout
)  

from .config import load_config

class CoreAnalyzer:
    """
    Base analyzer class that provides shared functionality for all analyzers.
    
    This class handles:
    - Configuration loading
    - Logging setup
    - Directory creation
    - Basic statistical analysis
    - Common visualization generation
    """
    
    def __init__(self, config_path: str = 'config/analysis_config.json', 
                output_dir: str = 'data/analysis'):
        """
        Initialize the analyzer with configuration and output settings.
        
        Args:
            config_path: Path to the configuration file
            output_dir: Directory for saving analysis results
        """
        # Load configuration
        self.config = load_config(config_path)
        self.config_path = config_path
        
        # Set up logging
        log_file = f"data/logs/analysis_{datetime.now().strftime('%Y%m%d')}.log"
        self.logger = setup_logging(log_file)
        self.logger.info(f"Initializing {self.__class__.__name__}")
        
        # Set up output directories
        self.output_dir = output_dir
        self.figure_dir = f"{output_dir}/figures"
        create_directories([output_dir, self.figure_dir])
        
        # Set up visualization settings from config or defaults
        self._setup_visualization_settings()
        
        # Initialize data containers
        self.data = {}
        self.analysis_results = {}
    
    def _setup_visualization_settings(self):
        """Initialize visualization settings from config or defaults"""
        if self.config and 'visualization' in self.config and 'basic' in self.config['visualization']:
            viz_config = self.config['visualization']['basic']
            
            # Colors setup
            if 'colors' in viz_config and viz_config['colors']:
                self.colors = viz_config['colors']
            else:
                self.colors = sns.color_palette("husl", 8)
            
            # Figure size setup
            if 'figure_size' in viz_config and viz_config['figure_size']:
                self.figure_size = tuple(viz_config['figure_size'])
            else:
                self.figure_size = (12, 8)
            
            # DPI setup
            if 'dpi' in viz_config:
                plt.rcParams['figure.dpi'] = viz_config['dpi']
            else:
                plt.rcParams['figure.dpi'] = 300
        else:
            # Default visualization settings
            plt.style.use('default')
            self.colors = sns.color_palette("husl", 8)
            self.figure_size = (12, 8)
            plt.rcParams['figure.dpi'] = 300
    
    def is_feature_enabled(self, feature_path: str, default: bool = False) -> bool:
        """
        Check if a feature is enabled in the configuration.
        
        Args:
            feature_path: Dot-separated path to the feature's enabled flag
            default: Default value if the config key is not found
            
        Returns:
            Boolean indicating if the feature is enabled
        """
        keys = feature_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
                
        return bool(value)
    
    def analyze_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform basic statistical analysis on a DataFrame.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary containing statistical results
        """
        self.logger.info("Performing statistical analysis")
        
        # Basic record info
        results = {
            'record_count': len(df),
            'column_count': len(df.columns),
            'missing_values': df.isnull().sum().to_dict(),
        }
        
        # Analyze numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            results['numeric_columns'] = {}
            
            for col in numeric_columns:
                results['numeric_columns'][col] = {
                    'mean': df[col].mean(),
                    'median': df[col].median(),
                    'std': df[col].std(),
                    'min': df[col].min(),
                    'max': df[col].max()
                }
        
        # Analyze categorical columns
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_columns) > 0:
            results['categorical_columns'] = {}
            
            for col in categorical_columns:
                value_counts = df[col].value_counts()
                if len(value_counts) <= 10:  # Only include full counts if small number of categories
                    results['categorical_columns'][col] = {
                        'unique_values': len(value_counts),
                        'top_values': value_counts.to_dict(),
                        'missing_values': df[col].isnull().sum()
                    }
                else:
                    results['categorical_columns'][col] = {
                        'unique_values': len(value_counts),
                        'top_values': value_counts.head(5).to_dict(),  # Only top 5 categories
                        'missing_values': df[col].isnull().sum()
                    }
          
        # Analyze datetime columns
        datetime_columns = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]
        if datetime_columns:
            results['datetime_columns'] = {}
            
            for col in datetime_columns:
                results['datetime_columns'][col] = {
                    'min': df[col].min().isoformat() if not pd.isna(df[col].min()) else None,
                    'max': df[col].max().isoformat() if not pd.isna(df[col].max()) else None,
                    'range_days': (df[col].max() - df[col].min()).days if not pd.isna(df[col].min()) and not pd.isna(df[col].max()) else None
                }
        
        return results
    
    def create_basic_visualizations(self, source: str) -> None:
        """Create basic visualizations for a data source."""
        self.logger.info(f"Creating basic visualizations for {source}")
        
        try:
            df = self.load_data(source)
            
            # Create output directory if it doesn't exist
            source_dir = os.path.join(self.output_dir, source)
            create_directories([source_dir])
            
            # 1. Missing values heatmap
            plt.figure(figsize=self.figure_size)
            sns.heatmap(df.isnull(), cbar=False, cmap='viridis')
            plt.title(f'Missing Values in {source.capitalize()} Data')
            plt.tight_layout()
            plt.savefig(os.path.join(source_dir, "missing_values.png"))
            plt.close()
            
            # 2. Distribution plots for numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            for i, col in enumerate(numeric_cols[:5]):  # Limit to first 5 columns
                plt.figure(figsize=(10, 6))
                sns.histplot(df[col].dropna(), kde=True)
                plt.title(f'Distribution of {col} in {source.capitalize()} Data')
                plt.tight_layout()
                plt.savefig(os.path.join(source_dir, f"distribution_{col}.png"))
                plt.close()
            
            # 3. Correlation matrix for numeric columns
            if len(numeric_cols) > 1:
                plt.figure(figsize=self.figure_size)
                corr_matrix = df[numeric_cols].corr()
                sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f')
                plt.title(f'Correlation Matrix for {source.capitalize()} Data')
                plt.tight_layout()
                plt.savefig(os.path.join(source_dir, "correlation_matrix.png"))
                plt.close()
            
            # 4. Price trend for market data
            if source == 'market' and 'price' in df.columns:
                plt.figure(figsize=self.figure_size)
                plt.plot(df['date'], df['price'])
                plt.title(f'{source.capitalize()} Price Trend')
                plt.xlabel('Date')
                plt.ylabel('Price')
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.savefig(os.path.join(source_dir, "price_trend.png"))
                plt.close()
                
        except Exception as e:
            self.logger.error(f"Error creating visualizations for {source}: {e}")
            raise
    
    def create_time_series_viz(self, df: pd.DataFrame, date_col: str, value_col: str) -> None:
        """Create a time series visualization."""
        if date_col not in df.columns or value_col not in df.columns:
            self.logger.warning(f"Required columns not found in DataFrame")
            return
        
        try:
            # Convert to datetime if not already
            date_series = pd.to_datetime(df[date_col])
            
            # Create the plot
            plt.figure(figsize=self.figure_size)
            plt.plot(date_series, df[value_col])
            plt.title(f'{value_col} Over Time')
            plt.xlabel('Date')
            plt.ylabel(value_col)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Save the plot
            output_path = f"{self.figure_dir}/{value_col.lower()}_time_series.png"
            plt.savefig(output_path)
            plt.close()
            
            self.logger.info(f"Created time series visualization: {output_path}")
        except Exception as e:
            self.logger.error(f"Error creating time series visualization: {e}")


class UnifiedAnalyzer(CoreAnalyzer):
    """Unified analyzer class that handles all types of data sources."""
    
    def __init__(self, config_path: str = 'config/analysis_config.json', 
                output_dir: str = 'data/analysis'):
        """Initialize the UnifiedAnalyzer."""
        super().__init__(config_path, output_dir)
        self._setup_nltk_resources()
        self.test_dir = "test_output"  # Directory for test data
    
    def _setup_nltk_resources(self):
        """Download required NLTK resources."""
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            nltk.download('maxent_ne_chunker', quiet=True)
            nltk.download('words', quiet=True)
        except Exception as e:
            self.logger.warning(f"Error downloading NLTK resources: {e}")
    
    def load_data(self, source: str) -> pd.DataFrame:
        """Load data from a specific source."""
        valid_sources = ['market', 'news', 'reddit']
        if source not in valid_sources:
            raise ValueError(f"Invalid data source: {source}")
        
        try:
            # Load data from test directory
            file_path = os.path.join(self.test_dir, f"{source}_data.csv")
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"No data file found for {source}")
            
            df = pd.read_csv(file_path)
            self.logger.info(f"Loaded {source} data from {file_path}")
            
            return df
        except Exception as e:
            self.logger.error(f"Error loading {source} data: {e}")
            raise
    
    def analyze_statistics(self, source: str) -> Dict[str, Any]:
        """Analyze statistics for a specific data source."""
        try:
            df = self.load_data(source)
            stats = {}
            
            # Analyze numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                stats[col] = {
                    'mean': float(df[col].mean()),
                    'std': float(df[col].std()),
                    'min': float(df[col].min()),
                    'max': float(df[col].max())
                }
            
            # Analyze categorical columns
            cat_cols = df.select_dtypes(include=['object']).columns
            for col in cat_cols:
                value_counts = df[col].value_counts()
                stats[col] = value_counts.to_dict()
            
            return stats
        except Exception as e:
            self.logger.error(f"Error analyzing {source} statistics: {e}")
            return {}
    
    def create_time_series_viz(self, source: str, column: str) -> None:
        """Create a time series visualization for a specific data source and column."""
        try:
            df = self.load_data(source)
            if column not in df.columns:
                raise ValueError(f"Column {column} not found in {source} data")
            
            plt.figure(figsize=self.figure_size)
            plt.plot(pd.to_datetime(df['date']), df[column])
            plt.title(f'{source.capitalize()} {column} Time Series')
            plt.xlabel('Date')
            plt.ylabel(column)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            output_path = os.path.join(self.output_dir, f"{source}_{column}_time_series.png")
            plt.savefig(output_path)
            plt.close()
            
            self.logger.info(f"Created time series visualization: {output_path}")
        except Exception as e:
            self.logger.error(f"Error creating time series visualization: {e}")
    
    def analyze_all(self) -> Dict[str, Any]:
        """Analyze all data sources."""
        results = {}
        sources = ['market', 'news', 'reddit']
        
        for source in sources:
            try:
                results[source] = self.analyze_statistics(source)
                self.create_basic_visualizations(source)
            except Exception as e:
                self.logger.error(f"Error analyzing {source}: {e}")
                results[source] = {'error': str(e)}
        
        return results
    
    def save_results(self, results: Dict[str, Any], output_path: Optional[str] = None, format: str = 'json') -> str:
        """Save analysis results."""
        if format not in ['json', 'csv']:
            raise ValueError("Invalid format. Must be 'json' or 'csv'")
        
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(self.output_dir, f"analysis_results_{timestamp}.{format}")
        
        try:
            if format == 'json':
                with open(output_path, 'w') as f:
                    json.dump(results, f, indent=2)
            else:  # CSV format
                # Convert the nested dictionary to a DataFrame
                rows = []
                for source, stats in results.items():
                    for key, value in stats.items():
                        if isinstance(value, dict):
                            for subkey, subvalue in value.items():
                                rows.append({
                                    'source': source,
                                    'metric': key,
                                    'submetric': subkey,
                                    'value': subvalue
                                })
                        else:
                            rows.append({
                                'source': source,
                                'metric': key,
                                'value': value
                            })
                
                pd.DataFrame(rows).to_csv(output_path, index=False)
            
            self.logger.info(f"Saved analysis results to {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"Error saving results: {e}")
            raise


def main():
    """Main function to demonstrate usage"""
    analyzer = UnifiedAnalyzer()
    
    # Load data from all sources
    analyzer.load_data()
    
    # Perform analysis
    results = analyzer.analyze_all()
    
    # Create visualizations
    analyzer.create_basic_visualizations()
    
    # Save results
    output_file = analyzer.save_results(results)
    print(f"Analysis complete. Results saved to {output_file}")


if __name__ == "__main__":
    main() 