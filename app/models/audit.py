"""
Audit logging models for tracking admin actions
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum
from datetime import datetime
import enum

# Import the shared Base from the main database module
from app.models.database import Base

class AuditActionEnum(enum.Enum):
    """Enum for audit action types"""
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    FORM_APPROVAL = "FORM_APPROVAL"
    FORM_REJECTION = "FORM_REJECTION"
    DATA_EXPORT = "DATA_EXPORT"
    REPORT_GENERATION = "REPORT_GENERATION"
    USER_CREATION = "USER_CREATION"
    USER_DEACTIVATION = "USER_DEACTIVATION"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"
    SYSTEM_ACCESS = "SYSTEM_ACCESS"
    DATA_VIEW = "DATA_VIEW"
    CONFIGURATION_CHANGE = "CONFIGURATION_CHANGE"

class AuditSeverityEnum(enum.Enum):
    """Enum for audit severity levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class AuditLog(Base):
    """Audit log model for tracking admin actions"""
    
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    action = Column(SQLEnum(AuditActionEnum), nullable=False, index=True)
    severity = Column(SQLEnum(AuditSeverityEnum), default=AuditSeverityEnum.INFO, nullable=False)
    
    # User information
    user_id = Column(String(100), nullable=True, index=True)
    user_name = Column(String(200), nullable=True)
    user_email = Column(String(200), nullable=True)
    session_id = Column(String(100), nullable=True)
    
    # Action details
    resource_type = Column(String(100), nullable=True)  # e.g., "formulario", "user", "report"
    resource_id = Column(String(100), nullable=True)    # ID of the affected resource
    description = Column(Text, nullable=False)
    
    # Technical details
    ip_address = Column(String(45), nullable=True)      # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)
    request_method = Column(String(10), nullable=True)  # GET, POST, etc.
    request_path = Column(String(500), nullable=True)
    
    # Additional context
    extra_data = Column(Text, nullable=True)            # JSON string for additional data
    error_message = Column(Text, nullable=True)         # Error details if applicable
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action.value}, user={self.user_id}, timestamp={self.timestamp})>"