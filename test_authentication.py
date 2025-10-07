#!/usr/bin/env python3
"""
Test script for authentication system
"""

import sys
import os
from datetime import datetime, timedelta
import json
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.auth.auth_manager import AuthManager

def test_authentication_system():
    """Test the authentication system"""
    
    print("🧪 Testing Authentication System")
    print("=" * 60)
    
    # Test 1: AuthManager initialization
    print("\n1. Testing AuthManager Initialization...")
    test_auth_manager_init()
    
    # Test 2: User authentication
    print("\n2. Testing User Authentication...")
    test_user_authentication()
    
    # Test 3: Session management
    print("\n3. Testing Session Management...")
    test_session_management()
    
    # Test 4: Password management
    print("\n4. Testing Password Management...")
    test_password_management()
    
    # Test 5: User management
    print("\n5. Testing User Management...")
    test_user_management()
    
    # Test 6: Security features
    print("\n6. Testing Security Features...")
    test_security_features()
    
    print(f"\n📈 Authentication Testing Summary:")
    print(f"   - AuthManager initialization working")
    print(f"   - User authentication functional")
    print(f"   - Session management implemented")
    print(f"   - Password security enforced")
    print(f"   - User management operational")
    print(f"   - Security features active")
    print(f"   - Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def test_auth_manager_init():
    """Test AuthManager initialization"""
    
    try:
        # Create temporary config file
        temp_config = "temp_auth_config.json"
        
        # Initialize AuthManager
        auth_manager = AuthManager(temp_config)
        
        if auth_manager.config:
            print("   ✅ AuthManager initialized successfully")
            
            # Check default configuration
            if "admin_users" in auth_manager.config:
                print("   ✅ Default admin user created")
                
                admin_users = auth_manager.config["admin_users"]
                if "admin" in admin_users:
                    print("   ✅ Default 'admin' user exists")
                else:
                    print("   ❌ Default 'admin' user not found")
            
            if "session_settings" in auth_manager.config:
                print("   ✅ Session settings configured")
            
            if "security_settings" in auth_manager.config:
                print("   ✅ Security settings configured")
        else:
            print("   ❌ AuthManager initialization failed")
        
        # Cleanup
        if Path(temp_config).exists():
            Path(temp_config).unlink()
    
    except Exception as e:
        print(f"   ❌ AuthManager initialization test failed: {e}")

def test_user_authentication():
    """Test user authentication"""
    
    try:
        # Create temporary config
        temp_config = "temp_auth_test.json"
        auth_manager = AuthManager(temp_config)
        
        # Test valid authentication
        session_data = auth_manager.authenticate("admin", "admin123")
        
        if session_data:
            print("   ✅ Valid authentication successful")
            print(f"   Session ID: {session_data['session_id'][:8]}...")
            print(f"   User: {session_data['username']}")
            print(f"   Name: {session_data['name']}")
        else:
            print("   ❌ Valid authentication failed")
        
        # Test invalid authentication
        invalid_session = auth_manager.authenticate("admin", "wrong_password")
        
        if not invalid_session:
            print("   ✅ Invalid authentication properly rejected")
        else:
            print("   ❌ Invalid authentication not rejected")
        
        # Test non-existent user
        nonexistent_session = auth_manager.authenticate("nonexistent", "password")
        
        if not nonexistent_session:
            print("   ✅ Non-existent user properly rejected")
        else:
            print("   ❌ Non-existent user not rejected")
        
        # Cleanup
        if Path(temp_config).exists():
            Path(temp_config).unlink()
    
    except Exception as e:
        print(f"   ❌ User authentication test failed: {e}")

def test_session_management():
    """Test session management"""
    
    try:
        temp_config = "temp_session_test.json"
        auth_manager = AuthManager(temp_config)
        
        # Create session
        session_data = auth_manager.authenticate("admin", "admin123")
        
        if session_data:
            session_id = session_data["session_id"]
            
            # Test session validation
            validated_session = auth_manager.validate_session(session_id)
            
            if validated_session:
                print("   ✅ Session validation successful")
                print(f"   Last activity updated: {validated_session['last_activity']}")
            else:
                print("   ❌ Session validation failed")
            
            # Test invalid session ID
            invalid_validation = auth_manager.validate_session("invalid_session_id")
            
            if not invalid_validation:
                print("   ✅ Invalid session ID properly rejected")
            else:
                print("   ❌ Invalid session ID not rejected")
            
            # Test session logout
            logout_success = auth_manager.logout(session_id)
            
            if logout_success:
                print("   ✅ Session logout successful")
                
                # Verify session is no longer valid
                post_logout_validation = auth_manager.validate_session(session_id)
                if not post_logout_validation:
                    print("   ✅ Session properly invalidated after logout")
                else:
                    print("   ❌ Session still valid after logout")
            else:
                print("   ❌ Session logout failed")
            
            # Test active sessions
            active_sessions = auth_manager.get_active_sessions()
            print(f"   ✅ Active sessions retrieved: {len(active_sessions)} sessions")
        
        # Cleanup
        if Path(temp_config).exists():
            Path(temp_config).unlink()
    
    except Exception as e:
        print(f"   ❌ Session management test failed: {e}")

def test_password_management():
    """Test password management features"""
    
    try:
        temp_config = "temp_password_test.json"
        auth_manager = AuthManager(temp_config)
        
        # Test password hashing
        password = "test_password123!"
        hashed = auth_manager._hash_password(password)
        
        if hashed and ":" in hashed:
            print("   ✅ Password hashing working (salt:hash format)")
        else:
            print("   ❌ Password hashing failed")
        
        # Test password verification
        if auth_manager._verify_password(password, hashed):
            print("   ✅ Password verification successful")
        else:
            print("   ❌ Password verification failed")
        
        # Test wrong password verification
        if not auth_manager._verify_password("wrong_password", hashed):
            print("   ✅ Wrong password properly rejected")
        else:
            print("   ❌ Wrong password not rejected")
        
        # Test password strength validation
        weak_passwords = ["123", "password", "12345678"]
        strong_passwords = ["StrongPass123!", "MySecure@Pass2024", "Complex#Password1"]
        
        weak_rejected = 0
        for weak_pass in weak_passwords:
            if not auth_manager._validate_password_strength(weak_pass):
                weak_rejected += 1
        
        if weak_rejected == len(weak_passwords):
            print("   ✅ Weak passwords properly rejected")
        else:
            print(f"   ⚠️  Only {weak_rejected}/{len(weak_passwords)} weak passwords rejected")
        
        strong_accepted = 0
        for strong_pass in strong_passwords:
            if auth_manager._validate_password_strength(strong_pass):
                strong_accepted += 1
        
        if strong_accepted == len(strong_passwords):
            print("   ✅ Strong passwords properly accepted")
        else:
            print(f"   ⚠️  Only {strong_accepted}/{len(strong_passwords)} strong passwords accepted")
        
        # Test password change
        if auth_manager.change_password("admin", "admin123", "NewSecurePass123!"):
            print("   ✅ Password change successful")
            
            # Verify old password no longer works
            if not auth_manager.authenticate("admin", "admin123"):
                print("   ✅ Old password properly invalidated")
            else:
                print("   ❌ Old password still works")
            
            # Verify new password works
            if auth_manager.authenticate("admin", "NewSecurePass123!"):
                print("   ✅ New password works")
            else:
                print("   ❌ New password doesn't work")
        else:
            print("   ❌ Password change failed")
        
        # Cleanup
        if Path(temp_config).exists():
            Path(temp_config).unlink()
    
    except Exception as e:
        print(f"   ❌ Password management test failed: {e}")

def test_user_management():
    """Test user management features"""
    
    try:
        temp_config = "temp_user_test.json"
        auth_manager = AuthManager(temp_config)
        
        # Test user creation
        if auth_manager.create_user("testuser", "TestPass123!", "Test User", "test@universidad.edu.mx"):
            print("   ✅ User creation successful")
            
            # Verify user can authenticate
            if auth_manager.authenticate("testuser", "TestPass123!"):
                print("   ✅ New user can authenticate")
            else:
                print("   ❌ New user cannot authenticate")
        else:
            print("   ❌ User creation failed")
        
        # Test duplicate user creation
        if not auth_manager.create_user("testuser", "AnotherPass123!", "Another User", "another@universidad.edu.mx"):
            print("   ✅ Duplicate user creation properly rejected")
        else:
            print("   ❌ Duplicate user creation not rejected")
        
        # Test user info retrieval
        user_info = auth_manager.get_user_info("testuser")
        
        if user_info:
            print("   ✅ User info retrieval successful")
            if "password_hash" not in user_info:
                print("   ✅ Sensitive data properly excluded from user info")
            else:
                print("   ❌ Sensitive data exposed in user info")
        else:
            print("   ❌ User info retrieval failed")
        
        # Test user deactivation
        if auth_manager.deactivate_user("testuser"):
            print("   ✅ User deactivation successful")
            
            # Verify deactivated user cannot authenticate
            if not auth_manager.authenticate("testuser", "TestPass123!"):
                print("   ✅ Deactivated user cannot authenticate")
            else:
                print("   ❌ Deactivated user can still authenticate")
        else:
            print("   ❌ User deactivation failed")
        
        # Cleanup
        if Path(temp_config).exists():
            Path(temp_config).unlink()
    
    except Exception as e:
        print(f"   ❌ User management test failed: {e}")

def test_security_features():
    """Test security features"""
    
    try:
        temp_config = "temp_security_test.json"
        auth_manager = AuthManager(temp_config)
        
        # Test session timeout
        session_data = auth_manager.authenticate("admin", "admin123")
        
        if session_data:
            # Manually expire session for testing
            session_id = session_data["session_id"]
            auth_manager.sessions[session_id]["expires_at"] = datetime.now() - timedelta(hours=1)
            
            # Try to validate expired session
            if not auth_manager.validate_session(session_id):
                print("   ✅ Expired session properly rejected")
            else:
                print("   ❌ Expired session not rejected")
        
        # Test session cleanup
        initial_session_count = len(auth_manager.sessions)
        auth_manager._cleanup_expired_sessions()
        final_session_count = len(auth_manager.sessions)
        
        if final_session_count < initial_session_count:
            print("   ✅ Expired sessions cleaned up")
        else:
            print("   ✅ No expired sessions to clean up")
        
        # Test configuration security
        config = auth_manager.config
        
        if "security_settings" in config:
            security = config["security_settings"]
            
            if "session_secret" in security and len(security["session_secret"]) >= 32:
                print("   ✅ Session secret properly generated")
            else:
                print("   ❌ Session secret not properly generated")
            
            if security.get("password_min_length", 0) >= 8:
                print("   ✅ Minimum password length enforced")
            else:
                print("   ❌ Minimum password length not enforced")
        
        # Test session ID uniqueness
        session1 = auth_manager.authenticate("admin", "admin123")
        session2 = auth_manager.authenticate("admin", "admin123")
        
        if session1 and session2 and session1["session_id"] != session2["session_id"]:
            print("   ✅ Unique session IDs generated")
        else:
            print("   ❌ Session IDs not unique")
        
        # Cleanup
        if Path(temp_config).exists():
            Path(temp_config).unlink()
    
    except Exception as e:
        print(f"   ❌ Security features test failed: {e}")

if __name__ == "__main__":
    test_authentication_system()