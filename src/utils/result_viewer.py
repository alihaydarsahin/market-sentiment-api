import os
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
from colorama import init, Fore, Style
import time

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
    
    def show_model_performance(self):
        """Show model performance metrics"""
        self.print_header("Model Performance")
        
        model_files = [f for f in os.listdir(self.models_dir) 
                      if f.endswith('.joblib')]
        
        if not model_files:
            print(f"{Fore.RED}No models found!{Style.RESET_ALL}")
            return
            
        print(f"\n{Fore.GREEN}Available Models:{Style.RESET_ALL}")
        for i, file in enumerate(model_files, 1):
            print(f"{i}. {file}")
            
            # Try to extract timestamp from filename
            try:
                timestamp = file.split('_')[-1].replace('.joblib', '')
                print(f"   {Fore.BLUE}Created: {timestamp}{Style.RESET_ALL}")
            except:
                pass

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