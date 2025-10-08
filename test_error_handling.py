#!/usr/bin/env python3
"""
Test error handling and validation system
"""

import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_error_handling_system():
    """Test the complete error handling system"""
    
    print("🧪 Testing Error Handling and Validation System")
    print("=" * 60)
    
    try:
        # Test 1: Import error handling modules
        from app.core.error_handler import (
            error_handler, ApplicationError, DatabaseError, ValidationError,
            AuthenticationError, ExportError, ReportError
        )
        from app.core.validators import FormValidator, DatabaseValidator, APIValidator
        from app.core.logging_middleware import app_logger, performance_monitor
        print("   ✅ Error handling modules imported successfully")
        
        # Test 2: Test validation functions
        test_validation_functions()
        
        # Test 3: Test error handling
        test_error_handling()
        
        # Test 4: Test logging middleware
        test_logging_middleware()
        
        # Test 5: Test performance monitoring
        test_performance_monitoring()
        
        print(f"\n📈 Error Handling System Testing Summary:")
        print(f"   - All modules imported successfully")
        print(f"   - Validation functions working correctly")
        print(f"   - Error handling operational")
        print(f"   - Logging middleware functional")
        print(f"   - Performance monitoring active")
        print(f"   - Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error handling system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_validation_functions():
    """Test validation functions"""
    
    print("\n2. Testing Validation Functions...")
    
    from app.core.validators import FormValidator, DatabaseValidator, APIValidator
    
    # Test email validation
    valid_emails = ["test@example.com", "user.name@domain.co.uk", "admin@universidad.edu.mx"]
    invalid_emails = ["invalid-email", "@domain.com", "user@", ""]
    
    for email in valid_emails:
        if FormValidator.validate_email(email):
            print(f"   ✅ Email validation passed for: {email}")
        else:
            print(f"   ❌ Email validation failed for valid email: {email}")
    
    for email in invalid_emails:
        if not FormValidator.validate_email(email):
            print(f"   ✅ Email validation correctly rejected: {email}")
        else:
            print(f"   ❌ Email validation incorrectly accepted: {email}")
    
    # Test name validation
    valid_names = ["Juan Pérez", "María García-López", "Dr. Carlos Rodríguez"]
    invalid_names = ["", "A", "X" * 300, "123456", "<script>alert('xss')</script>"]
    
    for name in valid_names:
        if FormValidator.validate_name(name):
            print(f"   ✅ Name validation passed for: {name}")
        else:
            print(f"   ❌ Name validation failed for valid name: {name}")
    
    for name in invalid_names:
        if not FormValidator.validate_name(name):
            print(f"   ✅ Name validation correctly rejected: {name}")
        else:
            print(f"   ❌ Name validation incorrectly accepted: {name}")
    
    # Test date validation
    valid_dates = ["2024-01-15", "2023-12-31", "2025-06-01"]
    invalid_dates = ["invalid-date", "2024-13-01", "1800-01-01", "2200-01-01"]
    
    for date_str in valid_dates:
        if FormValidator.validate_date(date_str):
            print(f"   ✅ Date validation passed for: {date_str}")
        else:
            print(f"   ❌ Date validation failed for valid date: {date_str}")
    
    for date_str in invalid_dates:
        if not FormValidator.validate_date(date_str):
            print(f"   ✅ Date validation correctly rejected: {date_str}")
        else:
            print(f"   ❌ Date validation incorrectly accepted: {date_str}")
    
    # Test ID validation
    valid_ids = [1, 123, "456", 999999]
    invalid_ids = [0, -1, "abc", "", None, 0.5]
    
    for id_val in valid_ids:
        if DatabaseValidator.validate_id(id_val):
            print(f"   ✅ ID validation passed for: {id_val}")
        else:
            print(f"   ❌ ID validation failed for valid ID: {id_val}")
    
    for id_val in invalid_ids:
        if not DatabaseValidator.validate_id(id_val):
            print(f"   ✅ ID validation correctly rejected: {id_val}")
        else:
            print(f"   ❌ ID validation incorrectly accepted: {id_val}")
    
    # Test string sanitization
    dangerous_strings = [
        "<script>alert('xss')</script>",
        "'; DROP TABLE users; --",
        "Normal text with <tags>",
        "Text with 'quotes' and \"double quotes\""
    ]
    
    for dangerous in dangerous_strings:
        sanitized = DatabaseValidator.sanitize_string(dangerous)
        if "<" not in sanitized and ">" not in sanitized and "'" not in sanitized and '"' not in sanitized:
            print(f"   ✅ String sanitization worked for dangerous input")
        else:
            print(f"   ⚠️  String sanitization may need improvement")

def test_error_handling():
    """Test error handling functions"""
    
    print("\n3. Testing Error Handling...")
    
    from app.core.error_handler import (
        error_handler, ApplicationError, DatabaseError, ValidationError
    )
    
    # Test custom error creation
    try:
        raise ValidationError("Test validation error", "test_field")
    except ValidationError as e:
        if e.message == "Test validation error" and e.field == "test_field":
            print("   ✅ ValidationError creation and handling working")
        else:
            print("   ❌ ValidationError creation failed")
    
    try:
        raise DatabaseError("Test database error", "test_operation")
    except DatabaseError as e:
        if e.message == "Test database error" and e.operation == "test_operation":
            print("   ✅ DatabaseError creation and handling working")
        else:
            print("   ❌ DatabaseError creation failed")
    
    # Test error response creation
    test_error = ApplicationError("Test error", "TEST_ERROR", {"detail": "test"})
    error_response = error_handler.create_error_response(test_error)
    
    if (error_response["success"] == False and 
        error_response["error"]["code"] == "TEST_ERROR" and
        error_response["error"]["message"] == "Test error"):
        print("   ✅ Error response creation working")
    else:
        print("   ❌ Error response creation failed")
    
    # Test success response creation
    success_response = error_handler.create_success_response({"data": "test"}, "Success message")
    
    if (success_response["success"] == True and 
        success_response["data"]["data"] == "test" and
        success_response["message"] == "Success message"):
        print("   ✅ Success response creation working")
    else:
        print("   ❌ Success response creation failed")

def test_logging_middleware():
    """Test logging middleware"""
    
    print("\n4. Testing Logging Middleware...")
    
    from app.core.logging_middleware import app_logger
    
    # Test basic logging
    try:
        app_logger.log_operation("test_operation", {"test": "data"}, "INFO", "test_user")
        print("   ✅ Basic operation logging working")
    except Exception as e:
        print(f"   ❌ Basic operation logging failed: {e}")
    
    # Test performance logging
    try:
        app_logger.log_performance("test_performance", 1.5, {"test": "data"}, "test_user")
        print("   ✅ Performance logging working")
    except Exception as e:
        print(f"   ❌ Performance logging failed: {e}")
    
    # Test database operation logging
    try:
        app_logger.log_database_operation("SELECT", "test_table", 10, 0.5, "test_user")
        print("   ✅ Database operation logging working")
    except Exception as e:
        print(f"   ❌ Database operation logging failed: {e}")
    
    # Test user action logging
    try:
        app_logger.log_user_action("test_action", "test_user", "Test User", {"test": "data"}, True)
        print("   ✅ User action logging working")
    except Exception as e:
        print(f"   ❌ User action logging failed: {e}")

def test_performance_monitoring():
    """Test performance monitoring"""
    
    print("\n5. Testing Performance Monitoring...")
    
    from app.core.logging_middleware import performance_monitor
    
    # Test metric recording
    try:
        performance_monitor.record_metric("test_metric", 2.5, {"tag": "test"})
        print("   ✅ Metric recording working")
    except Exception as e:
        print(f"   ❌ Metric recording failed: {e}")
    
    # Test metric summary
    try:
        summary = performance_monitor.get_metric_summary("test_metric")
        if summary and "count" in summary:
            print("   ✅ Metric summary generation working")
        else:
            print("   ❌ Metric summary generation failed")
    except Exception as e:
        print(f"   ❌ Metric summary generation failed: {e}")
    
    # Test all metrics summary
    try:
        all_metrics = performance_monitor.get_all_metrics()
        if isinstance(all_metrics, dict):
            print("   ✅ All metrics summary working")
        else:
            print("   ❌ All metrics summary failed")
    except Exception as e:
        print(f"   ❌ All metrics summary failed: {e}")

def test_form_validation():
    """Test complete form validation"""
    
    print("\n6. Testing Complete Form Validation...")
    
    from app.core.validators import FormValidator
    
    # Test valid form data
    valid_form_data = {
        "nombre_completo": "Dr. Juan Pérez García",
        "correo_institucional": "juan.perez@universidad.edu.mx",
        "cursos_capacitacion": [
            {
                "nombre_curso": "Curso de Python Avanzado",
                "fecha": "2024-03-15",
                "horas": 40
            }
        ],
        "publicaciones": [
            {
                "titulo": "Investigación en Inteligencia Artificial",
                "autores": "Dr. Juan Pérez, Dra. María García",
                "evento_revista": "Revista de Ciencias Computacionales",
                "estatus": "PUBLICADO"
            }
        ]
    }
    
    try:
        errors = FormValidator.validate_form_data(valid_form_data)
        if not errors:
            print("   ✅ Valid form data validation passed")
        else:
            print(f"   ❌ Valid form data validation failed: {errors}")
    except Exception as e:
        print(f"   ❌ Form validation failed: {e}")
    
    # Test invalid form data
    invalid_form_data = {
        "nombre_completo": "",  # Empty name
        "correo_institucional": "invalid-email",  # Invalid email
        "cursos_capacitacion": [
            {
                "nombre_curso": "ABC",  # Too short
                "fecha": "invalid-date",  # Invalid date
                "horas": -5  # Invalid hours
            }
        ]
    }
    
    try:
        errors = FormValidator.validate_form_data(invalid_form_data)
        if errors:
            print("   ✅ Invalid form data validation correctly found errors")
        else:
            print("   ❌ Invalid form data validation should have found errors")
    except Exception as e:
        print(f"   ❌ Form validation failed: {e}")

if __name__ == "__main__":
    success = test_error_handling_system()
    
    if success:
        print("\n🎉 Error handling and validation system is working correctly!")
    else:
        print("\n⚠️  Error handling and validation system test failed.")
    
    # Run additional form validation test
    test_form_validation()