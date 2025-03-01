import os
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
from colorama import init, Fore, Style
import time
import joblib
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from datetime import datetime

init()  # Initialize colorama

class ResultViewer:
    def __init__(self):
        self.figures_dir = 'data/analysis/figures'
        self.processed_dir = 'data/processed'
        self.models_dir = 'models'
        
    def print_header(self, text):
        """Print colorful header"""
        print(f"\n{Fore.CYAN}{'='*50}")
        print(f"{Fore.YELLOW}{text:^50}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    
    def show_latest_visualizations(self):
        """Display the latest visualization results"""
        self.print_header("Latest Visualizations")
        
        files = [f for f in os.listdir(self.figures_dir) if f.endswith('.png')]
        if not files:
            print(f"{Fore.RED}No visualizations found!{Style.RESET_ALL}")
            return
            
        for i, file in enumerate(files, 1):
            print(f"\n{Fore.GREEN}[{i}] {file}{Style.RESET_ALL}")
            img_path = os.path.join(self.figures_dir, file)
            print(f"{Fore.BLUE}Location: {img_path}{Style.RESET_ALL}")
            
            # Add option to open image
            choice = input(f"\n{Fore.YELLOW}Would you like to open this image? (y/n): {Style.RESET_ALL}")
            if choice.lower() == 'y':
                try:
                    img = Image.open(img_path)
                    img.show()
                    time.sleep(1)  # Give time for image to open
                except Exception as e:
                    print(f"{Fore.RED}Error opening image: {e}{Style.RESET_ALL}")
    
    def show_latest_data(self):
        """Show latest processed data summary"""
        self.print_header("Latest Processed Data")
        
        data_files = [f for f in os.listdir(self.processed_dir) 
                     if f.startswith('combined_data_')]
        
        if not data_files:
            print(f"{Fore.RED}No data files found!{Style.RESET_ALL}")
            return
            
        latest_file = sorted(data_files)[-1]
        data_path = os.path.join(self.processed_dir, latest_file)
        
        try:
            df = pd.read_csv(data_path)
            
            print(f"\n{Fore.GREEN}File: {latest_file}{Style.RESET_ALL}")
            print(f"\n{Fore.YELLOW}Shape:{Style.RESET_ALL} {df.shape}")
            
            print(f"\n{Fore.YELLOW}Columns:{Style.RESET_ALL}")
            for col in df.columns:
                print(f"- {col}")
            
            print(f"\n{Fore.YELLOW}First few rows:{Style.RESET_ALL}")
            print(df.head().to_string())
            
            print(f"\n{Fore.YELLOW}Basic statistics:{Style.RESET_ALL}")
            print(df.describe().to_string())
            
        except Exception as e:
            print(f"{Fore.RED}Error reading data: {e}{Style.RESET_ALL}")
    
    def load_data(self):
        """Load the latest processed data for model evaluation"""
        try:
            data_files = [f for f in os.listdir(self.processed_dir) 
                         if f.startswith('processed_data_')]
            
            if not data_files:
                print(f"{Fore.RED}No processed data files found!{Style.RESET_ALL}")
                return None
                
            latest_file = max(data_files, key=lambda x: x.split('_')[-1].replace('.csv', ''))
            data_path = os.path.join(self.processed_dir, latest_file)
            
            return pd.read_csv(data_path)
            
        except Exception as e:
            print(f"{Fore.RED}Error loading data: {e}{Style.RESET_ALL}")
            return None

    def show_model_performance(self):
        """Show model performance metrics with detailed evaluation"""
        self.print_header("Model Performance Analysis")
        
        try:
            # Find available models
            model_files = [f for f in os.listdir(self.models_dir) 
                          if f.endswith('.joblib') and not f.startswith('feature_names')]
            
            if not model_files:
                print(f"{Fore.RED}No models found in {self.models_dir}!{Style.RESET_ALL}")
                return
                
            print(f"\n{Fore.GREEN}Available Models:{Style.RESET_ALL}")
            for i, file in enumerate(model_files, 1):
                print(f"{i}. {file}")
                
                # Extract and show model creation date
                try:
                    timestamp = file.split('_')[-1].replace('.joblib', '')
                    created_date = datetime.strptime(timestamp, '%Y%m%d_%H%M')
                    print(f"   {Fore.BLUE}Created: {created_date.strftime('%Y-%m-%d %H:%M')}{Style.RESET_ALL}")
                except:
                    pass
            
            # Get user choice
            while True:
                choice = input(f"\n{Fore.YELLOW}Enter model number to evaluate (or 'q' to quit): {Style.RESET_ALL}")
                
                if choice.lower() == 'q':
                    return
                    
                try:
                    model_index = int(choice) - 1
                    if 0 <= model_index < len(model_files):
                        break
                    else:
                        print(f"{Fore.RED}Invalid choice! Please enter a number between 1 and {len(model_files)}{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED}Please enter a valid number!{Style.RESET_ALL}")
            
            # Load the chosen model
            model_path = os.path.join(self.models_dir, model_files[model_index])
            print(f"\n{Fore.CYAN}Loading model: {model_files[model_index]}{Style.RESET_ALL}")
            
            model = joblib.load(model_path)
            
            # Load feature names
            feature_path = os.path.join(self.models_dir, 'feature_names.joblib')
            if not os.path.exists(feature_path):
                print(f"{Fore.RED}Feature names file not found!{Style.RESET_ALL}")
                return
                
            feature_names = joblib.load(feature_path)
            features = feature_names.get('features', [])
            
            if not features:
                print(f"{Fore.RED}No feature names found!{Style.RESET_ALL}")
                return
            
            # Load evaluation data
            print(f"\n{Fore.CYAN}Loading evaluation data...{Style.RESET_ALL}")
            data = self.load_data()
            
            if data is None:
                return
            
            # Prepare features and target
            try:
                X = data[features]
                y = data['market_change']
                
                # Perform predictions
                print(f"\n{Fore.CYAN}Calculating performance metrics...{Style.RESET_ALL}")
                y_pred = model.predict(X)
                
                # Calculate metrics
                mse = mean_squared_error(y, y_pred)
                rmse = np.sqrt(mse)
                r2 = r2_score(y, y_pred)
                mae = mean_absolute_error(y, y_pred)
                
                # Display performance metrics
                print(f"\n{Fore.GREEN}Performance Metrics for {model_files[model_index]}:{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Mean Squared Error (MSE): {mse:.6f}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Root Mean Squared Error (RMSE): {rmse:.6f}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Mean Absolute Error (MAE): {mae:.6f}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}R-squared Score (R²): {r2:.6f}{Style.RESET_ALL}")
                
                # Feature importance if available
                if hasattr(model, 'feature_importances_'):
                    print(f"\n{Fore.GREEN}Feature Importance:{Style.RESET_ALL}")
                    importances = sorted(zip(features, model.feature_importances_),
                                      key=lambda x: x[1], reverse=True)
                    for feature, importance in importances:
                        print(f"{feature}: {importance:.4f}")
                
            except KeyError as e:
                print(f"{Fore.RED}Required feature not found in data: {e}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}Error during evaluation: {e}{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
            return

def main():
    viewer = ResultViewer()
    
    while True:
        viewer.print_header("Analysis Results Viewer")
        
        print(f"\n{Fore.YELLOW}Menu Options:{Style.RESET_ALL}")
        print("1. 📊 Latest Visualizations")
        print("2. 📈 Data Analysis Summary")
        print("3. 🤖 Model Performance")
        print("4. 🚪 Exit")
        
        try:
            choice = input(f"\n{Fore.GREEN}Enter your choice (1-4): {Style.RESET_ALL}")
            
            if choice == '1':
                viewer.show_latest_visualizations()
            elif choice == '2':
                viewer.show_latest_data()
            elif choice == '3':
                viewer.show_model_performance()
            elif choice == '4':
                viewer.print_header("Goodbye! 👋")
                break
            else:
                print(f"{Fore.RED}Invalid choice! Please try again.{Style.RESET_ALL}")
            
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            
        except KeyboardInterrupt:
            viewer.print_header("Goodbye! 👋")
            break
        except Exception as e:
            print(f"{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main() 