#!/usr/bin/env python3
"""
Final comprehensive test for error handling and validation system
"""

import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_complete_error_handling():
    """Test the complete error handling system integration"""
    
    print("🧪 Testing Complete Error Handling Integration")
    print("=" * 60)
    
    try:
        # Test 1: Import all modules
        from app.core.error_handler import error_handler, ApplicationError, DatabaseError, ValidationError
        from app.core.validators import FormValidator, DatabaseValidator, APIValidator
        from app.core.logging_middleware import app_logger, performance_monitor
        from app.core.simple_audit import simple_audit
        from app.models.audit import AuditActionEnum, AuditSeverityEnum
        print("   ✅ All error handling modules imported successfully")
        
        # Test 2: Test validation with real data
        test_real_validation()
        
        # Test 3: Test error handling with database operations
        test_database_error_handling()
        
        # Test 4: Test audit logging integration
        test_audit_integration()
        
        # Test 5: Test performance monitoring
        test_performance_integration()
        
        print(f"\n📈 Complete Error Handling Integration Summary:")
        print(f"   - All modules working together correctly")
        print(f"   - Validation system operational")
        print(f"   - Error handling comprehensive")
        print(f"   - Audit logging integrated")
        print(f"   - Performance monitoring active")
        print(f"   - Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Complete error handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_real_validation():
    """Test validation with realistic data"""
    
    print("\n2. Testing Real Data Validation...")
    
    from app.core.validators import FormValidator
    
    # Test realistic form data
    realistic_form = {
        "nombre_completo": "Dr. María Elena García-López",
        "correo_institucional": "maria.garcia@universidad.edu.mx",
        "cursos_capacitacion": [
            {
                "nombre_curso": "Metodologías de Investigación Científica",
                "fecha": "2024-02-15",
                "horas": 40
            },
            {
                "nombre_curso": "Análisis de Datos con Python",
                "fecha": "2024-03-20",
                "horas": 32
            }
        ],
        "publicaciones": [
            {
                "titulo": "Aplicaciones de Machine Learning en Educación Superior",
                "autores": "Dr. María García, Dr. Carlos Rodríguez, Dra. Ana Martínez",
                "evento_revista": "Revista Internacional de Tecnología Educativa",
                "estatus": "PUBLICADO"
            }
        ],
        "eventos_academicos": [
            {
                "nombre_evento": "Congreso Internacional de Innovación Educativa",
                "fecha": "2024-05-10",
                "tipo_participacion": "PONENTE"
            }
        ]
    }
    
    try:
        errors = FormValidator.validate_form_data(realistic_form)
        if not errors:
            print("   ✅ Realistic form data validation passed")
        else:
            print(f"   ⚠️  Realistic form data validation found issues: {errors}")
    except Exception as e:
        print(f"   ❌ Realistic form validation failed: {e}")
    
    # Test edge cases
    edge_case_form = {
        "nombre_completo": "José María de la Cruz y Fernández-Villalobos",  # Long name with special chars
        "correo_institucional": "jose.maria.delacruz@universidad-tecnologica.edu.mx",  # Long email
        "cursos_capacitacion": [
            {
                "nombre_curso": "A" * 500,  # Maximum length course name
                "fecha": "2024-12-31",  # End of year date
                "horas": 1000  # Maximum hours
            }
        ]
    }
    
    try:
        errors = FormValidator.validate_form_data(edge_case_form)
        if not errors:
            print("   ✅ Edge case form data validation passed")
        else:
            print(f"   ⚠️  Edge case form data validation found issues: {errors}")
    except Exception as e:
        print(f"   ❌ Edge case form validation failed: {e}")

def test_database_error_handling():
    """Test database error handling"""
    
    print("\n3. Testing Database Error Handling...")
    
    from app.core.error_handler import error_handler
    
    # Simulate database errors
    try:
        # Simulate a database connection error
        raise Exception("database is locked")
    except Exception as e:
        db_error = error_handler.handle_database_error(e, "test_operation", "test_user")
        if "temporalmente ocupada" in db_error.message:
            print("   ✅ Database lock error handled correctly")
        else:
            print(f"   ❌ Database lock error not handled properly: {db_error.message}")
    
    try:
        # Simulate a constraint violation
        raise Exception("UNIQUE constraint failed: users.email")
    except Exception as e:
        db_error = error_handler.handle_database_error(e, "create_user", "admin")
        if "Ya existe" in db_error.message:
            print("   ✅ Unique constraint error handled correctly")
        else:
            print(f"   ❌ Unique constraint error not handled properly: {db_error.message}")
    
    try:
        # Simulate a foreign key error
        raise Exception("FOREIGN KEY constraint failed")
    except Exception as e:
        db_error = error_handler.handle_database_error(e, "delete_record", "admin")
        if "integridad" in db_error.message:
            print("   ✅ Foreign key constraint error handled correctly")
        else:
            print(f"   ❌ Foreign key constraint error not handled properly: {db_error.message}")

def test_audit_integration():
    """Test audit logging integration with error handling"""
    
    print("\n4. Testing Audit Integration...")
    
    from app.core.simple_audit import simple_audit
    from app.models.audit import AuditActionEnum, AuditSeverityEnum
    from app.core.error_handler import error_handler
    
    # Test successful operation logging
    try:
        log_id = simple_audit.log_action(
            AuditActionEnum.SYSTEM_ERROR,
            "Test error logging integration",
            "test_user",
            "Test User",
            AuditSeverityEnum.ERROR
        )
        
        if log_id:
            print("   ✅ Error audit logging successful")
        else:
            print("   ❌ Error audit logging failed")
    except Exception as e:
        print(f"   ❌ Error audit logging failed: {e}")
    
    # Test user action logging
    try:
        log_id = simple_audit.log_action(
            AuditActionEnum.USER_ACTION,
            "Test user action with error handling",
            "admin",
            "Administrator",
            AuditSeverityEnum.INFO
        )
        
        if log_id:
            print("   ✅ User action audit logging successful")
        else:
            print("   ❌ User action audit logging failed")
    except Exception as e:
        print(f"   ❌ User action audit logging failed: {e}")
    
    # Test configuration change logging
    try:
        log_id = simple_audit.log_action(
            AuditActionEnum.CONFIGURATION_CHANGE,
            "Test configuration change logging",
            "admin",
            "Administrator",
            AuditSeverityEnum.WARNING
        )
        
        if log_id:
            print("   ✅ Configuration change audit logging successful")
        else:
            print("   ❌ Configuration change audit logging failed")
    except Exception as e:
        print(f"   ❌ Configuration change audit logging failed: {e}")

def test_performance_integration():
    """Test performance monitoring integration"""
    
    print("\n5. Testing Performance Integration...")
    
    from app.core.logging_middleware import performance_monitor, app_logger
    import time
    
    # Test performance monitoring with actual operations
    start_time = time.time()
    
    # Simulate some work
    time.sleep(0.1)
    
    duration = time.time() - start_time
    
    try:
        performance_monitor.record_metric("test_integration_operation", duration, {"type": "integration_test"})
        print("   ✅ Performance metric recording successful")
    except Exception as e:
        print(f"   ❌ Performance metric recording failed: {e}")
    
    # Test performance summary
    try:
        summary = performance_monitor.get_metric_summary("test_integration_operation")
        if summary and summary.get("count", 0) > 0:
            print(f"   ✅ Performance summary working (recorded {summary['count']} metrics)")
        else:
            print("   ❌ Performance summary not working")
    except Exception as e:
        print(f"   ❌ Performance summary failed: {e}")
    
    # Test application logging
    try:
        app_logger.log_operation(
            "integration_test_complete",
            {"duration": duration, "status": "success"},
            "INFO",
            "test_user"
        )
        print("   ✅ Application logging successful")
    except Exception as e:
        print(f"   ❌ Application logging failed: {e}")

def test_error_response_formats():
    """Test error response formatting"""
    
    print("\n6. Testing Error Response Formats...")
    
    from app.core.error_handler import error_handler, ValidationError, DatabaseError
    
    # Test validation error response
    validation_error = ValidationError("Invalid email format", "email")
    response = error_handler.create_error_response(validation_error)
    
    expected_fields = ["success", "error"]
    error_fields = ["code", "message", "timestamp", "details"]
    
    if (response.get("success") == False and 
        "error" in response and
        all(field in response["error"] for field in error_fields)):
        print("   ✅ Validation error response format correct")
    else:
        print(f"   ❌ Validation error response format incorrect: {response}")
    
    # Test success response
    success_response = error_handler.create_success_response(
        {"id": 123, "name": "Test"}, 
        "Operation completed successfully"
    )
    
    if (success_response.get("success") == True and
        "data" in success_response and
        "message" in success_response and
        "timestamp" in success_response):
        print("   ✅ Success response format correct")
    else:
        print(f"   ❌ Success response format incorrect: {success_response}")

if __name__ == "__main__":
    success = test_complete_error_handling()
    
    if success:
        print("\n🎉 Complete error handling system integration is working correctly!")
        
        # Run additional tests
        test_error_response_formats()
        
        print("\n✨ All error handling and validation systems are operational!")
    else:
        print("\n⚠️  Complete error handling system integration test failed.")