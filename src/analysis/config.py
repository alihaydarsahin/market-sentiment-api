"""
Configuration utility for the analysis module.
This module handles configuration generation and validation.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

# Default configuration template
DEFAULT_CONFIG = {
    "data_sources": {
        "reddit": {
            "enabled": True,
            "data_path": "data/raw/reddit",
            "analysis": {
                "sentiment_analysis": True,
                "entity_extraction": True
            }
        },
        "news": {
            "enabled": True,
            "data_path": "data/raw/news",
            "analysis": {
                "sentiment_analysis": True,
                "entity_extraction": True,
                "topic_extraction": True
            }
        },
        "market": {
            "enabled": True,
            "data_path": "data/raw/market",
            "analysis": {
                "volatility_analysis": True
            }
        }
    },
    "visualization": {
        "basic": {
            "enabled": True,
            "colors": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"],
            "figure_size": [12, 8],
            "dpi": 300
        },
        "advanced": {
            "enabled": True
        }
    },
    "cross_source_analysis": {
        "enabled": True
    },
    "parallel_processing": {
        "enabled": True,
        "max_workers": 4
    },
    "output": {
        "formats": ["json", "csv"],
        "generate_summary": True
    }
}


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load and validate a configuration file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Validated configuration dictionary
        
    Raises:
        FileNotFoundError: If the configuration file does not exist
        json.JSONDecodeError: If the configuration file is not valid JSON
    """
    logger = logging.getLogger('analysis')
    
    if not os.path.exists(config_path):
        logger.error(f"Configuration file not found: {config_path}")
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file: {e}")
        raise
    except Exception as e:
        logger.error(f"Error reading configuration file: {e}")
        raise
    
    # Validate the configuration
    validated_config = validate_config(config)
    logger.info(f"Loaded and validated configuration from {config_path}")
    
    return validated_config


def save_config(config: Dict[str, Any], output_path: str, pretty: bool = True) -> bool:
    """
    Save a configuration dictionary to a file.
    
    Args:
        config: Configuration dictionary to save
        output_path: Path to save the configuration file
        pretty: Whether to pretty-print the JSON
        
    Returns:
        True if successful, False otherwise
    """
    logger = logging.getLogger('analysis')
    
    # Ensure directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            logger.info(f"Created directory: {output_dir}")
        except Exception as e:
            logger.error(f"Failed to create directory {output_dir}: {e}")
            return False
    
    # Write configuration to file
    try:
        with open(output_path, 'w') as f:
            if pretty:
                json.dump(config, f, indent=2)
            else:
                json.dump(config, f)
        logger.info(f"Saved configuration file to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save configuration file: {e}")
        return False


def generate_default_config(
    output_path: str = 'config/analysis_config.json',
    pretty: bool = True,
    overwrite: bool = False
) -> bool:
    """
    Generate a default configuration file.
    
    Args:
        output_path: Path to output configuration file
        pretty: Whether to pretty-print the JSON
        overwrite: Whether to overwrite existing file
        
    Returns:
        True if successful, False otherwise
    """
    logger = logging.getLogger('analysis')
    
    # Check if file already exists
    if os.path.exists(output_path) and not overwrite:
        logger.warning(f"Configuration file already exists at {output_path}. Use overwrite=True to overwrite.")
        return False
    
    return save_config(DEFAULT_CONFIG, output_path, pretty)


def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate a configuration dictionary and fill in missing values with defaults.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        Validated configuration dictionary
    """
    logger = logging.getLogger('analysis')
    
    # Start with a copy of the default config
    validated_config = DEFAULT_CONFIG.copy()
    
    # Merge with provided config
    if config:
        _deep_merge(validated_config, config)
    else:
        logger.warning("Empty configuration provided, using defaults")
    
    # Validate specific sections
    _validate_data_sources(validated_config)
    _validate_visualization(validated_config)
    _validate_output(validated_config)
    
    return validated_config


def _deep_merge(target: Dict[str, Any], source: Dict[str, Any]) -> None:
    """
    Deep merge two dictionaries.
    
    Args:
        target: Target dictionary to merge into
        source: Source dictionary to merge from
    """
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            _deep_merge(target[key], value)
        else:
            target[key] = value


def _validate_data_sources(config: Dict[str, Any]) -> None:
    """
    Validate data sources configuration.
    
    Args:
        config: Configuration dictionary to validate
    """
    logger = logging.getLogger('analysis')
    
    if 'data_sources' not in config:
        logger.warning("No data_sources in configuration, using defaults")
        return
    
    # Check each data source
    for source, details in config['data_sources'].items():
        if 'data_path' not in details:
            logger.warning(f"No data_path for {source}, using default")
            if source in DEFAULT_CONFIG['data_sources']:
                details['data_path'] = DEFAULT_CONFIG['data_sources'][source]['data_path']
            else:
                details['data_path'] = f"data/raw/{source}"
        
        if 'enabled' not in details:
            details['enabled'] = True


def _validate_visualization(config: Dict[str, Any]) -> None:
    """
    Validate visualization configuration.
    
    Args:
        config: Configuration dictionary to validate
    """
    logger = logging.getLogger('analysis')
    
    if 'visualization' not in config:
        logger.warning("No visualization in configuration, using defaults")
        return
    
    # Basic visualization settings
    if 'basic' not in config['visualization']:
        config['visualization']['basic'] = DEFAULT_CONFIG['visualization']['basic']
    else:
        basic = config['visualization']['basic']
        default_basic = DEFAULT_CONFIG['visualization']['basic']
        
        if 'enabled' not in basic:
            basic['enabled'] = default_basic['enabled']
        
        if 'colors' not in basic or not basic['colors']:
            basic['colors'] = default_basic['colors']
        
        if 'figure_size' not in basic or not basic['figure_size']:
            basic['figure_size'] = default_basic['figure_size']
        
        if 'dpi' not in basic:
            basic['dpi'] = default_basic['dpi']


def _validate_output(config: Dict[str, Any]) -> None:
    """
    Validate output configuration.
    
    Args:
        config: Configuration dictionary to validate
    """
    logger = logging.getLogger('analysis')
    
    if 'output' not in config:
        logger.warning("No output in configuration, using defaults")
        config['output'] = DEFAULT_CONFIG['output']
        return
    
    # Output format settings
    output = config['output']
    default_output = DEFAULT_CONFIG['output']
    
    if 'formats' not in output or not output['formats']:
        output['formats'] = default_output['formats']
    
    if 'generate_summary' not in output:
        output['generate_summary'] = default_output['generate_summary']


def main():
    """Main function to demonstrate usage"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('config_generator')
    
    # Generate default configuration
    config_path = 'config/analysis_config.json'
    success = generate_default_config(config_path, pretty=True, overwrite=False)
    
    if success:
        logger.info("Configuration generated successfully")
    else:
        logger.error("Failed to generate configuration")


if __name__ == "__main__":
    main() 