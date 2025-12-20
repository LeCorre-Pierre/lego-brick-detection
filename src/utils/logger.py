"""
Logging configuration for Lego Brick Detection application.
"""

import logging
import sys
from pathlib import Path

# Create logs directory if it doesn't exist
logs_dir = Path(__file__).parent.parent.parent / "logs"
logs_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / "lego_detector.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Create logger for the application
logger = logging.getLogger("lego_detector")

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module."""
    return logging.getLogger(f"lego_detector.{name}")