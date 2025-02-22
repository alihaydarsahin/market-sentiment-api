import os
import sys
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_deployment_readiness():
    """Pre-deployment checks"""
    checks = {
        'directories': check_directories(),
        'dependencies': check_dependencies(),
        'data': check_data_files(),
        'models': check_models(),
        'env': check_env_files()
    }
    
    return all(checks.values()), checks

def check_directories():
    """Check required directories"""
    required_dirs = [
        'data/raw',
        'data/processed',
        'data/logs',
        'models',
        'data/analysis/figures'
    ]
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            logger.error(f"Missing directory: {dir_path}")
            return False
            
    return True

def check_dependencies():
    """Check required packages"""
    try:
        import flask
        import pandas
        import numpy
        import sklearn
        return True
    except ImportError as e:
        logger.error(f"Missing package: {e}")
        return False

def check_data_files():
    """Check data files"""
    required_files = [
        'data/processed/combined_data_'
    ]
    
    for file_prefix in required_files:
        files = [f for f in os.listdir(os.path.dirname(file_prefix)) 
                if f.startswith(os.path.basename(file_prefix))]
        if not files:
            logger.error(f"Missing data file: {file_prefix}")
            return False
    
    return True

def check_models():
    """Check model files"""
    model_files = os.listdir('models')
    if not any(f.endswith('.joblib') for f in model_files):
        logger.error("No trained model found!")
        return False
    return True

def check_env_files():
    """Check environment files"""
    if not os.path.exists('.env'):
        logger.error(".env file not found!")
        return False
    return True

if __name__ == '__main__':
    success, results = check_deployment_readiness()
    
    if success:
        logger.info("✅ Ready for deployment!")
    else:
        logger.error("❌ Deployment checks failed!")
        for check, result in results.items():
            status = "✅" if result else "❌"
            logger.info(f"{status} {check}") 