import logging.config
import os
from app.dependencies import get_settings

settings = get_settings()

# Utility functions for common operations
def is_empty(val):
    return val == "" or val == [] or val is None

def safe_get(d, key, default=None):
    return d.get(key, default) if isinstance(d, dict) else default

def setup_logging():
    """
    Sets up logging for the application using a configuration file.
    This ensures standardized logging across the entire application.
    """
    # Construct the path to 'logging.conf', assuming it's in the project's root.
    logging_config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'logging.conf')
    # Normalize the path to handle any '..' correctly.
    normalized_path = os.path.normpath(logging_config_path)
    # Apply the logging configuration.
    logging.config.fileConfig(normalized_path, disable_existing_loggers=False)