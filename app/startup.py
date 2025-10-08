"""
Application startup and initialization
"""

import os
import logging
from datetime import datetime

from app.config import settings
from app.database.connection import init_database
from app.database.optimization import db_optimizer
from app.core.logging_middleware import app_logger
from app.core.health_check import health_checker

def setup_logging():
    """Setup application logging"""
    
    # Create logs directory
    os.makedirs(settings.logs_dir, exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                os.path.join(settings.logs_dir, 'application.log'),
                encoding='utf-8'
            )
        ]
    )
    
    # Set specific logger levels
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.is_development else logging.WARNING
    )
    
    app_logger.log_operation("logging_configured", {"level": settings.log_level})

def initialize_database():
    """Initialize and optimize database"""
    
    try:
        app_logger.log_operation("database_initialization_started")
        
        # Initialize database tables
        init_database()
        
        # Run optimization if in production or if explicitly requested
        if settings.is_production or os.getenv("OPTIMIZE_DB", "false").lower() == "true":
            app_logger.log_operation("database_optimization_started")
            db_optimizer.optimize_database()
        
        app_logger.log_operation("database_initialization_completed")
        
    except Exception as e:
        app_logger.log_operation(
            "database_initialization_failed",
            {"error": str(e)},
            "ERROR"
        )
        raise

def create_required_directories():
    """Create all required directories"""
    
    directories = [
        settings.data_dir,
        settings.logs_dir,
        settings.reports_dir,
        settings.upload_dir
    ]
    
    created_dirs = []
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            created_dirs.append(directory)
        except Exception as e:
            app_logger.log_operation(
                "directory_creation_failed",
                {"directory": directory, "error": str(e)},
                "ERROR"
            )
    
    app_logger.log_operation(
        "directories_created",
        {"directories": created_dirs}
    )

def validate_configuration():
    """Validate application configuration"""
    
    issues = []
    
    # Check critical configuration
    if settings.is_production:
        if settings.secret_key == "dev-secret-key-change-in-production":
            issues.append("Using default secret key in production")
        
        if settings.debug:
            issues.append("Debug mode enabled in production")
        
        if not settings.database_url or "sqlite:///" in settings.database_url:
            issues.append("Using SQLite in production (consider PostgreSQL)")
    
    # Check database URL
    if not settings.database_url:
        issues.append("Database URL not configured")
    
    # Log configuration issues
    if issues:
        app_logger.log_operation(
            "configuration_issues_detected",
            {"issues": issues},
            "WARNING"
        )
    else:
        app_logger.log_operation("configuration_validated")
    
    return issues

def startup_application():
    """Complete application startup sequence"""
    
    startup_start = datetime.utcnow()
    
    try:
        app_logger.log_operation(
            "application_startup_started",
            {
                "environment": settings.environment,
                "version": settings.app_version,
                "debug": settings.debug
            }
        )
        
        # 1. Setup logging
        setup_logging()
        
        # 2. Create directories
        create_required_directories()
        
        # 3. Validate configuration
        config_issues = validate_configuration()
        
        # 4. Initialize database
        initialize_database()
        
        # 5. Initialize health checker
        health_status = health_checker.get_system_health()
        
        startup_duration = (datetime.utcnow() - startup_start).total_seconds()
        
        app_logger.log_operation(
            "application_startup_completed",
            {
                "duration_seconds": startup_duration,
                "health_status": health_status["status"],
                "configuration_issues": len(config_issues)
            }
        )
        
        return {
            "status": "success",
            "duration": startup_duration,
            "health_status": health_status["status"],
            "configuration_issues": config_issues
        }
        
    except Exception as e:
        startup_duration = (datetime.utcnow() - startup_start).total_seconds()
        
        app_logger.log_operation(
            "application_startup_failed",
            {
                "duration_seconds": startup_duration,
                "error": str(e)
            },
            "ERROR"
        )
        
        raise

def shutdown_application():
    """Application shutdown sequence"""
    
    try:
        app_logger.log_operation("application_shutdown_started")
        
        # Perform any cleanup tasks here
        # - Close database connections
        # - Save any pending data
        # - Clean up temporary files
        
        app_logger.log_operation("application_shutdown_completed")
        
    except Exception as e:
        app_logger.log_operation(
            "application_shutdown_failed",
            {"error": str(e)},
            "ERROR"
        )

if __name__ == "__main__":
    # Run startup when script is executed directly
    result = startup_application()
    print(f"Application startup completed: {result}")