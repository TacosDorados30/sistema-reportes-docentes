from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from app.config import settings
from app.models.database import Base
import os
import logging

# Silenciar logs de SQLAlchemy para mejor rendimiento
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.dialects').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.orm').setLevel(logging.WARNING)

# Import audit models to register them with SQLAlchemy
from app.models import audit

# Import database monitoring
# from app.core.database_monitor import db_monitor  # Removed for optimization

# Create database engine (optimized for performance)
if settings.database_url.startswith("sqlite"):
    # SQLite specific configuration - optimized for production
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,  # Silenciar logs para mejor rendimiento
        logging_name="sqlalchemy.engine"
    )
else:
    # For other databases (PostgreSQL, MySQL, etc.)
    engine = create_engine(
        settings.database_url,
        echo=False  # Silenciar logs para mejor rendimiento
    )

# Database monitoring removed for optimization

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database with tables and initial data if needed"""
    # Create tables
    create_tables()
    
    # Create directories for file storage
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.reports_dir, exist_ok=True)
    
    # print("Database initialized successfully")  # Silenciado para terminal limpia

if __name__ == "__main__":
    init_database()