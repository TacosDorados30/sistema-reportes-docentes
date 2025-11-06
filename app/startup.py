"""
Application startup - Optimized version
"""

import os
import logging
from datetime import datetime

from app.config import settings
from app.database.connection import init_database
from app.core.logging_middleware import app_logger

def setup_logging():
    """Setup minimal logging for performance"""
    os.makedirs(settings.logs_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.WARNING,  # Only warnings and errors
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(
                os.path.join(settings.logs_dir, 'application.log'),
                encoding='utf-8'
            )
        ]
    )
    
    # Silence SQLAlchemy logs for performance
    for logger_name in ["sqlalchemy.engine", "sqlalchemy.dialects", "sqlalchemy.pool", "sqlalchemy.orm"]:
        logging.getLogger(logger_name).setLevel(logging.ERROR)

def initialize_database():
    """Initialize database silently"""
    try:
        init_database()
    except Exception as e:
        app_logger.log_operation("database_init_failed", {"error": str(e)}, "ERROR")
        raise

def create_required_directories():
    """Create required directories silently"""
    directories = [settings.data_dir, settings.logs_dir, settings.reports_dir, settings.upload_dir]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            app_logger.log_operation("dir_creation_failed", {"dir": directory, "error": str(e)}, "ERROR")

def validate_configuration():
    """Quick configuration validation"""
    issues = []
    
    if settings.is_production:
        if settings.secret_key == "dev-secret-key-change-in-production":
            issues.append("Default secret key in production")
        if not settings.database_url or "sqlite:///" in settings.database_url:
            issues.append("SQLite in production")
    
    return issues

def startup_application():
    """Optimized startup sequence"""
    try:
        setup_logging()
        create_required_directories()
        config_issues = validate_configuration()
        initialize_database()
        
        return {
            "status": "success",
            "configuration_issues": config_issues
        }
        
    except Exception as e:
        app_logger.log_operation("startup_failed", {"error": str(e)}, "ERROR")
        raise

def shutdown_application():
    """Minimal shutdown sequence"""
    try:
        app_logger.log_operation("shutdown_completed")
    except Exception as e:
        app_logger.log_operation("shutdown_failed", {"error": str(e)}, "ERROR")

if __name__ == "__main__":
    result = startup_application()
    print(f"Startup completed: {result['status']}")