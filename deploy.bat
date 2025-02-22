@echo off
setlocal enabledelayedexpansion

:: Check for required tools
echo Checking dependencies...

:: Check Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker is not installed! Please install Docker Desktop.
    exit /b 1
)

:: Check Docker Compose
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker Compose is not installed!
    exit /b 1
)

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed!
    exit /b 1
)

:: Check pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pip is not installed!
    exit /b 1
)

:: Install required Python packages
echo Installing Python dependencies...
pip install -r requirements.txt

:: Create necessary directories
echo Creating directories...
if not exist "models" mkdir models
if not exist "data\logs" mkdir data\logs
if not exist "data\processed" mkdir data\processed
if not exist "data\analysis\figures" mkdir data\analysis\figures

:: Start deployment
echo Stopping containers...
docker-compose down

echo Building and starting containers...
docker-compose up --build -d

echo Waiting for database...
timeout /t 10

echo Running database migrations...
docker-compose exec -T api flask db upgrade

echo Initializing database...
docker-compose exec -T api python src/scripts/create_db.py

echo Training models...
docker-compose exec -T api python src/scripts/train_models.py

echo Running tests...
powershell -File test_api.ps1

echo Deployment complete! 