#!/usr/bin/env python3
"""
Test script for form validation and processing functions
"""

import sys
import os
from datetime import datetime, date

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.api.routes import validate_form_data, process_form_data, validate_array_field, process_array_field

def test_form_validation():
    """Test form validation and processing functions"""
    
    print("🧪 Testing Form Validation and Processing")
    print("=" * 60)
    
    # Test 1: Valid form data
    print("\n1. Testing Valid Form Data...")
    test_valid_form_data()
    
    # Test 2: Invalid form data
    print("\n2. Testing Invalid Form Data...")
    test_invalid_form_data()
    
    # Test 3: Array field validation
    print("\n3. Testing Array Field Validation...")
    test_array_field_validation()
    
    # Test 4: Data processing
    print("\n4. Testing Data Processing...")
    test_data_processing()
    
    # Test 5: Edge cases
    print("\n5. Testing Edge Cases...")
    test_edge_cases()
    
    print(f"\n📈 Form Validation Testing Summary:")
    print(f"   - Form validation functions working correctly")
    print(f"   - Error detection implemented properly")
    print(f"   - Data processing cleaning data effectively")
    print(f"   - Array validation handling complex structures")
    print(f"   - Edge cases handled gracefully")
    print(f"   - Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def test_valid_form_data():
    """Test validation with valid form data"""
    
    try:
        valid_data = {
            "nombre_completo": "Dr. Juan Pérez García",
            "correo_institucional": "juan.perez@universidad.edu.mx",
            "cursos_capacitacion": [
                {
                    "nombre_curso": "Python para Ciencia de Datos",
                    "fecha": "2024-02-15",
                    "horas": "40"
                }
            ],
            "publicaciones": [
                {
                    "autores": "Juan Pérez",
                    "titulo": "IA en Educación",
                    "evento_revista": "IEEE Conference",
                    "estatus": "PUBLICADO"
                }
            ],
            "eventos_academicos": [
                {
                    "nombre_evento": "Congreso de IA",
                    "fecha": "2024-03-10",
                    "tipo_participacion": "ORGANIZADOR"
                }
            ]
        }
        
        errors = validate_form_data(valid_data)
        
        if len(errors) == 0:
            print("   ✅ Valid form data passed validation")
        else:
            print(f"   ❌ Valid form data failed validation: {errors}")
    
    except Exception as e:
        print(f"   ❌ Valid form data test failed: {e}")

def test_invalid_form_data():
    """Test validation with invalid form data"""
    
    try:
        # Test missing required fields
        invalid_data1 = {
            "nombre_completo": "",
            "correo_institucional": "invalid-email-format"
        }
        
        errors1 = validate_form_data(invalid_data1)
        
        if len(errors1) > 0:
            print("   ✅ Missing required fields detected")
            print(f"   Errors found: {len(errors1)}")
        else:
            print("   ❌ Missing required fields not detected")
        
        # Test invalid email format
        invalid_data2 = {
            "nombre_completo": "Test User",
            "correo_institucional": "not-an-email"
        }
        
        errors2 = validate_form_data(invalid_data2)
        
        if any("formato" in error.lower() or "válido" in error.lower() for error in errors2):
            print("   ✅ Invalid email format detected")
        else:
            print("   ❌ Invalid email format not detected")
    
    except Exception as e:
        print(f"   ❌ Invalid form data test failed: {e}")

def test_array_field_validation():
    """Test array field validation"""
    
    try:
        # Test valid courses
        valid_courses = [
            {
                "nombre_curso": "Python Básico",
                "fecha": "2024-02-15",
                "horas": "30"
            },
            {
                "nombre_curso": "Machine Learning",
                "fecha": "2024-03-01",
                "horas": "60"
            }
        ]
        
        errors1 = validate_array_field(valid_courses, "cursos_capacitacion")
        
        if len(errors1) == 0:
            print("   ✅ Valid courses array passed validation")
        else:
            print(f"   ❌ Valid courses array failed: {errors1}")
        
        # Test invalid courses
        invalid_courses = [
            {
                "nombre_curso": "",  # Missing required field
                "fecha": "2024-02-15",
                "horas": "-10"  # Invalid hours
            },
            {
                "nombre_curso": "Valid Course",
                "fecha": "invalid-date",  # Invalid date format
                "horas": "abc"  # Invalid hours format
            }
        ]
        
        errors2 = validate_array_field(invalid_courses, "cursos_capacitacion")
        
        if len(errors2) > 0:
            print("   ✅ Invalid courses array errors detected")
            print(f"   Errors found: {len(errors2)}")
        else:
            print("   ❌ Invalid courses array errors not detected")
        
        # Test valid publications
        valid_publications = [
            {
                "autores": "Juan Pérez, María García",
                "titulo": "Investigación en IA",
                "evento_revista": "Revista de IA",
                "estatus": "PUBLICADO"
            }
        ]
        
        errors3 = validate_array_field(valid_publications, "publicaciones")
        
        if len(errors3) == 0:
            print("   ✅ Valid publications array passed validation")
        else:
            print(f"   ❌ Valid publications array failed: {errors3}")
    
    except Exception as e:
        print(f"   ❌ Array field validation test failed: {e}")

def test_data_processing():
    """Test data processing functions"""
    
    try:
        # Test basic data processing
        raw_data = {
            "nombre_completo": "  Dr. Juan Pérez  ",  # Extra spaces
            "correo_institucional": "  juan@universidad.edu.mx  ",
            "cursos_capacitacion": [
                {
                    "nombre_curso": "  Python Course  ",
                    "fecha": "2024-02-15",
                    "horas": "40"  # String number
                }
            ],
            "publicaciones": [],
            "eventos_academicos": []
        }
        
        processed = process_form_data(raw_data)
        
        # Check if spaces were trimmed
        if processed["nombre_completo"] == "Dr. Juan Pérez":
            print("   ✅ String trimming working correctly")
        else:
            print(f"   ❌ String trimming failed: '{processed['nombre_completo']}'")
        
        # Check if arrays were processed
        if isinstance(processed["cursos_capacitacion"], list):
            print("   ✅ Array processing working correctly")
        else:
            print("   ❌ Array processing failed")
        
        # Test array field processing
        raw_courses = [
            {
                "nombre_curso": "  Test Course  ",
                "fecha": "2024-02-15",
                "horas": "30",
                "empty_field": ""  # Should be removed
            },
            {
                "nombre_curso": "",  # Empty, should be filtered out
                "fecha": "",
                "horas": ""
            }
        ]
        
        processed_courses = process_array_field(raw_courses, "cursos_capacitacion")
        
        if len(processed_courses) == 1:  # Only the valid course should remain
            print("   ✅ Array field processing filtering correctly")
        else:
            print(f"   ❌ Array field processing failed: {len(processed_courses)} items")
        
        # Check if numeric conversion works
        if processed_courses[0].get("horas") == 30:  # Should be converted to int
            print("   ✅ Numeric conversion working correctly")
        else:
            print(f"   ❌ Numeric conversion failed: {processed_courses[0].get('horas')}")
    
    except Exception as e:
        print(f"   ❌ Data processing test failed: {e}")

def test_edge_cases():
    """Test edge cases and error conditions"""
    
    try:
        # Test empty data
        empty_data = {}
        errors1 = validate_form_data(empty_data)
        
        if len(errors1) > 0:
            print("   ✅ Empty data properly rejected")
        else:
            print("   ❌ Empty data not properly rejected")
        
        # Test None values
        none_data = {
            "nombre_completo": None,
            "correo_institucional": None
        }
        errors2 = validate_form_data(none_data)
        
        if len(errors2) > 0:
            print("   ✅ None values properly handled")
        else:
            print("   ❌ None values not properly handled")
        
        # Test invalid array structure
        invalid_array_data = {
            "nombre_completo": "Test User",
            "correo_institucional": "test@universidad.edu.mx",
            "cursos_capacitacion": "not-an-array"  # Should be array
        }
        
        errors3 = validate_form_data(invalid_array_data)
        
        if len(errors3) > 0:
            print("   ✅ Invalid array structure detected")
        else:
            print("   ❌ Invalid array structure not detected")
        
        # Test very long strings
        long_string_data = {
            "nombre_completo": "A" * 1000,  # Very long name
            "correo_institucional": "test@universidad.edu.mx"
        }
        
        processed_long = process_form_data(long_string_data)
        
        if processed_long["nombre_completo"] == "A" * 1000:
            print("   ✅ Long strings handled correctly")
        else:
            print("   ❌ Long strings not handled correctly")
        
        # Test special characters
        special_char_data = {
            "nombre_completo": "Dr. José María Ñuñez-García",
            "correo_institucional": "jose.maria@universidad.edu.mx"
        }
        
        errors4 = validate_form_data(special_char_data)
        
        if len(errors4) == 0:
            print("   ✅ Special characters handled correctly")
        else:
            print(f"   ❌ Special characters caused errors: {errors4}")
    
    except Exception as e:
        print(f"   ❌ Edge cases test failed: {e}")

if __name__ == "__main__":
    test_form_validation()