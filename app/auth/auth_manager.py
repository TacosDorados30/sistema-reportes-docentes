"""
Authentication manager for admin panel
"""

import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import json
from pathlib import Path

class AuthManager:
    """Simple authentication manager for admin panel"""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize authentication manager"""
        
        if config_file is None:
            config_file = os.path.join(os.path.dirname(__file__), '..', '..', 'auth_config.json')
        
        self.config_file = Path(config_file)
        self.sessions = {}  # In-memory session storage
        self.session_timeout = timedelta(hours=8)  # 8 hour session timeout
        
        # Load or create auth configuration
        self.config = self._load_or_create_config()
    
    def _load_or_create_config(self) -> Dict[str, Any]:
        """Load authentication configuration or create default"""
        
        # Try to load from file first (PRIORITY)
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # File has priority - don't merge env vars
                    # This allows password changes to persist
                    return config
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # If file doesn't exist, try to load from environment variables (FALLBACK)
        env_config = self._load_from_env()
        if env_config:
            # Save env config to file so future changes persist
            self._save_config(env_config)
            return env_config
        
        # Create default configuration
        default_config = {
            "admin_users": {
                "admin": {
                    "password_hash": self._hash_password("admin123"),
                    "name": "Administrador",
                    "email": "admin@universidad.edu.mx",
                    "created_at": datetime.now().isoformat(),
                    "active": True
                }
            },
            "session_settings": {
                "timeout_hours": 8,
                "require_https": False,
                "max_failed_attempts": 5,
                "lockout_duration_minutes": 30
            },
            "security_settings": {
                "password_min_length": 8,
                "require_special_chars": True,
                "session_secret": secrets.token_hex(32)
            }
        }
        
        # Save default configuration
        self._save_config(default_config)
        return default_config
    
    def _load_from_env(self) -> Optional[Dict[str, Any]]:
        """Load admin configuration from environment variables"""
        
        # Check if admin credentials are in environment
        admin_hash = os.getenv("ADMIN_PASSWORD_HASH")
        admin_name = os.getenv("ADMIN_NAME", "Administrador")
        admin_email = os.getenv("ADMIN_EMAIL", "admin@universidad.edu.mx")
        
        if not admin_hash:
            return None
        
        return {
            "admin_users": {
                "admin": {
                    "password_hash": admin_hash,
                    "name": admin_name,
                    "email": admin_email,
                    "active": True
                }
            },
            "session_settings": {
                "timeout_hours": 8,
                "require_https": False,
                "max_failed_attempts": 5,
                "lockout_duration_minutes": 30
            },
            "security_settings": {
                "password_min_length": 8,
                "require_special_chars": True,
                "session_secret": os.getenv("SESSION_SECRET", secrets.token_hex(32))
            }
        }
    
    def _merge_env_config(self, config: Dict[str, Any]):
        """Merge environment variables into config (env takes precedence)"""
        
        admin_hash = os.getenv("ADMIN_PASSWORD_HASH")
        if admin_hash and "admin_users" in config and "admin" in config["admin_users"]:
            # Environment variable overrides file
            config["admin_users"]["admin"]["password_hash"] = admin_hash
            config["admin_users"]["admin"]["name"] = os.getenv("ADMIN_NAME", config["admin_users"]["admin"].get("name", "Administrador"))
            config["admin_users"]["admin"]["email"] = os.getenv("ADMIN_EMAIL", config["admin_users"]["admin"].get("email", "admin@universidad.edu.mx"))
    
    def _save_config(self, config: Dict[str, Any]):
        """Save authentication configuration"""
        
        self.config_file.parent.mkdir(exist_ok=True)
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False, default=str)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt"""
        
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        
        try:
            salt, password_hash = stored_hash.split(':')
            computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return computed_hash == password_hash
        except ValueError:
            return False
    
    def authenticate(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user credentials using email"""
        
        # Find user by email
        users = self.config.get("admin_users", {})
        username = None
        user_data = None
        
        for uname, udata in users.items():
            if udata.get("email", "").lower() == email.lower():
                username = uname
                user_data = udata
                break
        
        # If not found by email, return None
        if not username or not user_data:
            return None
        
        # Check if user is active
        if not user_data.get("active", True):
            return None
        
        # Verify password
        if not self._verify_password(password, user_data["password_hash"]):
            return None
        
        # Create session
        session_id = secrets.token_urlsafe(32)
        session_data = {
            "session_id": session_id,
            "username": username,
            "name": user_data.get("name", username),
            "email": user_data.get("email", ""),
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "expires_at": datetime.now() + self.session_timeout
        }
        
        self.sessions[session_id] = session_data
        
        # Clean up expired sessions
        self._cleanup_expired_sessions()
        
        return session_data
    
    def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Validate session and return session data"""
        
        if not session_id or session_id not in self.sessions:
            return None
        
        session_data = self.sessions[session_id]
        
        # Check if session has expired
        if datetime.now() > session_data["expires_at"]:
            del self.sessions[session_id]
            return None
        
        # Update last activity
        session_data["last_activity"] = datetime.now()
        session_data["expires_at"] = datetime.now() + self.session_timeout
        
        return session_data
    
    def logout(self, session_id: str) -> bool:
        """Logout user by removing session"""
        
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        
        return False
    
    def _cleanup_expired_sessions(self):
        """Remove expired sessions"""
        
        now = datetime.now()
        expired_sessions = [
            session_id for session_id, session_data in self.sessions.items()
            if now > session_data["expires_at"]
        ]
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get list of active sessions"""
        
        self._cleanup_expired_sessions()
        
        return [
            {
                "session_id": session_data["session_id"],
                "username": session_data["username"],
                "name": session_data["name"],
                "created_at": session_data["created_at"].isoformat(),
                "last_activity": session_data["last_activity"].isoformat(),
                "expires_at": session_data["expires_at"].isoformat()
            }
            for session_data in self.sessions.values()
        ]
    
    def create_user(self, username: str, password: str, name: str, email: str) -> bool:
        """Create new admin user"""
        
        users = self.config.get("admin_users", {})
        
        # Check if user already exists
        if username in users:
            return False
        
        # Validate password strength
        if not self._validate_password_strength(password):
            return False
        
        # Create user
        users[username] = {
            "password_hash": self._hash_password(password),
            "name": name,
            "email": email,
            "created_at": datetime.now().isoformat(),
            "active": True
        }
        
        self.config["admin_users"] = users
        self._save_config(self.config)
        
        return True
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        
        users = self.config.get("admin_users", {})
        
        if username not in users:
            return False
        
        user_data = users[username]
        
        # Verify old password
        if not self._verify_password(old_password, user_data["password_hash"]):
            return False
        
        # Validate new password strength
        if not self._validate_password_strength(new_password):
            return False
        
        # Update password
        user_data["password_hash"] = self._hash_password(new_password)
        user_data["password_changed_at"] = datetime.now().isoformat()
        
        self._save_config(self.config)
        
        return True
    
    def _validate_password_strength(self, password: str) -> bool:
        """Validate password strength"""
        
        settings = self.config.get("security_settings", {})
        min_length = settings.get("password_min_length", 8)
        require_special = settings.get("require_special_chars", True)
        
        if len(password) < min_length:
            return False
        
        if require_special:
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if not any(char in special_chars for char in password):
                return False
        
        return True
    
    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user information (without sensitive data)"""
        
        users = self.config.get("admin_users", {})
        
        if username not in users:
            return None
        
        user_data = users[username].copy()
        
        # Remove sensitive information
        user_data.pop("password_hash", None)
        
        return user_data
    
    def deactivate_user(self, username: str) -> bool:
        """Deactivate user account"""
        
        users = self.config.get("admin_users", {})
        
        if username not in users:
            return False
        
        users[username]["active"] = False
        users[username]["deactivated_at"] = datetime.now().isoformat()
        
        self._save_config(self.config)
        
        # Remove all sessions for this user
        sessions_to_remove = [
            session_id for session_id, session_data in self.sessions.items()
            if session_data["username"] == username
        ]
        
        for session_id in sessions_to_remove:
            del self.sessions[session_id]
        
        return True
    
    def update_user_info(self, username: str, name: str, email: str) -> bool:
        """Update user name and email"""
        
        users = self.config.get("admin_users", {})
        
        if username not in users:
            return False
        
        # Update user information
        users[username]["name"] = name
        users[username]["email"] = email
        users[username]["updated_at"] = datetime.now().isoformat()
        
        self._save_config(self.config)
        
        return True
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        
        session_data = self.validate_session(session_id)
        
        if not session_data:
            return None
        
        return {
            "username": session_data["username"],
            "name": session_data["name"],
            "email": session_data["email"],
            "created_at": session_data["created_at"].isoformat(),
            "last_activity": session_data["last_activity"].isoformat(),
            "expires_at": session_data["expires_at"].isoformat()
        }