import os
import streamlit as st
from typing import Optional, List
from pydantic_settings import BaseSettings

def get_streamlit_secret(key_path: str, default_value: str = None):
    """Get secret from Streamlit secrets or environment variable"""
    try:
        # Try to get from Streamlit secrets first
        keys = key_path.split(".")
        value = st.secrets
        for key in keys:
            value = value[key]
        return value
    except (KeyError, AttributeError):
        # Fallback to environment variable
        env_key = key_path.replace(".", "_").upper()
        return os.getenv(env_key, default_value)

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./data/reportes_docentes.db"
    database_pool_size: int = 5
    database_max_overflow: int = 10
    
    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    jwt_secret: str = "dev-jwt-secret-change-in-production"
    admin_password_hash: str = "$2b$12$example.hash.change.in.production"
    
    # Application
    app_name: str = "Sistema de Reportes Docentes"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    
    # API Configuration
    api_prefix: str = "/api"
    cors_origins: List[str] = ["*"]  # Configure properly for production
    
    # File Storage
    upload_dir: str = "uploads"
    reports_dir: str = "reports"
    data_dir: str = "data"
    logs_dir: str = "logs"
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    # Performance
    cache_ttl: int = 300  # 5 minutes
    max_concurrent_requests: int = 10
    request_timeout: int = 30
    
    # Email (optional)
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    email_user: str = ""
    email_password: str = ""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Override with Streamlit secrets if available
        try:
            self.database_url = get_streamlit_secret("database.DATABASE_URL", self.database_url)
            self.secret_key = get_streamlit_secret("auth.SECRET_KEY", self.secret_key)
            self.jwt_secret = get_streamlit_secret("auth.JWT_SECRET", self.jwt_secret)
            self.admin_password_hash = get_streamlit_secret("auth.ADMIN_PASSWORD_HASH", self.admin_password_hash)
            self.environment = get_streamlit_secret("app.ENVIRONMENT", self.environment)
            self.debug = get_streamlit_secret("app.DEBUG", str(self.debug)).lower() == "true"
            self.log_level = get_streamlit_secret("app.LOG_LEVEL", self.log_level)
            
            # Email configuration
            self.smtp_server = get_streamlit_secret("email.SMTP_SERVER", self.smtp_server)
            self.smtp_port = int(get_streamlit_secret("email.SMTP_PORT", str(self.smtp_port)))
            self.email_user = get_streamlit_secret("email.EMAIL_USER", self.email_user)
            self.email_password = get_streamlit_secret("email.EMAIL_PASSWORD", self.email_password)
            
        except Exception as e:
            # If Streamlit secrets are not available, use environment variables
            self.database_url = os.getenv("DATABASE_URL", self.database_url)
            self.secret_key = os.getenv("SECRET_KEY", self.secret_key)
            self.jwt_secret = os.getenv("JWT_SECRET", self.jwt_secret)
            self.admin_password_hash = os.getenv("ADMIN_PASSWORD_HASH", self.admin_password_hash)
            self.environment = os.getenv("ENVIRONMENT", self.environment)
            self.debug = os.getenv("DEBUG", str(self.debug)).lower() == "true"
            self.log_level = os.getenv("LOG_LEVEL", self.log_level)
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() == "development"
    
    def create_directories(self):
        """Create necessary directories"""
        directories = [
            self.upload_dir,
            self.reports_dir,
            self.data_dir,
            self.logs_dir
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Create necessary directories
settings.create_directories()