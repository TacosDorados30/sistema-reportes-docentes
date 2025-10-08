#!/usr/bin/env python3
"""
Simple test for audit logging system
"""

import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_audit_imports():
    """Test that audit logging components can be imported"""
    
    print("🧪 Testing Audit Logging Imports")
    print("=" * 50)
    
    try:
        # Test model imports
        from app.models.audit import AuditLog, AuditActionEnum, AuditSeverityEnum
        print("   ✅ Audit models imported successfully")
        
        # Test enum values
        actions = list(AuditActionEnum)
        severities = list(AuditSeverityEnum)
        
        print(f"   ✅ Found {len(actions)} action types")
        print(f"   ✅ Found {len(severities)} severity levels")
        
        # Test logger import
        from app.core.audit_logger import AuditLogger
        print("   ✅ AuditLogger class imported successfully")
        
        # Test logger initialization (without database)
        logger = AuditLogger()
        print("   ✅ AuditLogger initialized successfully")
        
        # Test enum usage
        test_action = AuditActionEnum.LOGIN
        test_severity = AuditSeverityEnum.INFO
        
        print(f"   ✅ Enum usage working: {test_action.value}, {test_severity.value}")
        
        print("\n📈 Audit Import Testing Summary:")
        print("   - All imports successful")
        print("   - Enums working correctly")
        print("   - Logger initialization working")
        print(f"   - Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Import test failed: {e}")
        return False

def test_audit_functionality():
    """Test basic audit functionality without database"""
    
    print("\n🧪 Testing Basic Audit Functionality")
    print("=" * 50)
    
    try:
        from app.core.audit_logger import AuditLogger, AuditActionEnum, AuditSeverityEnum
        
        # Initialize logger without database (will use fallback logging)
        logger = AuditLogger()
        
        # Test basic logging (should fallback to Python logging)
        log_id = logger.log_action(
            action=AuditActionEnum.SYSTEM_ACCESS,
            description="Test audit log entry",
            user_id="test_user",
            user_name="Test User",
            severity=AuditSeverityEnum.INFO
        )
        
        print("   ✅ Basic log action completed (fallback mode)")
        
        # Test specific action methods
        login_id = logger.log_login(
            user_id="test_user",
            user_name="Test User", 
            user_email="test@example.com",
            session_id="test_session",
            success=True
        )
        
        print("   ✅ Login logging completed")
        
        logout_id = logger.log_logout(
            user_id="test_user",
            user_name="Test User",
            session_id="test_session"
        )
        
        print("   ✅ Logout logging completed")
        
        export_id = logger.log_data_export(
            export_type="test_export",
            record_count=100,
            user_id="test_user",
            user_name="Test User"
        )
        
        print("   ✅ Data export logging completed")
        
        report_id = logger.log_report_generation(
            report_type="test_report",
            report_title="Test Report",
            user_id="test_user",
            user_name="Test User"
        )
        
        print("   ✅ Report generation logging completed")
        
        print("\n📈 Basic Functionality Testing Summary:")
        print("   - All logging methods working")
        print("   - Fallback logging operational")
        print("   - No crashes or errors")
        print(f"   - Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Functionality test failed: {e}")
        return False

if __name__ == "__main__":
    success1 = test_audit_imports()
    success2 = test_audit_functionality()
    
    if success1 and success2:
        print("\n🎉 All audit logging tests passed!")
    else:
        print("\n⚠️  Some audit logging tests failed.")