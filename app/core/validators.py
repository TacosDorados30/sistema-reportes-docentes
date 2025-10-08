"""
Input validation utilities for the application
"""

import re
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date
from email_validator import validate_email, EmailNotValidError

class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)

class FormValidator:
    """Validator for form data"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not email or not isinstance(email, str):
            return False
        
        # Basic regex validation as fallback
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        try:
            # Try using email-validator first
            validate_email(email)
            return True
        except (EmailNotValidError, Exception):
            # Fallback to regex validation
            return bool(re.match(email_pattern, email))
    
    @staticmethod
    def validate_name(name: str, min_length: int = 2, max_length: int = 255) -> bool:
        """Validate name format"""
        if not name or not isinstance(name, str):
            return False
        
        name = name.strip()
        if len(name) < min_length or len(name) > max_length:
            return False
        
        # Check for valid characters (letters, spaces, accents, hyphens)
        pattern = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-\.]+$'
        return bool(re.match(pattern, name))
    
    @staticmethod
    def validate_date(date_str: Union[str, date], allow_future: bool = True) -> bool:
        """Validate date format and range"""
        try:
            if isinstance(date_str, str):
                # Try different date formats
                for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']:
                    try:
                        parsed_date = datetime.strptime(date_str, fmt).date()
                        break
                    except ValueError:
                        continue
                else:
                    return False
            elif isinstance(date_str, date):
                parsed_date = date_str
            else:
                return False
            
            # Check if date is reasonable (not too far in past or future)
            today = date.today()
            min_date = date(1900, 1, 1)
            max_date = date(2100, 12, 31) if allow_future else today
            
            return min_date <= parsed_date <= max_date
            
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_hours(hours: Union[str, int]) -> bool:
        """Validate hours (must be positive integer)"""
        try:
            hours_int = int(hours)
            return 1 <= hours_int <= 1000  # Reasonable range
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_text_length(text: str, min_length: int = 1, max_length: int = 1000) -> bool:
        """Validate text length"""
        if not isinstance(text, str):
            return False
        
        text = text.strip()
        return min_length <= len(text) <= max_length
    
    @staticmethod
    def validate_form_data(form_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate complete form data and return errors"""
        errors = {}
        
        # Validate required fields
        required_fields = ['nombre_completo', 'correo_institucional']
        for field in required_fields:
            if field not in form_data or not form_data[field]:
                errors[field] = errors.get(field, [])
                errors[field].append(f"El campo {field} es obligatorio")
        
        # Validate name
        if 'nombre_completo' in form_data:
            if not FormValidator.validate_name(form_data['nombre_completo']):
                errors['nombre_completo'] = errors.get('nombre_completo', [])
                errors['nombre_completo'].append("Nombre no válido")
        
        # Validate email
        if 'correo_institucional' in form_data:
            if not FormValidator.validate_email(form_data['correo_institucional']):
                errors['correo_institucional'] = errors.get('correo_institucional', [])
                errors['correo_institucional'].append("Email no válido")
        
        # Validate courses
        if 'cursos_capacitacion' in form_data:
            for i, curso in enumerate(form_data['cursos_capacitacion']):
                if not FormValidator.validate_text_length(curso.get('nombre_curso', ''), 5, 500):
                    field_key = f'cursos_capacitacion[{i}].nombre_curso'
                    errors[field_key] = ["Nombre del curso debe tener entre 5 y 500 caracteres"]
                
                if not FormValidator.validate_date(curso.get('fecha')):
                    field_key = f'cursos_capacitacion[{i}].fecha'
                    errors[field_key] = ["Fecha no válida"]
                
                if not FormValidator.validate_hours(curso.get('horas')):
                    field_key = f'cursos_capacitacion[{i}].horas'
                    errors[field_key] = ["Horas debe ser un número entre 1 y 1000"]
        
        # Validate publications
        if 'publicaciones' in form_data:
            for i, pub in enumerate(form_data['publicaciones']):
                if not FormValidator.validate_text_length(pub.get('titulo', ''), 10, 1000):
                    field_key = f'publicaciones[{i}].titulo'
                    errors[field_key] = ["Título debe tener entre 10 y 1000 caracteres"]
                
                if not FormValidator.validate_text_length(pub.get('autores', ''), 5, 500):
                    field_key = f'publicaciones[{i}].autores'
                    errors[field_key] = ["Autores debe tener entre 5 y 500 caracteres"]
        
        return errors

class DatabaseValidator:
    """Validator for database operations"""
    
    @staticmethod
    def validate_id(id_value: Any) -> bool:
        """Validate ID (must be positive integer)"""
        try:
            id_int = int(id_value)
            return id_int > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_enum_value(value: str, valid_values: List[str]) -> bool:
        """Validate enum value"""
        return value in valid_values
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not isinstance(text, str):
            return ""
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', text)
        
        # Trim whitespace and limit length
        sanitized = sanitized.strip()[:max_length]
        
        return sanitized

class APIValidator:
    """Validator for API requests"""
    
    @staticmethod
    def validate_pagination(page: Any, limit: Any) -> tuple[int, int]:
        """Validate and normalize pagination parameters"""
        try:
            page_int = max(1, int(page)) if page else 1
            limit_int = max(1, min(1000, int(limit))) if limit else 50
            return page_int, limit_int
        except (ValueError, TypeError):
            return 1, 50
    
    @staticmethod
    def validate_date_range(start_date: Any, end_date: Any) -> tuple[Optional[date], Optional[date]]:
        """Validate date range parameters"""
        parsed_start = None
        parsed_end = None
        
        if start_date:
            try:
                if isinstance(start_date, str):
                    parsed_start = datetime.strptime(start_date, '%Y-%m-%d').date()
                elif isinstance(start_date, date):
                    parsed_start = start_date
            except ValueError:
                pass
        
        if end_date:
            try:
                if isinstance(end_date, str):
                    parsed_end = datetime.strptime(end_date, '%Y-%m-%d').date()
                elif isinstance(end_date, date):
                    parsed_end = end_date
            except ValueError:
                pass
        
        # Ensure start_date is before end_date
        if parsed_start and parsed_end and parsed_start > parsed_end:
            parsed_start, parsed_end = parsed_end, parsed_start
        
        return parsed_start, parsed_end

def validate_and_sanitize_input(data: Dict[str, Any], validation_rules: Dict[str, Any]) -> Dict[str, Any]:
    """Generic input validation and sanitization"""
    
    sanitized_data = {}
    errors = []
    
    for field, rules in validation_rules.items():
        value = data.get(field)
        
        # Check if required
        if rules.get('required', False) and not value:
            errors.append(f"Field '{field}' is required")
            continue
        
        # Skip validation if field is optional and empty
        if not value and not rules.get('required', False):
            continue
        
        # Type validation
        expected_type = rules.get('type')
        if expected_type and not isinstance(value, expected_type):
            try:
                value = expected_type(value)
            except (ValueError, TypeError):
                errors.append(f"Field '{field}' must be of type {expected_type.__name__}")
                continue
        
        # String validation
        if isinstance(value, str):
            # Length validation
            min_length = rules.get('min_length', 0)
            max_length = rules.get('max_length', 10000)
            
            if len(value) < min_length:
                errors.append(f"Field '{field}' must be at least {min_length} characters")
                continue
            
            if len(value) > max_length:
                errors.append(f"Field '{field}' must be at most {max_length} characters")
                continue
            
            # Sanitize string
            value = DatabaseValidator.sanitize_string(value, max_length)
        
        # Numeric validation
        if isinstance(value, (int, float)):
            min_value = rules.get('min_value')
            max_value = rules.get('max_value')
            
            if min_value is not None and value < min_value:
                errors.append(f"Field '{field}' must be at least {min_value}")
                continue
            
            if max_value is not None and value > max_value:
                errors.append(f"Field '{field}' must be at most {max_value}")
                continue
        
        sanitized_data[field] = value
    
    if errors:
        raise ValidationError("; ".join(errors))
    
    return sanitized_data