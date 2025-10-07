#!/usr/bin/env python3
"""
Database initialization script
Run this script to create the database tables and initial setup
"""

import sys
import os

# Add the project root to the path so we can import app modules
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from app.database.connection import init_database
from app.config import settings

def main():
    """Initialize the database"""
    print("Initializing database...")
    print(f"Database URL: {settings.database_url}")
    
    try:
        init_database()
        print("✅ Database initialized successfully!")
        print(f"✅ Upload directory created: {settings.upload_dir}")
        print(f"✅ Reports directory created: {settings.reports_dir}")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()