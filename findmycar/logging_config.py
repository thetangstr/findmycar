"""
Simple logging configuration for AutoNavigator
"""
import logging
import sys

class ExternalAPIError(Exception):
    """Custom exception for external API errors"""
    pass

class APIError(Exception):
    """Custom exception for API errors"""
    pass

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

def get_logger(name):
    """Get a logger with basic configuration"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger

def log_error(logger, message, exception=None):
    """Log an error message with optional exception details"""
    if exception:
        logger.error(f"{message}: {str(exception)}")
    else:
        logger.error(message)

def setup_logging():
    """Setup basic logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger('autonavigator')