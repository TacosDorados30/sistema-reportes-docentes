"""
Simple audit logging system
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.audit import AuditLog, AuditActionEnum, AuditSeverityEnum
from app.database.connection import SessionLocal

class SimpleAuditLogger:
    """Simple audit logging system"""
    
    def __init__(self):
        """Initialize audit logger"""
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - AUDIT - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_action(self, action: AuditActionEnum, description: str, 
                   user_id: Optional[str] = None, user_name: Optional[str] = None,
                   severity: AuditSeverityEnum = AuditSeverityEnum.INFO) -> Optional[int]:
        """Log an audit action"""
        
        try:
            db = SessionLocal()
            
            audit_entry = AuditLog(
                action=action,
                severity=severity,
                user_id=user_id,
                user_name=user_name,
                description=description
            )
            
            db.add(audit_entry)
            db.commit()
            
            log_message = f"[{action}] {description}"
            if user_id:
                log_message += f" | User: {user_id}"
            
            self.logger.info(log_message)
            
            audit_id = audit_entry.id
            db.close()
            return audit_id
            
        except Exception as e:
            self.logger.error(f"Failed to write audit log: {e}")
            self.logger.info(f"AUDIT FALLBACK: [{action}] {description}")
            return None
    
    def log_form_approval(self, form_id: int, form_owner: str, approved_by: str):
        """Log form approval"""
        description = f"Form #{form_id} (owner: {form_owner}) approved by {approved_by}"
        return self.log_action(AuditActionEnum.FORM_APPROVAL, description, approved_by, approved_by)
    
    def log_form_rejection(self, form_id: int, form_owner: str, rejected_by: str, reason: str = ""):
        """Log form rejection"""
        description = f"Form #{form_id} (owner: {form_owner}) rejected by {rejected_by}"
        if reason:
            description += f" - Reason: {reason}"
        return self.log_action(AuditActionEnum.FORM_REJECTION, description, rejected_by, rejected_by)
    
    def log_login(self, user_id: str, user_name: str, success: bool = True):
        """Log login attempt"""
        if success:
            description = f"User '{user_name}' logged in successfully"
            severity = AuditSeverityEnum.INFO
        else:
            description = f"Failed login attempt for user '{user_id}'"
            severity = AuditSeverityEnum.WARNING
        
        return self.log_action(AuditActionEnum.LOGIN, description, user_id, user_name, severity)
    
    def log_logout(self, user_id: str, user_name: str):
        """Log logout"""
        description = f"User '{user_name}' logged out"
        return self.log_action(AuditActionEnum.LOGOUT, description, user_id, user_name)

# Global instance
simple_audit = SimpleAuditLogger()