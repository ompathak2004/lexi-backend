import logging
import sys
from datetime import datetime
from app.config import get_settings

def setup_logging():
    """Configure logging for the application"""
    settings = get_settings()
    
    class CustomFormatter(logging.Formatter):
        def format(self, record):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            level_colors = {
                'DEBUG': '\033[36m',    # Cyan
                'INFO': '\033[32m',     # Green  
                'WARNING': '\033[33m',  # Yellow
                'ERROR': '\033[31m',    # Red
                'CRITICAL': '\033[35m', # Magenta
            }
            reset_color = '\033[0m'
            
            level_name = record.levelname
            color = level_colors.get(level_name, '')
            
            # Format: [TIMESTAMP] [LEVEL] [MODULE] MESSAGE
            formatted_message = f"[{timestamp}] {color}[{level_name}]{reset_color} [{record.name}] {record.getMessage()}"
            return formatted_message
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler with UTF-8 encoding
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    console_handler.setFormatter(CustomFormatter())
    # Set UTF-8 encoding for Windows compatibility
    if hasattr(console_handler.stream, 'reconfigure'):
        try:
            console_handler.stream.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass
    root_logger.addHandler(console_handler)
    
    # File handler for detailed logs with UTF-8 encoding
    file_handler = logging.FileHandler('jagriti_api.log', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger("httpx").setLevel(logging.WARNING)  
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    
    return root_logger

logger = setup_logging()