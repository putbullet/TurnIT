"""
Logging utility for TurnIT application
"""

import logging
import os
from pathlib import Path
from datetime import datetime

def setup_logging():
    """Setup application logging"""
    
    # Create logs directory
    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Create log filename with timestamp
    log_filename = f"turnit_{datetime.now().strftime('%Y%m%d')}.log"
    log_path = logs_dir / log_filename
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()  # Also log to console
        ]
    )
    
    # Create logger for the application
    logger = logging.getLogger('turnit')
    logger.info(f"Logging initialized. Log file: {log_path}")
    
    return logger

def get_logger(name):
    """Get a logger instance for a specific module"""
    return logging.getLogger(name)
