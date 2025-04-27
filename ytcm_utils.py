import logging
from logging import *
from logging.handlers import RotatingFileHandler
import os
from flask import request
from ytcm_consts import *

# Logger configuration
def setup_logger():
    # Create logs directory if it doesn't exist
    logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), YTCM_LOG_FILE_DIR))
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    logger = logging.getLogger(YTCM_LOGGER_NAME)
    logger.setLevel(logging.DEBUG if YTCM_DEBUG_MODE else logging.ERROR)
    
    # Remove any existing handlers to avoid duplicates
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
    
    try:
        # Handler for log file with error handling
        log_file_path = os.path.join(logs_dir, YTCM_LOG_FILE_NAME)
        file_handler = RotatingFileHandler(
            log_file_path, 
            maxBytes=YTCM_LOG_FILE_MAX_SIZE, 
            backupCount=YTCM_LOG_FILE_BACKUP_COUNT,
            delay=True  # Delay file opening until first log write
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: [%(ip)s] %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        logger.addHandler(file_handler)
    except (OSError, IOError) as e:
        # Fall back to console-only logging if file handler fails
        print(f"Warning: Could not set up file logging: {str(e)}")
    
    # Handler for console (always add this as a fallback)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: [%(ip)s] %(message)s'
    ))
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    
    # Ensure that the logger can handle extra attributes
    logging.LoggerAdapter(logger, {"ip": "N/A"})
    
    return logger

ytcm_logger: Logger = setup_logger()

def info_log(message, ip=None):
    global ytcm_logger
    if YTCM_TRACE_MODE:
        try:
            # Get the IP from the Flask request if not provided and if we are in a Flask context
            if ip is None and request:
                try:
                    ip = request.remote_addr
                except:
                    ip = "N/A"
            # If we still don't have an IP, use a default value
            if ip is None:
                ip = "N/A"
                
            # Add the IP as an extra to the log
            extra = {'ip': ip}
            ytcm_logger.info(message, extra=extra)
        except (OSError, IOError) as e:
            # Handle stale file handle errors during logging
            print(f"Logging error (handled): {str(e)}")
            # Attempt to reset logger handlers
            ytcm_logger = setup_logger()

def err_log(message, exc_info=YTCM_ERR_LOG_EXTRA_INFO, ip=None):
    global ytcm_logger
    if YTCM_DEBUG_MODE:
        try:
            # Get the IP from the Flask request if not provided and if we are in a Flask context
            if ip is None and request:
                try:
                    ip = request.remote_addr
                except:
                    ip = "N/A"
            # If we still don't have an IP, use a default value
            if ip is None:
                ip = "N/A"
                
            # Add the IP as an extra to the log
            extra = {'ip': ip}
            ytcm_logger.error(message, extra=extra)
        except (OSError, IOError) as log_err:
            # Handle stale file handle errors during error logging
            print(f"Logging error (handled): {str(log_err)}")
            # Attempt to reset logger handlers
            ytcm_logger = setup_logger()
