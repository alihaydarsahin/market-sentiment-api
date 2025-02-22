import pandas_datareader as pdr
import fredapi
import logging

class EconomicDataCollector:
    def __init__(self, fred_api_key):
        self.fred = fredapi.Fred(api_key=fred_api_key)
        self.indicators = {
            'GDP': 'GDP',
            'Inflation': 'CPIAUCSL',
            'Unemployment': 'UNRATE',
            'Consumer_Confidence': 'UMCSENT'
        }
    
    def collect_economic_data(self):
        """Collect major economic indicators"""
        data = {}
        for name, series_id in self.indicators.items():
            try:
                series = self.fred.get_series(series_id)
                data[name] = series
            except Exception as e:
                logger.error(f"Error collecting {name}: {e}")
        
        return data 