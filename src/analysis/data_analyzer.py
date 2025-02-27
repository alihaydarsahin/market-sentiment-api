import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob
import os
import json
import logging
import glob
import shutil

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataAnalyzer:
    def __init__(self):
        self.data_paths = {
            'reddit': 'data/raw/reddit',
            'market': 'data/raw/market',
            'github': 'data/raw/github',
            'news': 'data/raw/news'
        }
        # Create analysis directory
        os.makedirs('data/analysis/figures', exist_ok=True)
    
    def load_latest_data(self):
        """Load most recent data from each source"""
        data = {}
        for source, path in self.data_paths.items():
            try:
                # Get latest file
                files = os.listdir(path)
                if not files:
                    continue
                latest_file = sorted(files)[-1]
                
                # Load data
                df = pd.read_csv(f"{path}/{latest_file}")
                data[source] = df
                
            except Exception as e:
                logger.error(f"Error loading {source} data: {e}")
        
        return data
    
    def analyze_sentiment(self, data):
        """Analyze sentiment across Reddit and News data"""
        sentiment_analysis = {}
        
        # Reddit sentiment
        if 'reddit' in data:
            reddit_df = data['reddit']
            sentiment_analysis['reddit'] = {
                'mean_sentiment': reddit_df['sentiment_polarity'].mean(),
                'sentiment_trend': reddit_df.groupby('subreddit')['sentiment_polarity'].mean().to_dict(),
                'most_positive_topics': reddit_df.nlargest(5, 'sentiment_polarity')[['title', 'sentiment_polarity']].to_dict('records')
            }
        
        # News sentiment
        if 'news' in data:
            news_df = data['news']
            sentiment_analysis['news'] = {
                'mean_sentiment': news_df['sentiment_score'].mean(),
                'sentiment_by_source': news_df.groupby('source')['sentiment_score'].mean().to_dict()
            }
        
        return sentiment_analysis
    
    def analyze_correlations(self, data):
        """Analyze correlations between sentiment and market data"""
        if 'market' not in data or ('reddit' not in data and 'news' not in data):
            return {}
        
        market_df = data['market']
        correlations = {}
        
        # Prepare market data
        market_daily = market_df.groupby('date')['close'].mean().reset_index()
        
        # Correlate with Reddit sentiment
        if 'reddit' in data:
            reddit_df = data['reddit']
            reddit_daily = reddit_df.groupby(pd.to_datetime(reddit_df['created_utc']).dt.date)['sentiment_polarity'].mean()
            correlations['reddit_market'] = market_daily['close'].corr(reddit_daily)
        
        # Correlate with news sentiment
        if 'news' in data:
            news_df = data['news']
            news_daily = news_df.groupby(pd.to_datetime(news_df['publishedAt']).dt.date)['sentiment_score'].mean()
            correlations['news_market'] = market_daily['close'].corr(news_daily)
        
        return correlations
    
    def get_top_topics(self, data):
        """Get trending topics from Reddit and GitHub"""
        topics = {}
        
        # Reddit topics
        if 'reddit' in data:
            reddit_df = data['reddit']
            topics['reddit'] = reddit_df.groupby('subreddit').size().nlargest(5).to_dict()
        
        # GitHub topics
        if 'github' in data:
            github_df = data['github']
            topics['github'] = github_df.groupby('language').size().nlargest(5).to_dict()
        
        return topics
    
    def analyze_market_impact(self, data):
        """Analyze market impact of sentiment"""
        if 'market' not in data:
            return {}
        
        market_df = data['market']
        impact = {
            'price_changes': market_df.groupby('symbol')['change_pct'].mean().to_dict(),
            'volume_changes': market_df.groupby('symbol')['volume'].pct_change().mean().to_dict()
        }
        
        return impact
    
    def analyze_trends(self):
        """Analyze trends across all data sources"""
        data = self.load_latest_data()
        
        analysis = {
            'sentiment': self.analyze_sentiment(data),
            'correlations': self.analyze_correlations(data),
            'top_topics': self.get_top_topics(data),
            'market_impact': self.analyze_market_impact(data)
        }
        
        return analysis
    
    def generate_report(self):
        """Generate comprehensive analysis report with enhanced features"""
        analysis = self.analyze_trends()
        
        # Create report directory with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        report_dir = f"data/analysis/report_{timestamp}"
        os.makedirs(report_dir, exist_ok=True)
        os.makedirs(f"{report_dir}/figures", exist_ok=True)
        
        try:
            # Create visualizations with error handling
            visualization_tasks = {
                'sentiment': lambda: self.plot_sentiment_trends(analysis['sentiment']),
                'correlations': lambda: self.plot_correlation_matrix(analysis['correlations']),
                'topics': lambda: self.plot_top_topics(analysis['top_topics'])
            }
            
            failed_plots = []
            for name, task in visualization_tasks.items():
                try:
                    task()
                    # Move plots to report directory
                    old_path = f"data/analysis/figures/{name}_*.png"
                    for file in glob.glob(old_path):
                        shutil.move(file, f"{report_dir}/figures/")
                except Exception as e:
                    logger.error(f"Error generating {name} plot: {e}")
                    failed_plots.append(name)
            
            # Add metadata to analysis
            analysis['metadata'] = {
                'generated_at': timestamp,
                'failed_plots': failed_plots,
                'data_sources': list(analysis.keys()),
                'total_records_analyzed': self._get_total_records(analysis)
            }
            
            # Save report as JSON
            report_path = f"{report_dir}/analysis_report.json"
            with open(report_path, 'w') as f:
                json.dump(analysis, f, indent=4)
                
            # Generate HTML summary
            self._generate_html_summary(analysis, report_dir)
            
            logger.info(f"Report generated successfully at {report_dir}")
            return report_dir
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            raise
    
    def _get_total_records(self, analysis):
        """Helper method to count total records analyzed"""
        total = 0
        if 'sentiment' in analysis:
            if 'reddit' in analysis['sentiment']:
                total += len(analysis['sentiment']['reddit'].get('sentiment_trend', {}))
            if 'news' in analysis['sentiment']:
                total += len(analysis['sentiment']['news'].get('sentiment_by_source', {}))
        return total
    
    def _generate_html_summary(self, analysis, report_dir):
        """Generate HTML summary of the analysis"""
        template = """
        <html>
            <head>
                <title>Analysis Report {timestamp}</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .summary { margin-bottom: 20px; }
                    .visualization { margin: 20px 0; }
                </style>
            </head>
            <body>
                <h1>Analysis Report {timestamp}</h1>
                <div class="summary">
                    <h2>Summary</h2>
                    <p>Total records analyzed: {total_records}</p>
                    <p>Data sources: {sources}</p>
                    {failed_plots_info}
                </div>
                <div class="visualizations">
                    <h2>Visualizations</h2>
                    {visualization_html}
                </div>
            </body>
        </html>
        """
        
        # Generate visualization HTML
        viz_html = ""
        for fig_file in glob.glob(f"{report_dir}/figures/*.png"):
            viz_html += f'<div class="visualization"><img src="figures/{os.path.basename(fig_file)}" /></div>'
        
        failed_plots_info = ""
        if analysis['metadata']['failed_plots']:
            failed_plots_info = "<p>Failed plots: " + ", ".join(analysis['metadata']['failed_plots']) + "</p>"
        
        html_content = template.format(
            timestamp=analysis['metadata']['generated_at'],
            total_records=analysis['metadata']['total_records_analyzed'],
            sources=", ".join(analysis['metadata']['data_sources']),
            failed_plots_info=failed_plots_info,
            visualization_html=viz_html
        )
        
        with open(f"{report_dir}/report_summary.html", 'w') as f:
            f.write(html_content)

    def plot_sentiment_trends(self, sentiment_data):
        """Plot sentiment trends"""
        plt.figure(figsize=(12, 6))
        
        if 'reddit' in sentiment_data and sentiment_data['reddit']['sentiment_trend']:
            subreddits = sentiment_data['reddit']['sentiment_trend'].keys()
            sentiments = sentiment_data['reddit']['sentiment_trend'].values()
            plt.bar(subreddits, sentiments, alpha=0.6, label='Reddit')
            plt.legend()  # Only add legend if we have data
        else:
            plt.text(0.5, 0.5, 'No sentiment data available', 
                    horizontalalignment='center',
                    verticalalignment='center')
        
        plt.title('Sentiment Analysis by Source')
        plt.xlabel('Source')
        plt.ylabel('Sentiment Score')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save plot
        plt.savefig('data/analysis/figures/sentiment_trends.png')
        plt.close()
    
    def plot_correlation_matrix(self, correlation_data):
        """Plot correlation matrix"""
        if not correlation_data:
            return
        
        corr_matrix = pd.DataFrame(correlation_data).fillna(0)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
        plt.title('Correlations between Sources')
        plt.tight_layout()
        
        # Save plot
        plt.savefig('data/analysis/figures/correlation_matrix.png')
        plt.close()
    
    def plot_top_topics(self, topics_data):
        """Plot top topics"""
        plt.figure(figsize=(12, 6))
        
        if 'reddit' in topics_data:
            topics = topics_data['reddit'].keys()
            counts = topics_data['reddit'].values()
            plt.bar(topics, counts, alpha=0.6, label='Reddit Topics')
        
        plt.title('Top Topics by Platform')
        plt.xlabel('Topic')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        
        # Save plot
        plt.savefig('data/analysis/figures/top_topics.png')
        plt.close()

def main():
    analyzer = DataAnalyzer()
    analyzer.generate_report()
    logger.info("Analysis complete! Check data/analysis folder for results.")

if __name__ == "__main__":
    main() 