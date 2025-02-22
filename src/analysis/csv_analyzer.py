import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
import glob
import numpy as np
from scipy import stats  # Added for probplot
import warnings
warnings.filterwarnings('ignore')  # Suppress warnings

class CSVAnalyzer:
    def __init__(self):
        self.output_dir = 'data/analysis/figures'
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set style for all plots
        plt.style.use('default')  # or 'classic', 'bmh', 'ggplot', etc.
        self.colors = sns.color_palette("husl", 8)
        
        # Set higher DPI for better quality
        plt.rcParams['figure.dpi'] = 300
        
    def find_csv_files(self, directory):
        """Find all CSV files in directory and subdirectories"""
        return glob.glob(f"{directory}/**/*.csv", recursive=True)
    
    def analyze_csv(self, csv_path):
        """Analyze a single CSV file"""
        try:
            # Read CSV
            df = pd.read_csv(csv_path)
            filename = os.path.basename(csv_path).replace('.csv', '')
            
            # Determine data type from filename
            data_type = 'other'
            if 'news' in filename.lower():
                data_type = 'news_analysis'
            elif 'reddit' in filename.lower():
                data_type = 'reddit_analysis'
            elif 'market' in filename.lower():
                data_type = 'market_analysis'
            elif 'github' in filename.lower():
                data_type = 'github_analysis'
            
            # Create figure directory with data type
            fig_dir = f"{self.output_dir}/{data_type}"
            os.makedirs(fig_dir, exist_ok=True)
            
            print(f"\nAnalyzing {filename}")
            print(f"Data type: {data_type}")
            print(f"Shape: {df.shape}")
            
            # Save data info
            with open(f"{fig_dir}/data_info.txt", 'a') as f:
                f.write(f"\n\n=== {filename} ===\n")
                df.info(buf=f)
            
            # Basic statistics
            self.plot_basic_stats(df, fig_dir, filename)
            
            # Numerical columns analysis
            self.plot_numerical_analysis(df, fig_dir, filename)
            
            # Categorical columns analysis
            self.plot_categorical_analysis(df, fig_dir, filename)
            
            # Time series analysis if date columns exist
            self.plot_time_series(df, fig_dir, filename)
            
            # Correlation matrix
            self.plot_correlation_matrix(df, fig_dir, filename)
            
            # Save summary statistics
            summary_file = f"{fig_dir}/summary_statistics.csv"
            mode = 'a' if os.path.exists(summary_file) else 'w'
            with open(summary_file, mode) as f:
                if mode == 'w':
                    df.describe().to_csv(f)
                else:
                    f.write(f"\n\n=== {filename} ===\n")
                    df.describe().to_csv(f)
            
            print(f"✓ Analysis complete for {filename}")
            return True
            
        except Exception as e:
            print(f"✗ Error analyzing {csv_path}: {e}")
            return False
    
    def plot_basic_stats(self, df, output_dir, filename):
        """Plot basic statistics"""
        try:
            # Data overview
            stats_df = pd.DataFrame({
                'dtype': df.dtypes,
                'non_null': df.count(),
                'null_count': df.isnull().sum(),
                'unique_values': df.nunique(),
                'memory_usage': df.memory_usage(deep=True)
            })
            
            # Save stats as CSV
            stats_file = f"{output_dir}/basic_stats.csv"
            mode = 'a' if os.path.exists(stats_file) else 'w'
            with open(stats_file, mode) as f:
                if mode == 'w':
                    stats_df.to_csv(f)
                else:
                    f.write(f"\n\n=== {filename} ===\n")
                    stats_df.to_csv(f)
            
            # Create visual summary
            plt.figure(figsize=(12, 6))
            stats_df['null_percentage'] = (stats_df['null_count'] / len(df)) * 100
            sns.barplot(x=stats_df.index, y=stats_df['null_percentage'])
            plt.title(f'Null Values Percentage - {filename}')
            plt.xticks(rotation=45, ha='right')
            plt.ylabel('Null Percentage (%)')
            plt.tight_layout()
            plt.savefig(f"{output_dir}/null_values_{filename}.png")
            plt.close()
            
        except Exception as e:
            print(f"Error in basic stats: {e}")
    
    def plot_numerical_analysis(self, df, output_dir, filename):
        """Analyze numerical columns"""
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numerical_cols:
            try:
                plt.figure(figsize=(15, 5))
                
                # Distribution plot
                plt.subplot(1, 3, 1)
                sns.histplot(df[col].dropna(), kde=True)
                plt.title(f'{filename} - {col} Distribution')
                plt.xticks(rotation=45)
                
                # Box plot
                plt.subplot(1, 3, 2)
                sns.boxplot(y=df[col].dropna())
                plt.title(f'{filename} - {col} Box Plot')
                
                # QQ plot
                plt.subplot(1, 3, 3)
                stats.probplot(df[col].dropna(), dist="norm", plot=plt)
                plt.title(f'{filename} - {col} Q-Q Plot')
                
                plt.tight_layout()
                plt.savefig(f"{output_dir}/{col}_analysis.png")
                plt.close()
                
                # Save statistics
                desc = df[col].describe()
                desc.to_csv(f"{output_dir}/{col}_statistics.csv")
                
            except Exception as e:
                print(f"Error analyzing {filename} - {col}: {e}")
    
    def plot_categorical_analysis(self, df, output_dir, filename):
        """Analyze categorical columns"""
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        for col in categorical_cols:
            try:
                if df[col].nunique() < 50:  # Only plot if fewer than 50 unique values
                    plt.figure(figsize=(12, 6))
                    
                    # Value counts
                    value_counts = df[col].value_counts()
                    
                    # Bar plot
                    sns.barplot(x=value_counts.index, y=value_counts.values)
                    plt.title(f'{filename} - {col} Value Distribution')
                    plt.xticks(rotation=45, ha='right')
                    
                    plt.tight_layout()
                    plt.savefig(f"{output_dir}/{col}_distribution.png")
                    plt.close()
                    
                    # Save top values to CSV
                    value_counts.head(10).to_frame(name='count').to_csv(
                        f"{output_dir}/{col}_top_values.csv"
                    )
            except Exception as e:
                print(f"Error analyzing categorical {filename} - {col}: {e}")
    
    def plot_time_series(self, df, output_dir, filename):
        """Time series analysis for date columns"""
        date_columns = []
        for col in df.columns:
            try:
                pd.to_datetime(df[col])
                date_columns.append(col)
            except:
                continue
        
        for date_col in date_columns:
            try:
                df[date_col] = pd.to_datetime(df[date_col])
                
                # Daily counts
                daily_counts = df.groupby(df[date_col].dt.date).size()
                
                plt.figure(figsize=(12, 6))
                daily_counts.plot(kind='line', marker='o')
                plt.title(f'{filename} - Time Series Analysis - {date_col}')
                plt.xlabel('Date')
                plt.ylabel('Count')
                plt.xticks(rotation=45)
                plt.grid(True)
                plt.tight_layout()
                plt.savefig(f"{output_dir}/{date_col}_timeseries.png")
                plt.close()
                
                # Save time series data
                daily_counts.to_csv(f"{output_dir}/{date_col}_timeseries.csv")
                
            except Exception as e:
                print(f"Error in time series analysis for {filename} - {date_col}: {e}")
    
    def plot_correlation_matrix(self, df, output_dir, filename):
        """Create correlation matrix"""
        try:
            numerical_df = df.select_dtypes(include=[np.number])
            
            if not numerical_df.empty:
                plt.figure(figsize=(12, 8))
                correlation = numerical_df.corr()
                
                # Plot correlation matrix
                mask = np.triu(np.ones_like(correlation, dtype=bool))
                sns.heatmap(correlation, 
                          mask=mask,
                          annot=True, 
                          cmap='coolwarm', 
                          center=0,
                          fmt='.2f',
                          square=True)
                plt.title(f'{filename} - Correlation Matrix')
                plt.tight_layout()
                plt.savefig(f"{output_dir}/correlation_matrix.png")
                plt.close()
                
                # Save correlation to CSV
                correlation.to_csv(f"{output_dir}/correlation_matrix.csv")
                
        except Exception as e:
            print(f"Error in correlation analysis: {e}")

def main():
    analyzer = CSVAnalyzer()
    
    # Find all CSV files in data/raw directory
    csv_files = analyzer.find_csv_files('data/raw')
    
    print(f"Found {len(csv_files)} CSV files")
    
    # Analyze each CSV file
    for csv_file in csv_files:
        analyzer.analyze_csv(csv_file)
    
    print("\nAnalysis complete! Check data/analysis/figures for results")

if __name__ == "__main__":
    main() 