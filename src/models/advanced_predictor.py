import pandas as pd
import numpy as np
import os
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LassoCV
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_percentage_error
from sklearn.impute import KNNImputer
import joblib
import logging
from datetime import datetime, timedelta

class AdvancedPredictor:
    def __init__(self):
        self.model_dir = 'models'
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Multiple models for ensemble
        self.models = {
            'gbm': GradientBoostingRegressor(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=4,
                subsample=0.8,
                random_state=42
            ),
            'rf': RandomForestRegressor(
                n_estimators=200,
                max_depth=10,
                min_samples_leaf=4,
                random_state=42
            ),
            'nn': MLPRegressor(
                hidden_layer_sizes=(100, 50),
                max_iter=1000,
                early_stopping=True,
                random_state=42
            ),
            'lasso': LassoCV(
                cv=5,
                random_state=42
            )
        }
        
        self.scaler = RobustScaler()  # More robust to outliers
        self.imputer = KNNImputer(n_neighbors=5)
        self.logger = logging.getLogger(__name__)
        
    def create_advanced_features(self, data):
        """Create advanced features for prediction"""
        features = pd.DataFrame(index=data.index)
        
        # Sentiment features
        for col in ['reddit_sentiment', 'news_sentiment']:
            if col in data.columns:
                # Basic features
                features[col] = data[col]
                
                # Rolling statistics
                for window in [3, 7, 14]:
                    features[f'{col}_ma{window}'] = data[col].rolling(window=window, min_periods=1).mean()
                    features[f'{col}_std{window}'] = data[col].rolling(window=window, min_periods=1).std()
                
                # Rate of change
                features[f'{col}_roc'] = data[col].pct_change()
                
                # Momentum
                features[f'{col}_momentum'] = data[col].diff()
                
                # Volatility
                features[f'{col}_volatility'] = data[col].rolling(window=7).std() / data[col].rolling(window=7).mean()
        
        # Market features
        if 'market_change' in data.columns:
            features['market_change'] = data['market_change']
            
            # Technical indicators
            for window in [3, 7, 14]:
                # Moving averages
                features[f'market_ma{window}'] = data['market_change'].rolling(window=window).mean()
                
                # Bollinger Bands
                ma = data['market_change'].rolling(window=window).mean()
                std = data['market_change'].rolling(window=window).std()
                features[f'market_bb_upper{window}'] = ma + (std * 2)
                features[f'market_bb_lower{window}'] = ma - (std * 2)
                
                # Relative Strength Index (RSI)
                delta = data['market_change'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
                rs = gain / loss
                features[f'market_rsi{window}'] = 100 - (100 / (1 + rs))
        
        # Calendar features
        features['day_of_week'] = pd.to_datetime(data.index).dayofweek
        features['month'] = pd.to_datetime(data.index).month
        features['is_month_end'] = pd.to_datetime(data.index).is_month_end.astype(int)
        
        return features
    
    def train_models(self, data, target_col='market_change', forecast_days=7):
        """Train all models"""
        try:
            # Prepare features
            features = self.create_advanced_features(data)
            
            # Prepare target
            y = features[target_col].shift(-forecast_days)
            X = features.drop(target_col, axis=1)
            
            # Remove NaN values
            mask = ~y.isna()
            X = X[mask]
            y = y[mask]
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Time series cross-validation
            tscv = TimeSeriesSplit(n_splits=5)
            model_scores = {}
            
            for name, model in self.models.items():
                scores = []
                predictions = []
                
                for train_idx, val_idx in tscv.split(X_scaled):
                    X_train, X_val = X_scaled[train_idx], X_scaled[val_idx]
                    y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
                    
                    model.fit(X_train, y_train)
                    pred = model.predict(X_val)
                    predictions.extend(pred)
                    
                    # Calculate metrics
                    mse = mean_squared_error(y_val, pred)
                    r2 = r2_score(y_val, pred)
                    mape = mean_absolute_percentage_error(y_val, pred)
                    
                    scores.append({
                        'mse': mse,
                        'rmse': np.sqrt(mse),
                        'r2': r2,
                        'mape': mape
                    })
                
                # Average scores
                model_scores[name] = {
                    metric: np.mean([s[metric] for s in scores])
                    for metric in scores[0].keys()
                }
                
                # Save model
                timestamp = datetime.now().strftime('%Y%m%d_%H%M')
                model_path = f"{self.model_dir}/{name}_model_{timestamp}.joblib"
                joblib.dump(model, model_path)
                
                self.logger.info(f"{name} model performance:")
                for metric, value in model_scores[name].items():
                    self.logger.info(f"- {metric}: {value:.4f}")
            
            # Save scaler
            scaler_path = f"{self.model_dir}/scaler_{timestamp}.joblib"
            joblib.dump(self.scaler, scaler_path)
            
            return model_scores
            
        except Exception as e:
            self.logger.error(f"Error training models: {e}")
            return None
    
    def ensemble_predict(self, data):
        """Make predictions using all models"""
        try:
            features = self.create_advanced_features(data)
            features_scaled = self.scaler.transform(features.drop('market_change', axis=1))
            
            predictions = {}
            for name, model in self.models.items():
                pred = model.predict(features_scaled)
                predictions[name] = pred
            
            # Ensemble prediction (weighted average based on R2 scores)
            weights = {name: model.score(features_scaled, data['market_change']) 
                      for name, model in self.models.items()}
            total_weight = sum(weights.values())
            weights = {k: v/total_weight for k, v in weights.items()}
            
            ensemble_pred = sum(pred * weights[name] 
                              for name, pred in predictions.items())
            
            return pd.Series(ensemble_pred, index=features.index)
            
        except Exception as e:
            self.logger.error(f"Error making predictions: {e}")
            return None 