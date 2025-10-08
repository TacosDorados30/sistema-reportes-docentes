"""
Logging middleware for monitoring and debugging
"""

import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime
from functools import wraps

from app.core.simple_audit import simple_audit

class ApplicationLogger:
    """Enhanced application logging"""
    
    def __init__(self, name: str = "app"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Create handlers if they don't exist
        if not self.logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(simple_formatter)
            self.logger.addHandler(console_handler)
            
            # File handler for errors
            try:
                file_handler = logging.FileHandler('logs/application.log')
                file_handler.setLevel(logging.WARNING)
                file_handler.setFormatter(detailed_formatter)
                self.logger.addHandler(file_handler)
            except (OSError, IOError):
                # If can't create file handler, continue without it
                pass
    
    def log_operation(self, operation: str, details: Dict[str, Any] = None, 
                     level: str = "INFO", user_id: str = None):
        """Log an operation with details"""
        
        message = f"Operation: {operation}"
        if details:
            message += f" | Details: {details}"
        if user_id:
            message += f" | User: {user_id}"
        
        log_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.log(log_level, message)
    
    def log_performance(self, operation: str, duration: float, 
                       details: Dict[str, Any] = None, user_id: str = None):
        """Log performance metrics"""
        
        message = f"Performance: {operation} took {duration:.3f}s"
        if details:
            message += f" | Details: {details}"
        if user_id:
            message += f" | User: {user_id}"
        
        # Log as warning if operation is slow
        level = logging.WARNING if duration > 5.0 else logging.INFO
        self.logger.log(level, message)
    
    def log_database_operation(self, operation: str, table: str = None, 
                             record_count: int = None, duration: float = None,
                             user_id: str = None):
        """Log database operations"""
        
        message = f"DB Operation: {operation}"
        if table:
            message += f" on {table}"
        if record_count is not None:
            message += f" ({record_count} records)"
        if duration is not None:
            message += f" in {duration:.3f}s"
        if user_id:
            message += f" | User: {user_id}"
        
        self.logger.info(message)
    
    def log_user_action(self, action: str, user_id: str, user_name: str = None,
                       details: Dict[str, Any] = None, success: bool = True):
        """Log user actions"""
        
        status = "SUCCESS" if success else "FAILED"
        message = f"User Action: {action} by {user_name or user_id} - {status}"
        
        if details:
            message += f" | Details: {details}"
        
        level = logging.INFO if success else logging.WARNING
        self.logger.log(level, message)
        
        # Also log to audit system
        try:
            simple_audit.log_action(
                action="USER_ACTION",
                description=f"{action} - {status}",
                user_id=user_id,
                user_name=user_name
            )
        except Exception as e:
            self.logger.error(f"Failed to log to audit system: {e}")

# Global logger instance
app_logger = ApplicationLogger()

def log_execution_time(operation_name: str = None, user_id_func: callable = None):
    """Decorator to log execution time"""
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            operation = operation_name or f"{func.__module__}.{func.__name__}"
            
            # Get user ID if function provided
            user_id = None
            if user_id_func:
                try:
                    user_id = user_id_func()
                except:
                    pass
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                app_logger.log_performance(
                    operation=operation,
                    duration=duration,
                    details={"status": "success"},
                    user_id=user_id
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                app_logger.log_performance(
                    operation=operation,
                    duration=duration,
                    details={"status": "error", "error": str(e)},
                    user_id=user_id
                )
                
                raise
        
        return wrapper
    return decorator

def log_database_operation(operation: str, table: str = None):
    """Decorator to log database operations"""
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Try to determine record count from result
                record_count = None
                if hasattr(result, '__len__'):
                    try:
                        record_count = len(result)
                    except:
                        pass
                elif isinstance(result, (int, bool)):
                    record_count = 1 if result else 0
                
                app_logger.log_database_operation(
                    operation=operation,
                    table=table,
                    record_count=record_count,
                    duration=duration
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                app_logger.log_database_operation(
                    operation=f"{operation} (FAILED)",
                    table=table,
                    duration=duration
                )
                
                raise
        
        return wrapper
    return decorator

def log_user_action(action_name: str):
    """Decorator to log user actions"""
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Try to extract user info from arguments
            user_id = None
            user_name = None
            
            # Look for user info in kwargs
            if 'user_id' in kwargs:
                user_id = kwargs['user_id']
            if 'user_name' in kwargs:
                user_name = kwargs['user_name']
            
            # Look for user info in args (common patterns)
            for arg in args:
                if hasattr(arg, 'get'):  # Dict-like object
                    if not user_id and 'user_id' in arg:
                        user_id = arg['user_id']
                    if not user_name and 'user_name' in arg:
                        user_name = arg['user_name']
            
            try:
                result = func(*args, **kwargs)
                
                app_logger.log_user_action(
                    action=action_name,
                    user_id=user_id or "unknown",
                    user_name=user_name,
                    success=True
                )
                
                return result
                
            except Exception as e:
                app_logger.log_user_action(
                    action=action_name,
                    user_id=user_id or "unknown",
                    user_name=user_name,
                    details={"error": str(e)},
                    success=False
                )
                
                raise
        
        return wrapper
    return decorator

class PerformanceMonitor:
    """Monitor application performance"""
    
    def __init__(self):
        self.metrics = {}
        self.logger = ApplicationLogger("performance")
    
    def record_metric(self, metric_name: str, value: float, 
                     tags: Dict[str, str] = None):
        """Record a performance metric"""
        
        timestamp = datetime.utcnow()
        
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        
        self.metrics[metric_name].append({
            "value": value,
            "timestamp": timestamp,
            "tags": tags or {}
        })
        
        # Keep only last 1000 entries per metric
        if len(self.metrics[metric_name]) > 1000:
            self.metrics[metric_name] = self.metrics[metric_name][-1000:]
        
        # Log slow operations
        if value > 5.0:  # More than 5 seconds
            self.logger.log_operation(
                f"SLOW_OPERATION: {metric_name}",
                {"duration": value, "tags": tags},
                "WARNING"
            )
    
    def get_metric_summary(self, metric_name: str) -> Dict[str, Any]:
        """Get summary statistics for a metric"""
        
        if metric_name not in self.metrics:
            return {}
        
        values = [m["value"] for m in self.metrics[metric_name]]
        
        if not values:
            return {}
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "recent": values[-10:] if len(values) >= 10 else values
        }
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get summary of all metrics"""
        
        return {
            metric_name: self.get_metric_summary(metric_name)
            for metric_name in self.metrics.keys()
        }

# Global performance monitor
performance_monitor = PerformanceMonitor()

def monitor_performance(metric_name: str = None, tags: Dict[str, str] = None):
    """Decorator to monitor performance"""
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            name = metric_name or f"{func.__module__}.{func.__name__}"
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                performance_monitor.record_metric(name, duration, tags)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                error_tags = (tags or {}).copy()
                error_tags["error"] = "true"
                
                performance_monitor.record_metric(name, duration, error_tags)
                
                raise
        
        return wrapper
    return decorator