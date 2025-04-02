"""
Test script for the refactored analysis module.
This script verifies the core functionality of the UnifiedAnalyzer class.
"""

import os
import sys
import logging
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any

# Import the analysis module components
from .core import UnifiedAnalyzer
from .config import generate_default_config, save_config
from .utils import setup_logging

class TestUnifiedAnalyzer(unittest.TestCase):
    """Test cases for the UnifiedAnalyzer class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        # Create test directories
        cls.test_dir = "test_output"
        cls.config_dir = os.path.join(cls.test_dir, "config")
        cls.output_dir = os.path.join(cls.test_dir, "output")
        os.makedirs(cls.test_dir, exist_ok=True)
        os.makedirs(cls.config_dir, exist_ok=True)
        os.makedirs(cls.output_dir, exist_ok=True)
        
        # Set up logging
        setup_logging(log_file=os.path.join(cls.test_dir, "test.log"))
        cls.logger = logging.getLogger('analysis.test')
        
        # Generate test configuration
        cls.config_path = os.path.join(cls.config_dir, "test_config.json")
        config = generate_default_config()
        save_config(config, cls.config_path)
        
        # Create test data
        cls._create_test_data()
        
        # Initialize analyzer
        cls.analyzer = UnifiedAnalyzer(
            config_path=cls.config_path,
            output_dir=cls.output_dir
        )
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        import shutil
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
    
    @classmethod
    def _create_test_data(cls):
        """Create test data for analysis."""
        # Create sample market data
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        market_data = pd.DataFrame({
            'date': dates,
            'price': np.random.normal(100, 10, len(dates)),
            'volume': np.random.randint(1000, 10000, len(dates))
        })
        market_data.to_csv(os.path.join(cls.test_dir, "market_data.csv"), index=False)
        
        # Create sample news data
        news_data = pd.DataFrame({
            'date': dates,
            'title': [f"Test News {i}" for i in range(len(dates))],
            'content': [f"Test content for news {i}" for i in range(len(dates))],
            'source': ['Test Source'] * len(dates)
        })
        news_data.to_csv(os.path.join(cls.test_dir, "news_data.csv"), index=False)
        
        # Create sample Reddit data
        reddit_data = pd.DataFrame({
            'date': dates,
            'title': [f"Test Post {i}" for i in range(len(dates))],
            'content': [f"Test content for post {i}" for i in range(len(dates))],
            'score': np.random.randint(0, 100, len(dates))
        })
        reddit_data.to_csv(os.path.join(cls.test_dir, "reddit_data.csv"), index=False)
    
    def test_initialization(self):
        """Test UnifiedAnalyzer initialization."""
        self.assertIsNotNone(self.analyzer)
        self.assertEqual(self.analyzer.output_dir, self.output_dir)
        self.assertTrue(os.path.exists(self.config_path))
    
    def test_load_data(self):
        """Test data loading functionality."""
        # Load market data
        market_data = self.analyzer.load_data("market")
        self.assertIsInstance(market_data, pd.DataFrame)
        self.assertTrue('date' in market_data.columns)
        self.assertTrue('price' in market_data.columns)
        
        # Load news data
        news_data = self.analyzer.load_data("news")
        self.assertIsInstance(news_data, pd.DataFrame)
        self.assertTrue('date' in news_data.columns)
        self.assertTrue('title' in news_data.columns)
        
        # Load Reddit data
        reddit_data = self.analyzer.load_data("reddit")
        self.assertIsInstance(reddit_data, pd.DataFrame)
        self.assertTrue('date' in reddit_data.columns)
        self.assertTrue('title' in reddit_data.columns)
    
    def test_analyze_statistics(self):
        """Test statistical analysis functionality."""
        # Test market statistics
        market_stats = self.analyzer.analyze_statistics("market")
        self.assertIsInstance(market_stats, dict)
        self.assertTrue('price' in market_stats)
        self.assertTrue('volume' in market_stats)
        
        # Test news statistics
        news_stats = self.analyzer.analyze_statistics("news")
        self.assertIsInstance(news_stats, dict)
        self.assertTrue('source' in news_stats)
        
        # Test Reddit statistics
        reddit_stats = self.analyzer.analyze_statistics("reddit")
        self.assertIsInstance(reddit_stats, dict)
        self.assertTrue('score' in reddit_stats)
    
    def test_create_visualizations(self):
        """Test visualization creation."""
        # Test basic visualizations
        self.analyzer.create_basic_visualizations("market")
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "market", "price_trend.png")))
        
        # Test time series visualization
        self.analyzer.create_time_series_viz("market", "price")
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "market_price_time_series.png")))
    
    def test_analyze_all(self):
        """Test comprehensive analysis functionality."""
        results = self.analyzer.analyze_all()
        self.assertIsInstance(results, dict)
        self.assertTrue('market' in results)
        self.assertTrue('news' in results)
        self.assertTrue('reddit' in results)
    
    def test_save_results(self):
        """Test result saving functionality."""
        # Generate some test results
        test_results = {
            'market': {'price': {'mean': 100, 'std': 10}},
            'news': {'source': {'Test Source': 100}},
            'reddit': {'score': {'mean': 50, 'std': 20}}
        }
        
        # Test JSON saving
        json_path = os.path.join(self.output_dir, "test_results.json")
        self.analyzer.save_results(test_results, output_path=json_path, format='json')
        self.assertTrue(os.path.exists(json_path))
        
        # Test CSV saving
        csv_path = os.path.join(self.output_dir, "test_results.csv")
        self.analyzer.save_results(test_results, output_path=csv_path, format='csv')
        self.assertTrue(os.path.exists(csv_path))
    
    def test_error_handling(self):
        """Test error handling functionality."""
        # Test invalid data source
        with self.assertRaises(ValueError):
            self.analyzer.load_data("invalid_source")
        
        # Test invalid output format
        with self.assertRaises(ValueError):
            self.analyzer.save_results({}, format='invalid_format')

def main():
    """Run the test suite."""
    unittest.main(verbosity=2)

if __name__ == "__main__":
    main() 