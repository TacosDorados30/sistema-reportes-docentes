import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./reportes_docentes.db"
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "admin123")
    
    # Application
    app_name: str = "Sistema de Reportes Docentes"
    app_version: str = "1.0.0"
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # API Configuration
    api_prefix: str = "/api"
    cors_origins: list = ["*"]  # Configure properly for production
    
    # File Storage
    upload_dir: str = "uploads"
    reports_dir: str = "reports"
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()