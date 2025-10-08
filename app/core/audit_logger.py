"""
Audit logging system for tracking admin actions and system events
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.audit import AuditLog, AuditActionEnum, AuditSeverityEnum
from app.database.connection import SessionLocal

class AuditLogger:
    """Centralized audit logging system"""
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize audit logger"""
        self.db = db_session
        self._should_close_db = db_session is None
        
        # Setup Python logging for backup/debugging
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)
        
        # Create handler if not exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - AUDIT - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _get_db(self) -> Session:
        """Get database session"""
        if self.db is None:
            self.db = SessionLocal()
        return self.db
    
    def _close_db_if_needed(self):
        """Close database session if we created it"""
        if self._should_close_db and self.db:
            self.db.close()
            self.db = None
    
    def log_action(self,
                   action: AuditActionEnum,
                   description: str,
                   user_id: Optional[str] = None,
                   user_name: Optional[str] = None,
                   user_email: Optional[str] = None,
                   session_id: Optional[str] = None,
                   resource_type: Optional[str] = None,
                   resource_id: Optional[str] = None,
                   severity: AuditSeverityEnum = AuditSeverityEnum.INFO,
                   ip_address: Optional[str] = None,
                   user_agent: Optional[str] = None,
                   request_method: Optional[str] = None,
                   request_path: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None,
                   error_message: Optional[str] = None) -> Optional[int]:
        """Log an audit action"""
        
        try:
            db = self._get_db()
            
            # Create audit log entry
            audit_entry = AuditLog(
                action=action,
                severity=severity,
                user_id=user_id,
                user_name=user_name,
                user_email=user_email,
                session_id=session_id,
                resource_type=resource_type,
                resource_id=resource_id,
                description=description,
                ip_address=ip_address,
                user_agent=user_agent,
                request_method=request_method,
                request_path=request_path,
                extra_data=json.dumps(metadata) if metadata else None,
                error_message=error_message
            )
            
            db.add(audit_entry)
            db.commit()
            
            # Also log to Python logger for immediate visibility
            log_message = f"[{action.value}] {description}"
            if user_id:
                log_message += f" | User: {user_id}"
            if resource_type and resource_id:
                log_message += f" | Resource: {resource_type}#{resource_id}"
            
            if severity == AuditSeverityEnum.ERROR or severity == AuditSeverityEnum.CRITICAL:
                self.logger.error(log_message)
            elif severity == AuditSeverityEnum.WARNING:
                self.logger.warning(log_message)
            else:
                self.logger.info(log_message)
            
            return audit_entry.id
            
        except Exception as e:
            # Fallback to Python logging if database fails
            self.logger.error(f"Failed to write audit log to database: {e}")
            self.logger.info(f"AUDIT FALLBACK: [{action.value}] {description}")
            return None
        
        finally:
            self._close_db_if_needed()

# Global audit logger instance
audit_logger = AuditLogger()