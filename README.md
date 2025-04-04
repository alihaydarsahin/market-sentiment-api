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

## Environment Setup

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- PostgreSQL
- Git
- PowerShell (for Windows users)

### Virtual Environment Setup

#### Windows
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Linux/Mac
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration
1. Copy environment template:
```bash
cp .env.example .env
```

2. Configure environment variables in `.env`:
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `API_KEY`: API key for external services
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Deployment

### Using Docker (Recommended)
```bash
# Windows
.\deploy.bat

# Linux/Mac
./deploy.sh
```

The deployment script will:
1. Stop any running containers
2. Build and start new containers
3. Initialize the database
4. Run migrations
5. Train models
6. Start the API server

### Manual Deployment
1. Start PostgreSQL database
2. Run database migrations:
```bash
flask db upgrade
```

3. Initialize database:
```bash
python src/scripts/init_db.py
```

4. Train models:
```bash
python src/scripts/train_models.py
```

5. Start API server:
```bash
python src/api/app.py
```

## Testing

### API Testing
```bash
# Windows
.\test_api.ps1

# Linux/Mac
curl -X GET http://localhost:5000/api/health
```

The test script will:
1. Check API health
2. Test authentication
3. Test prediction endpoint
4. Display results with color-coded output

### Development Testing
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_api.py

# Run with coverage
python -m pytest --cov=src tests/
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