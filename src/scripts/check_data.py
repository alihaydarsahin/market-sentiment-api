import os
import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_data_files():
    """Check available data files"""
    data_dirs = [
        'data/raw',
        'data/processed',
        'data/analysis/figures'
    ]
    
    for dir_path in data_dirs:
        logger.info(f"\nChecking directory: {dir_path}")
        if os.path.exists(dir_path):
            files = os.listdir(dir_path)
            for file in files:
                if file.endswith('.csv'):
                    file_path = os.path.join(dir_path, file)
                    df = pd.read_csv(file_path)
                    logger.info(f"\nFile: {file}")
                    logger.info(f"Shape: {df.shape}")
                    logger.info(f"Columns: {df.columns.tolist()}")
        else:
            logger.warning(f"Directory not found: {dir_path}")

if __name__ == '__main__':
    check_data_files() 