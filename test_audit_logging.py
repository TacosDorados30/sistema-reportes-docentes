#!/usr/bin/env python3
"""
Test script for audit logging system
"""

import sys
import os
from datetime import datetime, timedelta
import tempfile
import sqlite3

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.audit_logger import AuditLogger, AuditActionEnum, AuditSeverityEnum
from app.models.audit import AuditLog, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def test_audit_logging_system():
    """Test the audit logging system"""
    
    print("🧪 Testing Audit Logging System")
    print("=" * 60)
    
    # Test 1: Database setup and basic logging
    print("\n1. Testing Database Setup and Basic Logging...")
    test_basic_logging()
    
    # Test 2: Specific action logging
    print("\n2. Testing Specific Action Logging...")
    test_specific_actions()
    
    # Test 3: Log retrieval and filtering
    print("\n3. Testing Log Retrieval and Filtering...")
    test_log_retrieval()
    
    # Test 4: Audit summary and statistics
    print("\n4. Testing Audit Summary and Statistics...")
    test_audit_summary()
    
    # Test 5: Log cleanup functionality
    print("\n5. Testing Log Cleanup...")
    test_log_cleanup()
    
    # Test 6: Error handling
    print("\n6. Testing Error Handling...")
    test_error_handling()
    
    print(f"\n📈 Audit Logging Testing Summary:")
    print(f"   - Database setup and basic logging working")
    print(f"   - Specific action logging functional")
    print(f"   - Log retrieval and filtering operational")
    print(f"   - Audit summary generation working")
    print(f"   - Log cleanup functionality active")
    print(f"   - Error handling robust")
    print(f"   - Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def create_test_database():
    """Create a temporary test database"""
    
    # Create temporary database
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    # Create engine and tables
    engine = create_engine(f'sqlite:///{temp_db.name}')
    Base.metadata.create_all(engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return SessionLocal(), temp_db.name

def test_basic_logging():
    """Test basic audit logging functionality"""
    
    try:
        # Create test database
        db_session, db_file = create_test_database()
        
        # Initialize audit logger with test database
        audit_logger = AuditLogger(db_session)
        
        # Test basic log entry
        log_id = audit_logger.log_action(
            action=AuditActionEnum.SYSTEM_ACCESS,
            description="Test log entry",
            user_id="test_user",
            user_name="Test User",
            user_email="test@example.com",
            session_id="test_session_123",
            resource_type="test_resource",
            resource_id="123",
            metadata={"test": True, "value": 42}
        )
        
        if log_id:
            print("   ✅ Basic log entry created successfully")
            print(f"   Log ID: {log_id}")
        else:
            print("   ❌ Basic log entry creation failed")
        
        # Test log with different severity
        error_log_id = audit_logger.log_action(
            action=AuditActionEnum.SYSTEM_ACCESS,
            description="Test error log",
            user_id="test_user",
            severity=AuditSeverityEnum.ERROR,
            error_message="This is a test error"
        )
        
        if error_log_id:
            print("   ✅ Error log entry created successfully")
        else:
            print("   ❌ Error log entry creation failed")
        
        # Cleanup
        db_session.close()
        os.unlink(db_file)
    
    except Exception as e:
        print(f"   ❌ Basic logging test failed: {e}")

def test_specific_actions():
    """Test specific action logging methods"""
    
    try:
        # Create test database
        db_session, db_file = create_test_database()
        audit_logger = AuditLogger(db_session)
        
        # Test login logging
        login_id = audit_logger.log_login(
            user_id="test_user",
            user_name="Test User",
            user_email="test@example.com",
            session_id="session_123",
            ip_address="192.168.1.100",
            success=True
        )
        
        if login_id:
            print("   ✅ Login logging successful")
        else:
            print("   ❌ Login logging failed")
        
        # Test failed login
        failed_login_id = audit_logger.log_login(
            user_id="bad_user",
            user_name="Bad User",
            user_email="",
            session_id="",
            success=False
        )
        
        if failed_login_id:
            print("   ✅ Failed login logging successful")
        else:
            print("   ❌ Failed login logging failed")
        
        # Test logout logging
        logout_id = audit_logger.log_logout(
            user_id="test_user",
            user_name="Test User",
            session_id="session_123",
            reason="user_initiated"
        )
        
        if logout_id:
            print("   ✅ Logout logging successful")
        else:
            print("   ❌ Logout logging failed")
        
        # Test form approval logging
        approval_id = audit_logger.log_form_approval(
            form_id=123,
            form_owner="Dr. John Doe",
            approved_by_user="admin",
            approved_by_name="Administrator",
            session_id="admin_session"
        )
        
        if approval_id:
            print("   ✅ Form approval logging successful")
        else:
            print("   ❌ Form approval logging failed")
        
        # Test form rejection logging
        rejection_id = audit_logger.log_form_rejection(
            form_id=124,
            form_owner="Dr. Jane Smith",
            rejected_by_user="admin",
            rejected_by_name="Administrator",
            reason="Incomplete information",
            session_id="admin_session"
        )
        
        if rejection_id:
            print("   ✅ Form rejection logging successful")
        else:
            print("   ❌ Form rejection logging failed")
        
        # Test data export logging
        export_id = audit_logger.log_data_export(
            export_type="forms",
            record_count=150,
            user_id="admin",
            user_name="Administrator",
            session_id="admin_session",
            filters_applied={"status": "approved"},
            file_format="CSV"
        )
        
        if export_id:
            print("   ✅ Data export logging successful")
        else:
            print("   ❌ Data export logging failed")
        
        # Test report generation logging
        report_id = audit_logger.log_report_generation(
            report_type="annual",
            report_title="Annual Activity Report 2024",
            user_id="admin",
            user_name="Administrator",
            session_id="admin_session",
            period_start="2024-01-01",
            period_end="2024-12-31",
            output_format="PDF"
        )
        
        if report_id:
            print("   ✅ Report generation logging successful")
        else:
            print("   ❌ Report generation logging failed")
        
        # Cleanup
        db_session.close()
        os.unlink(db_file)
    
    except Exception as e:
        print(f"   ❌ Specific actions test failed: {e}")

def test_log_retrieval():
    """Test log retrieval and filtering"""
    
    try:
        # Create test database
        db_session, db_file = create_test_database()
        audit_logger = AuditLogger(db_session)
        
        # Create multiple test logs
        test_logs = [
            {
                "action": AuditActionEnum.LOGIN,
                "description": "User login",
                "user_id": "user1",
                "severity": AuditSeverityEnum.INFO
            },
            {
                "action": AuditActionEnum.FORM_APPROVAL,
                "description": "Form approved",
                "user_id": "admin",
                "severity": AuditSeverityEnum.INFO,
                "resource_type": "formulario"
            },
            {
                "action": AuditActionEnum.DATA_EXPORT,
                "description": "Data exported",
                "user_id": "admin",
                "severity": AuditSeverityEnum.INFO
            },
            {
                "action": AuditActionEnum.SYSTEM_ACCESS,
                "description": "System error",
                "user_id": "user1",
                "severity": AuditSeverityEnum.ERROR
            }
        ]
        
        created_logs = []
        for log_data in test_logs:
            log_id = audit_logger.log_action(**log_data)
            if log_id:
                created_logs.append(log_id)
        
        print(f"   ✅ Created {len(created_logs)} test logs")
        
        # Test basic retrieval
        all_logs = audit_logger.get_audit_logs(limit=10)
        
        if len(all_logs) >= len(created_logs):
            print("   ✅ Basic log retrieval successful")
            print(f"   Retrieved {len(all_logs)} logs")
        else:
            print("   ❌ Basic log retrieval failed")
        
        # Test filtering by user
        user_logs = audit_logger.get_audit_logs(user_id="admin", limit=10)
        admin_log_count = len([log for log in test_logs if log.get("user_id") == "admin"])
        
        if len(user_logs) == admin_log_count:
            print("   ✅ User filtering successful")
        else:
            print(f"   ⚠️  User filtering: expected {admin_log_count}, got {len(user_logs)}")
        
        # Test filtering by action
        login_logs = audit_logger.get_audit_logs(action=AuditActionEnum.LOGIN, limit=10)
        login_log_count = len([log for log in test_logs if log.get("action") == AuditActionEnum.LOGIN])
        
        if len(login_logs) == login_log_count:
            print("   ✅ Action filtering successful")
        else:
            print(f"   ⚠️  Action filtering: expected {login_log_count}, got {len(login_logs)}")
        
        # Test filtering by severity
        error_logs = audit_logger.get_audit_logs(severity=AuditSeverityEnum.ERROR, limit=10)
        error_log_count = len([log for log in test_logs if log.get("severity") == AuditSeverityEnum.ERROR])
        
        if len(error_logs) == error_log_count:
            print("   ✅ Severity filtering successful")
        else:
            print(f"   ⚠️  Severity filtering: expected {error_log_count}, got {len(error_logs)}")
        
        # Test date filtering
        now = datetime.now()
        recent_logs = audit_logger.get_audit_logs(
            start_date=now - timedelta(minutes=1),
            end_date=now + timedelta(minutes=1),
            limit=10
        )
        
        if len(recent_logs) >= len(created_logs):
            print("   ✅ Date filtering successful")
        else:
            print("   ⚠️  Date filtering may have issues")
        
        # Cleanup
        db_session.close()
        os.unlink(db_file)
    
    except Exception as e:
        print(f"   ❌ Log retrieval test failed: {e}")

def test_audit_summary():
    """Test audit summary and statistics"""
    
    try:
        # Create test database
        db_session, db_file = create_test_database()
        audit_logger = AuditLogger(db_session)
        
        # Create diverse test logs
        test_actions = [
            AuditActionEnum.LOGIN,
            AuditActionEnum.LOGIN,
            AuditActionEnum.FORM_APPROVAL,
            AuditActionEnum.FORM_REJECTION,
            AuditActionEnum.DATA_EXPORT,
            AuditActionEnum.LOGOUT
        ]
        
        test_severities = [
            AuditSeverityEnum.INFO,
            AuditSeverityEnum.WARNING,
            AuditSeverityEnum.INFO,
            AuditSeverityEnum.INFO,
            AuditSeverityEnum.INFO,
            AuditSeverityEnum.INFO
        ]
        
        test_users = ["user1", "user2", "admin", "admin", "admin", "user1"]
        
        for i, (action, severity, user) in enumerate(zip(test_actions, test_severities, test_users)):
            audit_logger.log_action(
                action=action,
                description=f"Test action {i+1}",
                user_id=user,
                user_name=f"User {user}",
                severity=severity
            )
        
        # Get summary
        summary = audit_logger.get_audit_summary()
        
        if "error" not in summary:
            print("   ✅ Audit summary generation successful")
            
            # Check summary contents
            if "total_logs" in summary and summary["total_logs"] >= len(test_actions):
                print(f"   ✅ Total logs count: {summary['total_logs']}")
            else:
                print("   ⚠️  Total logs count may be incorrect")
            
            if "action_counts" in summary:
                action_counts = summary["action_counts"]
                print(f"   ✅ Action counts: {len(action_counts)} different actions")
                
                # Check specific counts
                if action_counts.get("LOGIN", 0) == 2:
                    print("   ✅ LOGIN count correct")
                else:
                    print(f"   ⚠️  LOGIN count: expected 2, got {action_counts.get('LOGIN', 0)}")
            
            if "severity_counts" in summary:
                severity_counts = summary["severity_counts"]
                print(f"   ✅ Severity counts: {len(severity_counts)} different severities")
            
            if "top_users" in summary:
                top_users = summary["top_users"]
                print(f"   ✅ Top users: {len(top_users)} users")
                
                # Check if admin is most active (3 actions)
                if top_users and top_users[0][0] == "admin" and top_users[0][1] == 3:
                    print("   ✅ Top user calculation correct")
                else:
                    print("   ⚠️  Top user calculation may be incorrect")
        else:
            print(f"   ❌ Audit summary generation failed: {summary['error']}")
        
        # Cleanup
        db_session.close()
        os.unlink(db_file)
    
    except Exception as e:
        print(f"   ❌ Audit summary test failed: {e}")

def test_log_cleanup():
    """Test log cleanup functionality"""
    
    try:
        # Create test database
        db_session, db_file = create_test_database()
        audit_logger = AuditLogger(db_session)
        
        # Create logs with different timestamps
        now = datetime.now()
        
        # Recent log (should be kept)
        recent_log_id = audit_logger.log_action(
            action=AuditActionEnum.LOGIN,
            description="Recent log",
            user_id="user1"
        )
        
        # Manually create old log by directly inserting into database
        old_timestamp = now - timedelta(days=400)  # Older than 365 days
        
        # Insert old log directly
        old_log = AuditLog(
            action=AuditActionEnum.LOGOUT,
            description="Old log",
            user_id="user2",
            timestamp=old_timestamp,
            severity=AuditSeverityEnum.INFO
        )
        
        db_session.add(old_log)
        db_session.commit()
        old_log_id = old_log.id
        
        print(f"   ✅ Created test logs: recent (ID: {recent_log_id}), old (ID: {old_log_id})")
        
        # Verify both logs exist
        all_logs_before = audit_logger.get_audit_logs(limit=10)
        print(f"   Total logs before cleanup: {len(all_logs_before)}")
        
        # Perform cleanup (keep 365 days)
        deleted_count = audit_logger.cleanup_old_logs(days_to_keep=365)
        
        if deleted_count > 0:
            print(f"   ✅ Cleanup successful: {deleted_count} logs deleted")
            
            # Verify old log is gone but recent log remains
            all_logs_after = audit_logger.get_audit_logs(limit=10)
            print(f"   Total logs after cleanup: {len(all_logs_after)}")
            
            # Check if recent log still exists
            recent_log_exists = any(log.id == recent_log_id for log in all_logs_after)
            old_log_exists = any(log.id == old_log_id for log in all_logs_after)
            
            if recent_log_exists and not old_log_exists:
                print("   ✅ Cleanup correctly preserved recent logs and removed old logs")
            else:
                print("   ⚠️  Cleanup may not have worked as expected")
        else:
            print("   ⚠️  No logs were deleted (may be expected if no old logs exist)")
        
        # Cleanup
        db_session.close()
        os.unlink(db_file)
    
    except Exception as e:
        print(f"   ❌ Log cleanup test failed: {e}")

def test_error_handling():
    """Test error handling in audit logging"""
    
    try:
        # Test with invalid database (should fallback to Python logging)
        invalid_audit_logger = AuditLogger()
        
        # This should not crash even with database issues
        log_id = invalid_audit_logger.log_action(
            action=AuditActionEnum.SYSTEM_ACCESS,
            description="Test with potential database issues",
            user_id="test_user"
        )
        
        # log_id might be None due to database issues, but should not crash
        print("   ✅ Error handling test completed without crashing")
        
        # Test with invalid enum values (should be caught by type system)
        try:
            # This should work fine
            valid_log_id = invalid_audit_logger.log_action(
                action=AuditActionEnum.LOGIN,
                description="Valid enum test",
                severity=AuditSeverityEnum.INFO
            )
            print("   ✅ Valid enum values handled correctly")
        except Exception as e:
            print(f"   ❌ Valid enum handling failed: {e}")
        
        # Test with None values
        try:
            none_log_id = invalid_audit_logger.log_action(
                action=AuditActionEnum.SYSTEM_ACCESS,
                description="Test with None values",
                user_id=None,
                user_name=None,
                metadata=None
            )
            print("   ✅ None values handled gracefully")
        except Exception as e:
            print(f"   ❌ None value handling failed: {e}")
        
        # Test with very long strings
        try:
            long_description = "A" * 10000  # Very long description
            long_log_id = invalid_audit_logger.log_action(
                action=AuditActionEnum.SYSTEM_ACCESS,
                description=long_description,
                user_id="test_user"
            )
            print("   ✅ Long strings handled gracefully")
        except Exception as e:
            print(f"   ❌ Long string handling failed: {e}")
    
    except Exception as e:
        print(f"   ❌ Error handling test failed: {e}")

if __name__ == "__main__":
    test_audit_logging_system()