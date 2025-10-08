"""
Health check system for monitoring application status
"""

import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database.connection import SessionLocal
from app.config import settings
from app.core.simple_audit import simple_audit
from app.models.audit import AuditActionEnum

class HealthChecker:
    """System health monitoring"""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
        self.last_check = None
        self.check_history = []
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": self._get_uptime(),
            "checks": {}
        }
        
        # Database health
        db_health = self._check_database_health()
        health_status["checks"]["database"] = db_health
        
        # System resources
        system_health = self._check_system_resources()
        health_status["checks"]["system"] = system_health
        
        # Application health
        app_health = self._check_application_health()
        health_status["checks"]["application"] = app_health
        
        # Storage health
        storage_health = self._check_storage_health()
        health_status["checks"]["storage"] = storage_health
        
        # Determine overall status
        failed_checks = [
            check for check in health_status["checks"].values()
            if check["status"] != "healthy"
        ]
        
        if failed_checks:
            if any(check["status"] == "critical" for check in failed_checks):
                health_status["status"] = "critical"
            else:
                health_status["status"] = "warning"
        
        # Store check result
        self.last_check = health_status
        self._store_check_history(health_status)
        
        return health_status
    
    def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        
        check_result = {
            "status": "healthy",
            "message": "Database is operational",
            "details": {}
        }
        
        try:
            db = SessionLocal()
            start_time = time.time()
            
            # Test basic connectivity
            db.execute(text("SELECT 1"))
            
            # Test audit logs table
            db.execute(text("SELECT COUNT(*) FROM audit_logs"))
            
            # Test main tables
            db.execute(text("SELECT COUNT(*) FROM formularios_envio"))
            
            response_time = time.time() - start_time
            
            check_result["details"] = {
                "response_time_ms": round(response_time * 1000, 2),
                "connection_pool_size": settings.database_pool_size,
                "database_url": settings.database_url.split("://")[0] + "://***"  # Hide credentials
            }
            
            # Check response time
            if response_time > 2.0:
                check_result["status"] = "warning"
                check_result["message"] = "Database response time is slow"
            elif response_time > 5.0:
                check_result["status"] = "critical"
                check_result["message"] = "Database response time is critical"
            
            db.close()
            
        except SQLAlchemyError as e:
            check_result["status"] = "critical"
            check_result["message"] = f"Database error: {str(e)[:100]}"
            check_result["details"]["error"] = str(e)
        except Exception as e:
            check_result["status"] = "critical"
            check_result["message"] = f"Database connection failed: {str(e)[:100]}"
            check_result["details"]["error"] = str(e)
        
        return check_result
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        
        check_result = {
            "status": "healthy",
            "message": "System resources are normal",
            "details": {}
        }
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            check_result["details"] = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "memory_available_mb": round(memory.available / 1024 / 1024, 2),
                "disk_percent": disk_percent,
                "disk_free_gb": round(disk.free / 1024 / 1024 / 1024, 2)
            }
            
            # Check thresholds
            warnings = []
            if cpu_percent > 80:
                warnings.append(f"High CPU usage: {cpu_percent}%")
            if memory_percent > 85:
                warnings.append(f"High memory usage: {memory_percent}%")
            if disk_percent > 90:
                warnings.append(f"High disk usage: {disk_percent}%")
            
            if warnings:
                check_result["status"] = "warning"
                check_result["message"] = "; ".join(warnings)
            
            # Critical thresholds
            if cpu_percent > 95 or memory_percent > 95 or disk_percent > 95:
                check_result["status"] = "critical"
                check_result["message"] = "Critical resource usage detected"
            
        except Exception as e:
            check_result["status"] = "warning"
            check_result["message"] = f"Could not check system resources: {str(e)[:100]}"
            check_result["details"]["error"] = str(e)
        
        return check_result
    
    def _check_application_health(self) -> Dict[str, Any]:
        """Check application-specific health"""
        
        check_result = {
            "status": "healthy",
            "message": "Application is running normally",
            "details": {}
        }
        
        try:
            # Check configuration
            config_issues = []
            if settings.secret_key == "dev-secret-key-change-in-production" and settings.is_production:
                config_issues.append("Using default secret key in production")
            
            if not settings.database_url:
                config_issues.append("Database URL not configured")
            
            # Check directories
            import os
            required_dirs = [settings.data_dir, settings.logs_dir, settings.reports_dir]
            missing_dirs = [d for d in required_dirs if not os.path.exists(d)]
            
            if missing_dirs:
                config_issues.append(f"Missing directories: {', '.join(missing_dirs)}")
            
            check_result["details"] = {
                "environment": settings.environment,
                "version": settings.app_version,
                "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
                "configuration_issues": config_issues
            }
            
            if config_issues:
                check_result["status"] = "warning"
                check_result["message"] = f"Configuration issues: {'; '.join(config_issues)}"
            
        except Exception as e:
            check_result["status"] = "warning"
            check_result["message"] = f"Application health check failed: {str(e)[:100]}"
            check_result["details"]["error"] = str(e)
        
        return check_result
    
    def _check_storage_health(self) -> Dict[str, Any]:
        """Check storage and file system health"""
        
        check_result = {
            "status": "healthy",
            "message": "Storage is accessible",
            "details": {}
        }
        
        try:
            import os
            
            # Check if required directories are writable
            test_dirs = [settings.data_dir, settings.logs_dir, settings.reports_dir]
            writable_dirs = []
            
            for directory in test_dirs:
                try:
                    test_file = os.path.join(directory, ".health_check")
                    with open(test_file, 'w') as f:
                        f.write("health_check")
                    os.remove(test_file)
                    writable_dirs.append(directory)
                except Exception:
                    pass
            
            check_result["details"] = {
                "required_directories": test_dirs,
                "writable_directories": writable_dirs,
                "storage_accessible": len(writable_dirs) == len(test_dirs)
            }
            
            if len(writable_dirs) < len(test_dirs):
                check_result["status"] = "warning"
                check_result["message"] = "Some storage directories are not writable"
            
        except Exception as e:
            check_result["status"] = "warning"
            check_result["message"] = f"Storage health check failed: {str(e)[:100]}"
            check_result["details"]["error"] = str(e)
        
        return check_result
    
    def _get_uptime(self) -> Dict[str, Any]:
        """Get application uptime"""
        
        uptime_delta = datetime.utcnow() - self.start_time
        
        return {
            "seconds": int(uptime_delta.total_seconds()),
            "human_readable": str(uptime_delta).split('.')[0],  # Remove microseconds
            "started_at": self.start_time.isoformat()
        }
    
    def _store_check_history(self, health_status: Dict[str, Any]):
        """Store health check history"""
        
        # Keep only last 100 checks
        self.check_history.append({
            "timestamp": health_status["timestamp"],
            "status": health_status["status"],
            "failed_checks": [
                name for name, check in health_status["checks"].items()
                if check["status"] != "healthy"
            ]
        })
        
        if len(self.check_history) > 100:
            self.check_history = self.check_history[-100:]
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health check summary"""
        
        if not self.check_history:
            return {"message": "No health checks performed yet"}
        
        recent_checks = self.check_history[-10:]  # Last 10 checks
        
        status_counts = {}
        for check in recent_checks:
            status = check["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_checks": len(self.check_history),
            "recent_status_distribution": status_counts,
            "last_check": self.last_check["timestamp"] if self.last_check else None,
            "current_status": self.last_check["status"] if self.last_check else "unknown"
        }
    
    def log_health_check(self, health_status: Dict[str, Any]):
        """Log health check results to audit system"""
        
        try:
            # Only log if there are issues
            if health_status["status"] != "healthy":
                failed_checks = [
                    name for name, check in health_status["checks"].items()
                    if check["status"] != "healthy"
                ]
                
                simple_audit.log_action(
                    AuditActionEnum.SYSTEM_ERROR,
                    f"Health check failed: {', '.join(failed_checks)}",
                    "system",
                    "Health Monitor"
                )
        except Exception as e:
            # Don't fail health check if audit logging fails
            pass

# Global health checker instance
health_checker = HealthChecker()

def get_health_status() -> Dict[str, Any]:
    """Get current health status"""
    return health_checker.get_system_health()

def get_simple_health() -> Dict[str, str]:
    """Get simple health status for basic monitoring"""
    try:
        health = health_checker.get_system_health()
        return {
            "status": health["status"],
            "message": "System is operational" if health["status"] == "healthy" else "System has issues"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Health check failed: {str(e)}"
        }