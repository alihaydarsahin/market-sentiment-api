import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os
from datetime import datetime, timedelta
import logging
from sklearn.impute import KNNImputer

class TrendPredictor:
    def __init__(self):
        self.model_dir = 'models'
        os.makedirs(self.model_dir, exist_ok=True)
        
        self.scaler = StandardScaler()
        self.imputer = KNNImputer(n_neighbors=3)
        
        # Use more robust model
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=3,
            random_state=42,
            validation_fraction=0.2,
            n_iter_no_change=5,
            tol=1e-4
        )
        
        self.logger = logging.getLogger(__name__)
    
    def prepare_features(self, data):
        """Prepare features with improved handling of sparse data"""
        try:
            features = pd.DataFrame(index=data.index)
            
            # Add sentiment features with rolling statistics
            for col in ['reddit_sentiment', 'news_sentiment']:
                if col in data.columns:
                    features[col] = data[col]
                    features[f'{col}_ma3'] = data[col].rolling(window=3, min_periods=1).mean()
                    features[f'{col}_ma7'] = data[col].rolling(window=7, min_periods=3).mean()
                    features[f'{col}_std7'] = data[col].rolling(window=7, min_periods=3).std()
            
            # Add market features with more sophisticated indicators
            if 'market_change' in data.columns:
                features['market_change'] = data['market_change']
                features['market_ma3'] = data['market_change'].rolling(window=3, min_periods=1).mean()
                features['market_ma7'] = data['market_change'].rolling(window=7, min_periods=3).mean()
                features['market_std7'] = data['market_change'].rolling(window=7, min_periods=3).std()
                
                # Add momentum indicators
                features['market_momentum'] = features['market_change'].diff()
                features['market_acceleration'] = features['market_momentum'].diff()
            
            # Handle missing values with KNN imputation
            if features.isnull().any().any():
                self.logger.info("Imputing missing values with KNN")
                features = pd.DataFrame(
                    self.imputer.fit_transform(features),
                    index=features.index,
                    columns=features.columns
                )
            
            return features
            
        except Exception as e:
            self.logger.error(f"Error preparing features: {e}")
            return None
    
    def train(self, data, target_col='market_change', forecast_days=7):
        """Train the model"""
        try:
            # Prepare features
            features = self.prepare_features(data)
            
            # Prepare target
            y = features[target_col].shift(-forecast_days)  # Future values
            features = features.drop(target_col, axis=1)
            
            # Remove NaN values
            mask = ~y.isna()
            X = features[mask]
            y = y[mask]
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model.fit(X_scaled, y)
            
            # Save model
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            model_path = f"{self.model_dir}/trend_predictor_{timestamp}.joblib"
            scaler_path = f"{self.model_dir}/scaler_{timestamp}.joblib"
            
            joblib.dump(self.model, model_path)
            joblib.dump(self.scaler, scaler_path)
            
            self.logger.info(f"Model saved to {model_path}")
            
            # Calculate metrics
            y_pred = self.model.predict(X_scaled)
            r2 = r2_score(y, y_pred)
            rmse = np.sqrt(mean_squared_error(y, y_pred))
            
            self.logger.info(f"Model Performance - R2: {r2:.4f}, RMSE: {rmse:.4f}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error training model: {e}")
            return False
    
    def predict(self, data):
        """Make predictions"""
        try:
            features = self.prepare_features(data)
            features_scaled = self.scaler.transform(features)
            predictions = self.model.predict(features_scaled)
            
            return pd.Series(predictions, index=features.index)
            
        except Exception as e:
            self.logger.error(f"Error making predictions: {e}")
            return None

def main():
    # Test the model
    predictor = TrendPredictor()
    
    # Find latest combined data
    data_dir = 'data/processed'
    data_files = [f for f in os.listdir(data_dir) if f.startswith('combined_data_')]
    if not data_files:
        print("No data files found!")
        return
    
    latest_file = sorted(data_files)[-1]
    data_path = os.path.join(data_dir, latest_file)
    
    # Train model
    print("Training model...")
    success = predictor.train(data_path)
    
    if success:
        # Get feature importance
        importance = predictor.get_feature_importance()
        print("\nFeature Importance:")
        print(importance)

if __name__ == "__main__":
    main() 