"""
Analysis Utilities - Core functions for data loading, saving, and common operations.
"""

import os
import sys
import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime
from glob import glob
from typing import Dict, List, Any, Optional, Union, Callable
import functools
import traceback
import time
import threading
from pathlib import Path

# ----------------------
# Logging and Directories
# ----------------------

def setup_logging(log_file: Optional[str] = None, level: int = logging.INFO, logger_name: str = 'analysis') -> logging.Logger:
    """
    Set up logging with a consistent format.
    
    Args:
        log_file: Path to log file (if None, logs to console only)
        level: Logging level (default: INFO)
        logger_name: Name of the logger
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    
    # Clear existing handlers
    logger.handlers = []
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if log_file is specified
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def create_directories(directories: List[str]) -> None:
    """
    Create multiple directories if they don't exist.
    
    Args:
        directories: List of directory paths to create
    """
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

def get_timestamp() -> str:
    """
    Get current timestamp in a format suitable for filenames.
    
    Returns:
        Formatted timestamp string
    """
    return datetime.now().strftime('%Y%m%d_%H%M%S')

# ----------------------
# Configuration Handling
# ----------------------

_config_cache = {}

def load_configuration(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a JSON file with caching.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Configuration as a dictionary, or empty dict if file not found
    """
    global _config_cache
    
    # Return cached config if available
    if config_path in _config_cache:
        return _config_cache[config_path]
    
    # Try to load the configuration file
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        _config_cache[config_path] = config
        return config
    except FileNotFoundError:
        logging.warning(f"Configuration file not found: {config_path}")
        return {}
    except json.JSONDecodeError:
        logging.error(f"Error parsing configuration file: {config_path}")
        return {}

def get_config_value(config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Safely get a nested configuration value using a dot-separated path.
    
    Args:
        config: Configuration dictionary
        key_path: Dot-separated path to the desired value (e.g., "data_sources.reddit.enabled")
        default: Default value to return if the key doesn't exist
        
    Returns:
        Value from the configuration or the default value
    """
    if not config:
        return default
        
    keys = key_path.split('.')
    result = config
    
    for key in keys:
        if isinstance(result, dict) and key in result:
            result = result[key]
        else:
            return default
            
    return result

# ----------------------
# Data Loading and Saving
# ----------------------

def load_data(file_path: str, **kwargs) -> pd.DataFrame:
    """
    Load data from a file into a pandas DataFrame.
    
    Args:
        file_path: Path to the data file
        **kwargs: Additional arguments to pass to pandas read functions
        
    Returns:
        Loaded DataFrame
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file format is not supported
    """
    logger = logging.getLogger('analysis')
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if file_ext == '.csv':
            return pd.read_csv(file_path, **kwargs)
        elif file_ext in ['.xls', '.xlsx']:
            return pd.read_excel(file_path, **kwargs)
        elif file_ext == '.json':
            return pd.read_json(file_path, **kwargs)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        raise

def save_data(df: pd.DataFrame, output_path: str, **kwargs) -> None:
    """
    Save a DataFrame to a file.
    
    Args:
        df: DataFrame to save
        output_path: Path to save the file
        **kwargs: Additional arguments to pass to pandas write functions
    """
    logger = logging.getLogger('analysis')
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    file_ext = os.path.splitext(output_path)[1].lower()
    
    try:
        if file_ext == '.csv':
            df.to_csv(output_path, **kwargs)
        elif file_ext in ['.xls', '.xlsx']:
            df.to_excel(output_path, **kwargs)
        elif file_ext == '.json':
            df.to_json(output_path, **kwargs)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
            
        logger.info(f"Data saved to {output_path}")
    except Exception as e:
        logger.error(f"Error saving data to {output_path}: {e}")
        raise

def merge_dataframes_by_date(df1: pd.DataFrame, df2: pd.DataFrame, 
                           date_col1: str = 'date', date_col2: str = 'date',
                           how: str = 'inner') -> pd.DataFrame:
    """
    Merge two DataFrames based on date columns.
    
    Args:
        df1: First DataFrame
        df2: Second DataFrame
        date_col1: Date column name in first DataFrame
        date_col2: Date column name in second DataFrame
        how: Type of merge to perform ('inner', 'outer', 'left', 'right')
        
    Returns:
        Merged DataFrame
    """
    logger = logging.getLogger('analysis')
    
    try:
        # Convert date columns to datetime if they aren't already
        for df, col in [(df1, date_col1), (df2, date_col2)]:
            if not pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = pd.to_datetime(df[col])
        
        # Perform the merge
        merged_df = pd.merge(df1, df2, left_on=date_col1, right_on=date_col2, how=how)
        logger.info(f"Successfully merged DataFrames with {len(merged_df)} rows")
        
        return merged_df
    except Exception as e:
        logger.error(f"Error merging DataFrames: {e}")
        raise

def find_common_dates(df1: pd.DataFrame, df2: pd.DataFrame, 
                     date_col1: str = 'date', date_col2: str = 'date') -> List[Any]:
    """
    Find common dates between two DataFrames.
    
    Args:
        df1: First DataFrame
        df2: Second DataFrame
        date_col1: Date column name in first DataFrame
        date_col2: Date column name in second DataFrame
        
    Returns:
        List of common dates
    """
    logger = logging.getLogger('analysis')
    
    try:
        # Convert date columns to datetime if they aren't already
        for df, col in [(df1, date_col1), (df2, date_col2)]:
            if not pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = pd.to_datetime(df[col])
        
        # Find common dates
        dates1 = set(df1[date_col1])
        dates2 = set(df2[date_col2])
        common_dates = sorted(list(dates1.intersection(dates2)))
        
        logger.info(f"Found {len(common_dates)} common dates")
        return common_dates
    except Exception as e:
        logger.error(f"Error finding common dates: {e}")
        raise

# ----------------------
# Error Handling
# ----------------------

def error_handler(func: Callable) -> Callable:
    """
    Decorator for handling errors in functions.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger('analysis')
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            logger.debug(f"Traceback: {traceback.format_exc()}")
            raise
    return wrapper

# ----------------------
# Data Processing
# ----------------------

def extract_time_series(df: pd.DataFrame, date_col: str, 
                       value_col: Optional[str] = None, 
                       group_col: Optional[str] = None) -> pd.DataFrame:
    """
    Extract time series data from a DataFrame.
    
    Args:
        df: Source DataFrame
        date_col: Column containing dates
        value_col: Column containing values (if None, counts occurrences)
        group_col: Column to group by (optional)
        
    Returns:
        DataFrame with time series data
    """
    if date_col not in df.columns:
        raise ValueError(f"Date column '{date_col}' not found in DataFrame")
    
    # Convert to datetime if not already
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df = df.copy()
        df['date'] = pd.to_datetime(df[date_col])
    else:
        df = df.copy()
        df['date'] = df[date_col]
    
    # Extract just the date part (no time)
    df['date'] = df['date'].dt.date
    
    # Group by date (and optionally by group_col)
    if group_col:
        if group_col not in df.columns:
            raise ValueError(f"Group column '{group_col}' not found in DataFrame")
        
        if value_col:
            if value_col not in df.columns:
                raise ValueError(f"Value column '{value_col}' not found in DataFrame")
            
            # Group by date and group_col, calculate mean of value_col
            result = df.groupby(['date', group_col])[value_col].mean().reset_index()
        else:
            # Group by date and group_col, count occurrences
            result = df.groupby(['date', group_col]).size().reset_index(name='count')
    else:
        if value_col:
            if value_col not in df.columns:
                raise ValueError(f"Value column '{value_col}' not found in DataFrame")
            
            # Group by date, calculate mean of value_col
            result = df.groupby('date')[value_col].mean().reset_index()
        else:
            # Group by date, count occurrences
            result = df.groupby('date').size().reset_index(name='count')
    
    return result

@error_handler
def combine_datasets(dataframes: Dict[str, pd.DataFrame], common_key: str) -> pd.DataFrame:
    """
    Combine multiple DataFrames on a common key.
    
    Args:
        dataframes: Dictionary of DataFrames to combine
        common_key: Column name to join on
        
    Returns:
        Combined DataFrame
    """
    if not dataframes:
        return pd.DataFrame()
    
    # Start with first DataFrame
    sources = list(dataframes.keys())
    result = dataframes[sources[0]].copy()
    
    # Add a source column
    result['source'] = sources[0]
    
    # Combine with other DataFrames
    for source in sources[1:]:
        df = dataframes[source].copy()
        df['source'] = source
        
        # Check if common_key exists in both DataFrames
        if common_key not in result.columns or common_key not in df.columns:
            logging.warning(f"Common key '{common_key}' not found in {source} DataFrame")
            continue
        
        # Append rows
        result = pd.concat([result, df], ignore_index=True)
    
    return result

@error_handler
def get_file_stats(directory: str, file_extension: Optional[str] = None) -> Dict[str, Any]:
    """
    Get statistics for files in a directory.
    
    Args:
        directory: Directory to analyze
        file_extension: Filter by file extension (e.g., ".csv")
        
    Returns:
        Dictionary with file statistics
    """
    if not os.path.exists(directory):
        return {'error': f"Directory not found: {directory}"}
    
    # Get list of files
    if file_extension:
        files = glob.glob(os.path.join(directory, f"*{file_extension}"))
    else:
        files = glob.glob(os.path.join(directory, "*"))
        # Filter out directories
        files = [f for f in files if os.path.isfile(f)]
    
    if not files:
        return {
            'file_count': 0,
            'total_size': 0,
            'oldest_file': None,
            'newest_file': None
        }
    
    # Calculate statistics
    total_size = sum(os.path.getsize(f) for f in files)
    file_times = [(f, os.path.getmtime(f)) for f in files]
    oldest_file = min(file_times, key=lambda x: x[1])
    newest_file = max(file_times, key=lambda x: x[1])
    
    # Format timestamps
    oldest_timestamp = datetime.fromtimestamp(oldest_file[1]).strftime('%Y-%m-%d %H:%M:%S')
    newest_timestamp = datetime.fromtimestamp(newest_file[1]).strftime('%Y-%m-%d %H:%M:%S')
    
    return {
        'file_count': len(files),
        'total_size': total_size,
        'average_size': total_size / len(files),
        'oldest_file': {
            'path': oldest_file[0],
            'timestamp': oldest_timestamp
        },
        'newest_file': {
            'path': newest_file[0],
            'timestamp': newest_timestamp
        }
    }

def generate_summary_text(analysis_results: Dict[str, Any]) -> str:
    """
    Generate a human-readable summary of the analysis results.
    
    Args:
        analysis_results: Analysis results
        
    Returns:
        Text summary
    """
    summary = []
    
    # Add header
    summary.append("# Data Analysis Summary")
    summary.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary.append("")
    
    # Add metadata
    if 'metadata' in analysis_results:
        metadata = analysis_results['metadata']
        summary.append("## Analysis Metadata")
        if 'timestamp' in metadata:
            summary.append(f"* Analysis timestamp: {metadata['timestamp']}")
        if 'sources_analyzed' in metadata:
            summary.append(f"* Sources analyzed: {', '.join(metadata['sources_analyzed'])}")
        summary.append("")
    
    # Add statistical analysis
    if 'statistical_analysis' in analysis_results:
        stats = analysis_results['statistical_analysis']
        summary.append("## Statistical Analysis")
        
        for source, source_stats in stats.items():
            summary.append(f"### {source.capitalize()} Statistics")
            if 'record_count' in source_stats:
                summary.append(f"* Records: {source_stats['record_count']}")
            if 'column_count' in source_stats:
                summary.append(f"* Columns: {source_stats['column_count']}")
            summary.append("")
    
    # Add source-specific analysis
    for source in ['reddit', 'news', 'market']:
        section_key = f"{source}_analysis"
        if section_key in analysis_results:
            source_analysis = analysis_results[section_key]
            summary.append(f"## {source.capitalize()} Analysis")
            
            # Add common statistics
            if 'record_count' in source_analysis:
                summary.append(f"* Records: {source_analysis['record_count']}")
            
            # Source-specific sections
            if source == 'reddit' and 'subreddit_distribution' in source_analysis:
                summary.append("### Subreddit Distribution")
                for subreddit, count in source_analysis['subreddit_distribution'].items():
                    summary.append(f"* {subreddit}: {count}")
            
            if source == 'market' and 'symbol_analysis' in source_analysis:
                summary.append("### Stock Performance")
                for symbol, data in source_analysis['symbol_analysis'].items():
                    summary.append(f"#### {symbol}")
                    if 'price_metrics' in data:
                        metrics = data['price_metrics']
                        if 'avg_close' in metrics:
                            summary.append(f"* Average Close: ${metrics['avg_close']:.2f}")
                        if 'min_price' in metrics and 'max_price' in metrics:
                            summary.append(f"* Price Range: ${metrics['min_price']:.2f} - ${metrics['max_price']:.2f}")
            
            # Add sentiment analysis if present
            if 'sentiment_analysis' in source_analysis:
                sentiment = source_analysis['sentiment_analysis']
                summary.append("### Sentiment Analysis")
                if 'average_sentiment' in sentiment:
                    avg = sentiment['average_sentiment']
                    summary.append(f"* Average Polarity: {avg['polarity']:.2f}")
                    summary.append(f"* Average Subjectivity: {avg['subjectivity']:.2f}")
                if 'sentiment_distribution' in sentiment:
                    dist = sentiment['sentiment_distribution']
                    summary.append(f"* Positive: {dist['positive']}")
                    summary.append(f"* Neutral: {dist['neutral']}")
                    summary.append(f"* Negative: {dist['negative']}")
            
            summary.append("")
    
    # Add cross-source analysis if present
    if 'cross_source_analysis' in analysis_results:
        cross_analysis = analysis_results['cross_source_analysis']
        summary.append("## Cross-Source Analysis")
        
        if 'market_correlations' in cross_analysis:
            corr = cross_analysis['market_correlations']
            summary.append("### Market Correlations")
            
            if 'news_market_correlation' in corr:
                news_corr = corr['news_market_correlation']
                summary.append(f"* News-Market Correlation: {news_corr['correlation']:.2f}")
                summary.append(f"* Based on {news_corr['date_count']} days of data")
            
            summary.append("")
    
    # Join and return
    return "\n".join(summary)

# ----------------------
# Performance Utilities
# ----------------------

def timed(func: Callable) -> Callable:
    """
    Decorator for timing function execution.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        logger = logging.getLogger('analysis')
        logger.info(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        
        return result
    return wrapper

def run_with_timeout(func: Callable, args=(), kwargs={}, timeout_sec: int = 60) -> Any:
    """
    Run a function with a timeout.
    
    Args:
        func: Function to run
        args: Function arguments
        kwargs: Function keyword arguments
        timeout_sec: Timeout in seconds
        
    Returns:
        Function result
        
    Raises:
        TimeoutError: If the function doesn't complete within the timeout
    """
    result = None
    error = None
    
    def target():
        nonlocal result, error
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            error = e
    
    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout_sec)
    
    if thread.is_alive():
        thread.join()  # Ensure the thread is properly cleaned up
        raise TimeoutError(f"Function {func.__name__} timed out after {timeout_sec} seconds")
    
    if error:
        raise error
        
    return result 