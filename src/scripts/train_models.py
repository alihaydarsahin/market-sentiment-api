import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import joblib
import logging

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self):
        self.models_dir = 'models'
        self.data_dir = 'data/processed'
        os.makedirs(self.models_dir, exist_ok=True)
        
    def load_data(self):
        """Load the latest combined data"""
        try:
            # Find the latest combined data file
            data_files = [f for f in os.listdir(self.data_dir) 
                         if f.startswith('combined_data_')]
            
            if not data_files:
                raise ValueError("No combined data files found")
            
            latest_file = sorted(data_files)[-1]
            file_path = os.path.join(self.data_dir, latest_file)
            
            # Load data
            data = pd.read_csv(file_path)
            logger.info(f"Loaded data from {latest_file}, shape: {data.shape}")
            
            # Set index if 'Unnamed: 0' is date
            if 'Unnamed: 0' in data.columns:
                data['date'] = pd.to_datetime(data['Unnamed: 0'])
                data.set_index('date', inplace=True)
                data.drop('Unnamed: 0', axis=1, errors='ignore', inplace=True)
            
            return data
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return None
    
    def prepare_features(self, data):
        """Prepare features for training"""
        try:
            features = data.copy()
            logger.info("Initial features shape:", features.shape)
            
            # First fill NaN values in original columns
            features.fillna(method='ffill', inplace=True)
            features.fillna(method='bfill', inplace=True)
            
            # Add rolling features for each column
            for col in ['reddit_sentiment', 'news_sentiment', 'market_change']:
                if col in features.columns:
                    logger.info(f"Processing column: {col}")
                    
                    # Moving averages
                    for window in [3, 7, 14]:
                        features[f'{col}_ma{window}'] = features[col].rolling(
                            window=window, 
                            min_periods=1  # Use at least 1 value
                        ).mean()
                        
                        features[f'{col}_std{window}'] = features[col].rolling(
                            window=window, 
                            min_periods=1
                        ).std().fillna(0)  # Fill std NaN with 0
                    
                    # Momentum indicators
                    features[f'{col}_momentum'] = features[col].diff().fillna(0)
                    features[f'{col}_acceleration'] = features[f'{col}_momentum'].diff().fillna(0)
            
            # Fill any remaining NaN values
            features = features.fillna(method='ffill').fillna(method='bfill').fillna(0)
            
            logger.info(f"Final features shape: {features.shape}")
            logger.info(f"Features created: {features.columns.tolist()}")
            logger.info(f"NaN values remaining: {features.isnull().sum().sum()}")
            
            return features
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return None

    def validate_data(self, data):
        """Validate data before training"""
        try:
            logger.info("\nValidating data:")
            logger.info(f"Shape: {data.shape}")
            logger.info(f"Columns: {data.columns.tolist()}")
            logger.info(f"NaN values:\n{data.isnull().sum()}")
            logger.info(f"Data preview:\n{data.head()}")
            
            # Check if we have enough data
            if len(data) < 10:  # Minimum required samples
                raise ValueError(f"Not enough data points: {len(data)} < 10")
            
            # Check required columns
            required_cols = ['reddit_sentiment', 'news_sentiment', 'market_change']
            missing_cols = [col for col in required_cols if col not in data.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            return True
            
        except Exception as e:
            logger.error(f"Data validation error: {e}")
            return False

    def train_models(self):
        """Train and save models"""
        try:
            # Load data
            data = self.load_data()
            if data is None:
                return False
            
            # Validate data
            if not self.validate_data(data):
                return False
            
            # Prepare features
            features = self.prepare_features(data)
            if features is None or 'market_change' not in features.columns:
                raise ValueError("Could not prepare features or target variable missing")
            
            # Split features and target
            X = features.drop('market_change', axis=1)
            y = features['market_change']
            
            # Train-test split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, shuffle=False
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train models with better parameters
            models = {
                'rf': RandomForestRegressor(
                    n_estimators=100,
                    max_depth=5,  # Reduced to prevent overfitting
                    min_samples_leaf=3,  # Added to prevent overfitting
                    random_state=42
                ),
                'gbm': GradientBoostingRegressor(
                    n_estimators=100,
                    learning_rate=0.01,  # Reduced to prevent overfitting
                    max_depth=3,  # Reduced to prevent overfitting
                    min_samples_leaf=3,  # Added to prevent overfitting
                    random_state=42
                )
            }
            
            results = {}
            feature_importances = {}
            
            for name, model in models.items():
                # Train
                logger.info(f"\nTraining {name} model...")
                model.fit(X_train_scaled, y_train)
                
                # Evaluate
                train_score = model.score(X_train_scaled, y_train)
                test_score = model.score(X_test_scaled, y_test)
                
                # Get feature importances
                importances = pd.DataFrame({
                    'feature': X.columns,
                    'importance': model.feature_importances_
                }).sort_values('importance', ascending=False)
                
                feature_importances[name] = importances
                
                results[name] = {
                    'train_score': train_score,
                    'test_score': test_score
                }
                
                # Save model
                timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M')
                model_path = os.path.join(self.models_dir, f'{name}_model_{timestamp}.joblib')
                joblib.dump(model, model_path)
                logger.info(f"Saved {name} model to {model_path}")
            
            # Save scaler
            scaler_path = os.path.join(self.models_dir, 'scaler.joblib')
            joblib.dump(scaler, scaler_path)
            logger.info(f"Saved scaler to {scaler_path}")
            
            # Save feature names
            feature_names = {
                'features': X.columns.tolist(),
                'target': 'market_change'
            }
            joblib.dump(feature_names, os.path.join(self.models_dir, 'feature_names.joblib'))
            
            # Print detailed results
            logger.info("\nModel Performance:")
            for name, scores in results.items():
                logger.info(f"\n{name.upper()}:")
                logger.info(f"Train R2: {scores['train_score']:.4f}")
                logger.info(f"Test R2: {scores['test_score']:.4f}")
                
                logger.info(f"\nTop 5 important features for {name}:")
                logger.info(feature_importances[name].head())
            
            return True
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
            return False

if __name__ == '__main__':
    trainer = ModelTrainer()
    success = trainer.train_models()
    
    if success:
        logger.info("\nModel training completed successfully!")
    else:
        logger.error("\nModel training failed!") 