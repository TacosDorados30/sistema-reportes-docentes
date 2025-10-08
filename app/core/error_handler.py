"""
Error handling utilities for the application
"""

import logging
import traceback
from typing import Dict, Any, Optional, Union
from datetime import datetime
from functools import wraps

from app.core.simple_audit import simple_audit

class ApplicationError(Exception):
    """Base application error"""
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code or "APP_ERROR"
        self.details = details or {}
        self.timestamp = datetime.utcnow()
        super().__init__(self.message)

class DatabaseError(ApplicationError):
    """Database operation error"""
    def __init__(self, message: str, operation: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "DB_ERROR", details)
        self.operation = operation

class ValidationError(ApplicationError):
    """Input validation error"""
    def __init__(self, message: str, field: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "VALIDATION_ERROR", details)
        self.field = field

class AuthenticationError(ApplicationError):
    """Authentication error"""
    def __init__(self, message: str = "Authentication failed", details: Dict[str, Any] = None):
        super().__init__(message, "AUTH_ERROR", details)

class AuthorizationError(ApplicationError):
    """Authorization error"""
    def __init__(self, message: str = "Access denied", details: Dict[str, Any] = None):
        super().__init__(message, "AUTHZ_ERROR", details)

class ExportError(ApplicationError):
    """Data export error"""
    def __init__(self, message: str, export_format: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "EXPORT_ERROR", details)
        self.export_format = export_format

class ReportError(ApplicationError):
    """Report generation error"""
    def __init__(self, message: str, report_type: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "REPORT_ERROR", details)
        self.report_type = report_type

class ErrorHandler:
    """Centralized error handling"""
    
    def __init__(self):
        self.logger = logging.getLogger("error_handler")
        self.logger.setLevel(logging.ERROR)
        
        # Create handler if not exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - ERROR - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_error(self, error: Exception, context: str = None, user_id: str = None, 
                  additional_data: Dict[str, Any] = None):
        """Log error with context and audit trail"""
        
        error_details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if additional_data:
            error_details.update(additional_data)
        
        # Add traceback for debugging
        if hasattr(error, '__traceback__'):
            error_details["traceback"] = traceback.format_exception(
                type(error), error, error.__traceback__
            )
        
        # Log to application logger
        self.logger.error(f"Error in {context}: {error}", extra=error_details)
        
        # Log to audit system
        try:
            simple_audit.log_action(
                action="SYSTEM_ERROR",
                description=f"Error in {context}: {str(error)[:200]}",
                user_id=user_id
            )
        except Exception as audit_error:
            self.logger.error(f"Failed to log error to audit system: {audit_error}")
    
    def handle_database_error(self, error: Exception, operation: str = None, 
                            user_id: str = None) -> DatabaseError:
        """Handle database errors"""
        
        context = f"Database operation: {operation}" if operation else "Database operation"
        
        # Log the error
        self.log_error(error, context, user_id, {"operation": operation})
        
        # Create user-friendly error message
        if "UNIQUE constraint failed" in str(error):
            message = "Ya existe un registro con estos datos"
        elif "NOT NULL constraint failed" in str(error):
            message = "Faltan datos obligatorios"
        elif "FOREIGN KEY constraint failed" in str(error):
            message = "Error de integridad de datos"
        elif "database is locked" in str(error):
            message = "La base de datos está temporalmente ocupada, intente nuevamente"
        else:
            message = "Error en la base de datos"
        
        return DatabaseError(message, operation, {"original_error": str(error)})
    
    def handle_validation_error(self, error: Exception, field: str = None,
                              user_id: str = None) -> ValidationError:
        """Handle validation errors"""
        
        context = f"Validation error for field: {field}" if field else "Validation error"
        
        # Log the error
        self.log_error(error, context, user_id, {"field": field})
        
        # Create user-friendly error message
        message = str(error) if str(error) else "Datos no válidos"
        
        return ValidationError(message, field, {"original_error": str(error)})
    
    def handle_export_error(self, error: Exception, export_format: str = None,
                          user_id: str = None) -> ExportError:
        """Handle export errors"""
        
        context = f"Export error for format: {export_format}" if export_format else "Export error"
        
        # Log the error
        self.log_error(error, context, user_id, {"export_format": export_format})
        
        # Create user-friendly error message
        if "Permission denied" in str(error):
            message = "No tiene permisos para exportar datos"
        elif "No data" in str(error):
            message = "No hay datos para exportar"
        else:
            message = f"Error al exportar datos en formato {export_format or 'desconocido'}"
        
        return ExportError(message, export_format, {"original_error": str(error)})
    
    def handle_report_error(self, error: Exception, report_type: str = None,
                          user_id: str = None) -> ReportError:
        """Handle report generation errors"""
        
        context = f"Report error for type: {report_type}" if report_type else "Report error"
        
        # Log the error
        self.log_error(error, context, user_id, {"report_type": report_type})
        
        # Create user-friendly error message
        if "No data" in str(error):
            message = "No hay datos suficientes para generar el reporte"
        elif "Template" in str(error):
            message = "Error en la plantilla del reporte"
        else:
            message = f"Error al generar reporte {report_type or 'desconocido'}"
        
        return ReportError(message, report_type, {"original_error": str(error)})
    
    def create_error_response(self, error: ApplicationError) -> Dict[str, Any]:
        """Create standardized error response"""
        
        return {
            "success": False,
            "error": {
                "code": error.error_code,
                "message": error.message,
                "timestamp": error.timestamp.isoformat(),
                "details": error.details
            }
        }
    
    def create_success_response(self, data: Any = None, message: str = None) -> Dict[str, Any]:
        """Create standardized success response"""
        
        response = {
            "success": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if data is not None:
            response["data"] = data
        
        if message:
            response["message"] = message
        
        return response

# Global error handler instance
error_handler = ErrorHandler()

def handle_errors(context: str = None, user_id_func: callable = None):
    """Decorator for automatic error handling"""
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ApplicationError:
                # Re-raise application errors as they're already handled
                raise
            except Exception as e:
                # Get user ID if function provided
                user_id = None
                if user_id_func:
                    try:
                        user_id = user_id_func()
                    except:
                        pass
                
                # Handle different types of errors
                if "database" in str(e).lower() or "sql" in str(e).lower():
                    raise error_handler.handle_database_error(e, context, user_id)
                elif "validation" in str(e).lower():
                    raise error_handler.handle_validation_error(e, None, user_id)
                else:
                    # Generic application error
                    error_handler.log_error(e, context or func.__name__, user_id)
                    raise ApplicationError(
                        "Ha ocurrido un error inesperado",
                        "UNEXPECTED_ERROR",
                        {"original_error": str(e)}
                    )
        
        return wrapper
    return decorator

def safe_execute(func, default_value=None, error_message="Operation failed"):
    """Safely execute a function and return default value on error"""
    
    try:
        return func()
    except Exception as e:
        error_handler.log_error(e, f"Safe execution of {func.__name__}")
        return default_value

def validate_required_fields(data: Dict[str, Any], required_fields: list) -> None:
    """Validate that required fields are present"""
    
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing_fields.append(field)
    
    if missing_fields:
        raise ValidationError(
            f"Campos obligatorios faltantes: {', '.join(missing_fields)}",
            details={"missing_fields": missing_fields}
        )

def sanitize_user_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize user input to prevent injection attacks"""
    
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            # Remove potentially dangerous characters
            sanitized_value = value.strip()
            # Basic XSS prevention
            sanitized_value = sanitized_value.replace('<', '&lt;').replace('>', '&gt;')
            # SQL injection prevention (basic)
            dangerous_patterns = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'SELECT', '--', ';']
            for pattern in dangerous_patterns:
                sanitized_value = sanitized_value.replace(pattern, '')
            
            sanitized[key] = sanitized_value
        else:
            sanitized[key] = value
    
    return sanitized