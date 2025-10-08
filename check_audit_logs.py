#!/usr/bin/env python3
"""
Check audit logs in database
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import SessionLocal
from sqlalchemy import text

def check_audit_logs():
    """Check recent audit logs"""
    
    db = SessionLocal()
    try:
        result = db.execute(text('SELECT * FROM audit_log ORDER BY fecha DESC LIMIT 10'))
        
        print("📋 Recent Audit Logs:")
        print("=" * 80)
        
        for row in result:
            print(f"ID: {row[0]}")
            print(f"Form ID: {row[1] or 'N/A'}")
            print(f"Action: {row[2]}")
            print(f"User: {row[3]}")
            print(f"Date: {row[4]}")
            print(f"Comment: {row[5]}")
            print("-" * 40)
        
    finally:
        db.close()

if __name__ == "__main__":
    check_audit_logs()