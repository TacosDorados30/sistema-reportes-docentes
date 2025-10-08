#!/usr/bin/env python3
"""
Debug import issues
"""

import sys
import os
import traceback

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Python path:", sys.path[0])
print("Current directory:", os.getcwd())

try:
    print("Testing individual imports...")
    
    # Test 1: Import audit models
    from app.models.audit import AuditLog, AuditActionEnum, AuditSeverityEnum
    print("✅ Audit models imported")
    
    # Test 2: Import database connection
    from app.database.connection import SessionLocal
    print("✅ Database connection imported")
    
    # Test 3: Import the module
    import app.core.audit_logger
    print("✅ Module imported")
    print("Module attributes:", dir(app.core.audit_logger))
    
    # Test 4: Try to access the class
    if hasattr(app.core.audit_logger, 'AuditLogger'):
        print("✅ AuditLogger class found")
        AuditLogger = app.core.audit_logger.AuditLogger
        logger = AuditLogger()
        print("✅ AuditLogger instance created")
    else:
        print("❌ AuditLogger class not found in module")
        
        # Let's see what's in the file
        with open('app/core/audit_logger.py', 'r') as f:
            content = f.read()
            print(f"File size: {len(content)} characters")
            print("First 500 characters:")
            print(content[:500])
            print("...")
            print("Last 500 characters:")
            print(content[-500:])
    
except Exception as e:
    print(f"❌ Error: {e}")
    traceback.print_exc()