# Analysis Module

This module provides tools for analyzing and visualizing data from multiple sources, including market data, news articles, and social media.

## Structure

The analysis module is organized as follows:

- `core.py`: Contains the core analyzer classes
  - `CoreAnalyzer`: Base class with common functionality
  - `UnifiedAnalyzer`: Main class for analyzing data from multiple sources
- `utils.py`: Utility functions for data loading, saving, and processing
- `visualization.py`: Specialized visualization functions
- `config.py`: Configuration management utilities
- `cli.py`: Command-line interface for running analyses
- `main.py`: Entry point for the analysis package

## Usage

### Basic Usage

```python
from src.analysis import UnifiedAnalyzer

# Initialize the analyzer with default configuration
analyzer = UnifiedAnalyzer()

# Load data from all sources
analyzer.load_data()

# Perform analysis on all data sources
results = analyzer.analyze_all()

# Create visualizations
analyzer.create_visualizations(results)

# Save results
analyzer.save_results(results, 'output/results.json')
```

### Command-line Usage

```bash
python -m src.analysis --config=config.json --output=results --sources=all --format=json
```

Command-line options:
- `--config`: Path to configuration file (default: config.json)
- `--output`: Output directory (default: output)
- `--sources`: Data sources to analyze (comma-separated, or 'all')
- `--format`: Output format (json, csv, or both)
- `--visualize`: Enable visualizations (true/false)
- `--parallel`: Enable parallel processing (true/false)
- `--summary`: Generate human-readable summary (true/false)

## Configuration

The system uses a JSON configuration file to control various aspects of the analysis. Here's an example:

```json
{
  "data_sources": {
    "reddit": {
      "enabled": true,
      "data_path": "data/reddit",
      "analysis": {
        "sentiment": true,
        "entities": true,
        "topics": true
      }
    },
    "news": {
      "enabled": true,
      "data_path": "data/news",
      "analysis": {
        "sentiment": true,
        "entities": true,
        "topics": true
      }
    },
    "market": {
      "enabled": true,
      "data_path": "data/market",
      "analysis": {
        "statistics": true,
        "trends": true
      }
    }
  },
  "visualization": {
    "enabled": true,
    "output_path": "output/visualizations",
    "formats": ["png", "html"],
    "advanced": true
  },
  "cross_source_analysis": {
    "enabled": true,
    "correlations": true
  },
  "parallel_processing": {
    "enabled": true,
    "max_workers": 4
  },
  "output": {
    "formats": ["json", "csv"],
    "timestamp_files": true
  }
}
```

You can generate a default configuration using:

```python
from src.analysis import generate_default_config, save_config

config = generate_default_config()
save_config(config, 'config.json')
```

## Key Features

1. **Unified Analysis**: Analyze data from multiple sources in a consistent way
2. **Visualization**: Create visualizations for individual data sources and cross-source correlations
3. **Parallel Processing**: Analyze multiple data sources in parallel for improved performance
4. **Flexible Configuration**: Control all aspects of analysis through a comprehensive configuration system
5. **Command-line Interface**: Run analyses directly from the command line

## Dependencies

- pandas: Data manipulation
- numpy: Numerical operations
- matplotlib: Visualization
- seaborn: Enhanced visualizations
- plotly (optional): Interactive visualizations
- wordcloud (optional): Word cloud visualizations

## Extension

To add support for new data sources:
1. Update the `load_data` method in `UnifiedAnalyzer`
2. Add corresponding analysis methods
3. Update visualization methods as needed
4. Modify the configuration schema in `config.py` 