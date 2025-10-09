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

    def get_audit_logs(self,
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None,
                       action: Optional[AuditActionEnum] = None,
                       user_id: Optional[str] = None,
                       severity: Optional[AuditSeverityEnum] = None,
                       limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit logs with filtering"""

        try:
            db = self._get_db()

            query = db.query(AuditLog)

            # Apply filters
            if start_date:
                query = query.filter(AuditLog.timestamp >= start_date)

            if end_date:
                query = query.filter(AuditLog.timestamp <= end_date)

            if action:
                query = query.filter(AuditLog.action == action)

            if user_id:
                query = query.filter(AuditLog.user_id == user_id)

            if severity:
                query = query.filter(AuditLog.severity == severity)

            # Order by timestamp descending and limit
            logs = query.order_by(desc(AuditLog.timestamp)).limit(limit).all()

            # Convert to dict format
            result = []
            for log in logs:
                result.append({
                    'id': log.id,
                    'timestamp': log.timestamp,
                    'action': log.action.value,
                    'severity': log.severity.value,
                    'user_id': log.user_id,
                    'user_name': log.user_name,
                    'description': log.description,
                    'resource_type': log.resource_type,
                    'resource_id': log.resource_id,
                    'ip_address': log.ip_address,
                    'user_agent': log.user_agent,
                    'extra_data': log.extra_data,
                    'error_message': log.error_message
                })

            return result

        except Exception as e:
            self.logger.error(f"Error getting audit logs: {e}")
            return []
        finally:
            self._close_db_if_needed()

    def get_audit_summary(self,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get audit summary statistics"""

        try:
            db = self._get_db()

            query = db.query(AuditLog)

            # Apply date filters
            if start_date:
                query = query.filter(AuditLog.timestamp >= start_date)

            if end_date:
                query = query.filter(AuditLog.timestamp <= end_date)

            all_logs = query.all()

            # Calculate summary statistics
            total_logs = len(all_logs)

            # Count by action
            action_counts = {}
            for log in all_logs:
                action = log.action.value
                action_counts[action] = action_counts.get(action, 0) + 1

            # Count by severity
            severity_counts = {}
            for log in all_logs:
                severity = log.severity.value
                severity_counts[severity] = severity_counts.get(
                    severity, 0) + 1

            # Count by user
            user_counts = {}
            for log in all_logs:
                user = log.user_id or 'Unknown'
                user_counts[user] = user_counts.get(user, 0) + 1

            # Recent activity (last 24 hours)
            recent_cutoff = datetime.utcnow() - timedelta(hours=24)
            recent_logs = [
                log for log in all_logs if log.timestamp >= recent_cutoff]

            return {
                'total_logs': total_logs,
                'action_counts': action_counts,
                'severity_counts': severity_counts,
                'user_counts': user_counts,
                'recent_activity_count': len(recent_logs),
                'date_range': {
                    'start': start_date.isoformat() if start_date else None,
                    'end': end_date.isoformat() if end_date else None
                }
            }

        except Exception as e:
            self.logger.error(f"Error getting audit summary: {e}")
            return {'error': str(e)}
        finally:
            self._close_db_if_needed()

    def cleanup_old_logs(self, days_to_keep: int = 90) -> int:
        """Clean up old audit logs"""

        try:
            db = self._get_db()

            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

            # Count logs to be deleted
            count = db.query(AuditLog).filter(
                AuditLog.timestamp < cutoff_date).count()

            # Delete old logs
            db.query(AuditLog).filter(
                AuditLog.timestamp < cutoff_date).delete()
            db.commit()

            self.logger.info(
                f"Cleaned up {count} old audit logs (older than {days_to_keep} days)")

            return count

        except Exception as e:
            self.logger.error(f"Error cleaning up audit logs: {e}")
            return 0
        finally:
            self._close_db_if_needed()


# Global audit logger instance
audit_logger = AuditLogger()
