import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta

class DataValidator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def check_data_quality(self, data):
        """Check data quality and return validation results"""
        try:
            results = {
                'is_valid': True,
                'issues': [],
                'stats': {}
            }
            
            # Check if data is empty
            if data.empty:
                results['is_valid'] = False
                results['issues'].append("Data is empty")
                return results
            
            # Check for minimum data points
            if len(data) < 7:  # At least a week of data
                results['is_valid'] = False
                results['issues'].append("Insufficient data points (minimum 7 required)")
            
            # Check for missing values
            missing_pct = data.isnull().mean() * 100
            for col in missing_pct.index:
                if missing_pct[col] > 50:
                    results['issues'].append(f"High missing values in {col}: {missing_pct[col]:.1f}%")
                    results['is_valid'] = False
            
            # Check for data staleness
            latest_date = pd.to_datetime(data.index).max()
            if latest_date < datetime.now() - timedelta(days=7):
                results['issues'].append("Data is more than 7 days old")
                results['is_valid'] = False
            
            # Calculate basic statistics
            results['stats'] = {
                'rows': len(data),
                'columns': len(data.columns),
                'date_range': f"{data.index.min()} to {data.index.max()}",
                'missing_values': missing_pct.to_dict()
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in data validation: {e}")
            return {'is_valid': False, 'issues': [str(e)], 'stats': {}} 