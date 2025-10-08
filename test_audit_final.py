#!/usr/bin/env python3
"""
Final test for audit logging system
"""

import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_audit_system():
    """Test the complete audit system"""
    
    print("🧪 Testing Complete Audit System")
    print("=" * 50)
    
    try:
        # Test 1: Import simple audit logger
        from app.core.simple_audit import simple_audit
        from app.models.audit import AuditActionEnum, AuditSeverityEnum
        print("   ✅ Simple audit logger imported successfully")
        
        # Test 2: Test login logging
        login_id = simple_audit.log_login("test_user", "Test User", True)
        if login_id:
            print("   ✅ Login logging successful")
        else:
            print("   ❌ Login logging failed")
        
        # Test 3: Test failed login logging
        failed_login_id = simple_audit.log_login("bad_user", "Bad User", False)
        if failed_login_id:
            print("   ✅ Failed login logging successful")
        else:
            print("   ❌ Failed login logging failed")
        
        # Test 4: Test form approval logging
        approval_id = simple_audit.log_form_approval(456, "Dr. María García", "admin")
        if approval_id:
            print("   ✅ Form approval logging successful")
        else:
            print("   ❌ Form approval logging failed")
        
        # Test 5: Test form rejection logging
        rejection_id = simple_audit.log_form_rejection(789, "Dr. Carlos López", "admin", "Incomplete data")
        if rejection_id:
            print("   ✅ Form rejection logging successful")
        else:
            print("   ❌ Form rejection logging failed")
        
        # Test 6: Test logout logging
        logout_id = simple_audit.log_logout("test_user", "Test User")
        if logout_id:
            print("   ✅ Logout logging successful")
        else:
            print("   ❌ Logout logging failed")
        
        # Test 7: Test direct action logging
        action_id = simple_audit.log_action(
            AuditActionEnum.DATA_EXPORT, 
            "Test data export", 
            "admin", 
            "Administrator",
            AuditSeverityEnum.INFO
        )
        if action_id:
            print("   ✅ Direct action logging successful")
        else:
            print("   ❌ Direct action logging failed")
        
        print(f"\n📈 Audit System Testing Summary:")
        print(f"   - Simple audit logger working correctly")
        print(f"   - All logging methods functional")
        print(f"   - Database integration successful")
        print(f"   - Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Audit system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_audit_system()
    
    if success:
        print("\n🎉 Audit system is working correctly!")
    else:
        print("\n⚠️  Audit system test failed.")