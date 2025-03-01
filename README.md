# Market Sentiment Analysis and Prediction API

## Overview
A machine learning API that analyzes market sentiment from multiple data sources (Reddit, News, Market Data) and provides market predictions through a secure REST API. The system collects data from various sources, processes it using natural language processing techniques, and generates market sentiment predictions.

## Features

### Data Collection
- Reddit data collection with sentiment analysis
- News API integration for market news
- Market data from financial APIs
- E-commerce data scraping capabilities

### Data Analysis
- Sentiment analysis using NLP
- Time series analysis
- Statistical market analysis
- Automated data quality checks

### News Analysis Features
- Advanced text processing with NLTK
- Entity extraction and named entity recognition
- Tech company impact analysis
- Comprehensive visualizations:
  - Sentiment distribution analysis
  - Interactive word clouds
  - Category distribution charts
  - Tech company mention analysis
- Enhanced ML-focused categorization:
  - AI/ML developments
  - Blockchain and Web3
  - Cloud technologies
  - Cybersecurity
  - E-commerce trends
  - Fintech innovations
- Detailed JSON reporting with:
  - Sentiment metrics
  - Trend analysis
  - Topic clustering
  - Impact assessment

### Machine Learning
- RandomForest and GradientBoosting models
- Feature engineering with technical indicators
- Model performance monitoring
- Real-time prediction capabilities
- Comprehensive model evaluation:
  - Multiple performance metrics (MSE, RMSE, MAE, R²)
  - Feature importance analysis
  - Interactive model comparison
  - Historical performance tracking

### API Features
- Secure JWT authentication
- Role-based access control
- Rate limiting
- Swagger documentation
- Prometheus metrics

## Data Quality Features

### Automated Quality Checks
- **Data Freshness Monitoring**
  - Tracks data age across all sources
  - Alerts for outdated data
  - Configurable freshness thresholds

- **Sentiment Analysis Quality**
  - Distribution analysis with visualizations
  - Anomaly detection
  - Missing data tracking
  - Statistical validation

- **Data Consistency Checks**
  - Cross-source data validation
  - Date continuity verification
  - Value range validation
  - Automated gap detection

### Error Handling & Logging
- Comprehensive error catching
- Detailed logging with multiple handlers
- Structured error reporting
- Debug-friendly error messages

### Quality Reports
- JSON-formatted quality reports
- Visual distribution plots
- Temporal analysis
- Source-specific metrics

### Implementation Best Practices
✅ Robust error handling
✅ Type hints and documentation
✅ Configurable parameters
✅ Automated report generation
✅ Visualization capabilities

## Project Structure
```
project/
├── src/
│   ├── api/                 # API implementation
│   ├── data_collection/     # Data collectors
│   ├── analysis/           # Data analysis
│   ├── models/            # ML models
│   ├── pipeline/          # Data pipeline
│   ├── utils/             # Utilities
│   └── scripts/           # Management scripts
├── data/
│   ├── raw/               # Raw collected data
│   ├── processed/         # Processed datasets
│   └── analysis/          # Analysis results
├── models/                # Trained models
└── tests/                # Test suite
```

## Installation

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- PostgreSQL
- Git

### Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd market-sentiment-api
```

2. Create and activate virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize database:
```bash
python src/scripts/create_db.py
```

## Running the Application

### Using Docker
```bash
# Build and start containers
docker-compose up --build -d

# Initialize database
docker-compose exec api python src/scripts/create_db.py
```

### Manual Run
```bash
# Start the API server
python src/api/app.py
```

## API Documentation

### Authentication
```bash
# Login to get access token
curl -X POST http://localhost:5000/api/auth/login -u admin:admin123

# Response
{
    "access_token": "eyJ0eXAiOiJKV1...",
    "message": "Login successful"
}
```

### Available Endpoints
- `POST /api/auth/login` - Authentication
- `POST /api/auth/refresh` - Refresh token
- `GET /api/health` - Health check
- `POST /api/predict` - Make predictions
- `GET /api/data/latest` - Get latest data
- `GET /api/visualizations` - List visualizations
- `GET /api/model/info` - Model information (admin only)

### Making Predictions
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "reddit_sentiment": 0.5,
    "news_sentiment": 0.3,
    "market_change": 0.1
  }'
```

## Development

### Running Tests
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_api.py
```

### Code Quality
- PEP 8 compliant
- Type hints used
- Comprehensive docstrings
- Unit tests for core functionality

## Deployment
The application can be deployed using Docker Compose or traditional deployment methods.

### Docker Deployment
1. Configure environment variables in `.env`
2. Run deployment script:
```bash
# Windows
.\deploy.bat

# Linux/Mac
./deploy.sh
```

### Manual Deployment
1. Set up PostgreSQL database
2. Configure environment variables
3. Install dependencies
4. Run database migrations
5. Start the application server

## Monitoring
- Prometheus metrics at `/metrics`
- Logging to `data/logs/`
- Health check endpoint at `/api/health`

## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contact
For any questions or feedback, please open an issue on GitHub.

## Known Issues & Improvements

### Data Processing Improvements

#### 1. File Sorting and Date Handling
- **Issue**: Inconsistent date formats in filenames can cause incorrect sorting
- **Current**: Relies on alphabetical sorting of filenames
- **Solution**: Implemented date extraction for reliable chronological sorting
```python
latest_file = max(combined_files, key=lambda f: f.split('_')[-1].replace('.csv', ''))
```

#### 2. Empty Data Handling
- **Issue**: Potential crashes when no data files are found
- **Solution**: Added robust error handling
```python
if not combined_files:
    logger.warning("No combined data files found")
    return None
```

#### 3. File Read Error Management
- **Issue**: Potential crashes on corrupted or missing files
- **Solution**: Implemented comprehensive error handling
```python
try:
    data = pd.read_csv(os.path.join(self.data_dir, latest_file))
except Exception as e:
    logger.error(f"Failed to read {latest_file}: {e}")
    return None
```

### Implementation Example
```python
def get_latest_data(self):
    if not combined_files:
        logger.warning("No combined data files found")
        return None

    try:
        latest_file = max(combined_files, key=lambda f: f.split('_')[-1].replace('.csv', ''))
        file_path = os.path.join(self.data_dir, latest_file)
        data = pd.read_csv(file_path)
        logger.info(f"Loaded data from {latest_file}")
        return data
    except Exception as e:
        logger.error(f"Failed to read {latest_file}: {e}")
        return None
```

### Key Improvements
✅ Reliable chronological file sorting
✅ Robust empty data handling
✅ Comprehensive error management
✅ Detailed logging for debugging
✅ Safe file operations

## Model Performance Analysis

### Accessing Model Performance
```bash
# Run the result viewer
python src/utils/result_viewer.py

# Select option 3 for Model Performance
# Follow the interactive prompts to:
# 1. View available models
# 2. Select a model to evaluate
# 3. View comprehensive metrics
# 4. Analyze feature importance
```

### Understanding Metrics
- **MSE (Mean Squared Error)**: Measures average squared difference between predictions and actual values
- **RMSE (Root Mean Squared Error)**: Square root of MSE, provides error metric in same unit as target variable
- **MAE (Mean Absolute Error)**: Average absolute difference between predictions and actual values
- **R² Score**: Indicates how well the model explains the variance in the data (0 to 1)

## Using the Model Viewer

### Accessing Model Performance
```bash
# Run the result viewer
python src/utils/result_viewer.py

# Select option 3 for Model Performance
# Follow the interactive prompts to:
# 1. View available models
# 2. Select a model to evaluate
# 3. View comprehensive metrics
# 4. Analyze feature importance
```

### Understanding Metrics
- **MSE (Mean Squared Error)**: Measures average squared difference between predictions and actual values
- **RMSE (Root Mean Squared Error)**: Square root of MSE, provides error metric in same unit as target variable
- **MAE (Mean Absolute Error)**: Average absolute difference between predictions and actual values
- **R² Score**: Indicates how well the model explains the variance in the data (0 to 1)