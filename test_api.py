#!/usr/bin/env python3
"""
Test script for FastAPI endpoints
"""

import sys
import os
import requests
import json
from datetime import date

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://localhost:8000"
ADMIN_CREDENTIALS = ("admin", "admin123")

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Health check passed: {data['status']}")
        return True
    else:
        print(f"❌ Health check failed: {response.status_code}")
        return False

def test_form_submission():
    """Test form submission endpoint"""
    print("Testing form submission...")
    
    form_data = {
        "nombre_completo": "Dr. Test Usuario",
        "correo_institucional": "test@universidad.edu.mx",
        "cursos_capacitacion": [
            {
                "nombre_curso": "Curso de Prueba",
                "fecha": "2024-03-15",
                "horas": 30
            }
        ],
        "publicaciones": [
            {
                "autores": "Test Usuario",
                "titulo": "Artículo de Prueba",
                "evento_revista": "Revista Test",
                "estatus": "ACEPTADO"
            }
        ],
        "eventos_academicos": [],
        "diseno_curricular": [],
        "movilidad": [],
        "reconocimientos": [],
        "certificaciones": []
    }
    
    response = requests.post(
        f"{BASE_URL}/api/formulario/enviar",
        json=form_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Form submission successful: ID {data.get('formulario_id')}")
        return data.get('formulario_id')
    else:
        print(f"❌ Form submission failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_admin_auth():
    """Test admin authentication"""
    print("Testing admin authentication...")
    
    response = requests.get(
        f"{BASE_URL}/auth/verify",
        auth=ADMIN_CREDENTIALS
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Admin auth successful: {data['username']}")
        return True
    else:
        print(f"❌ Admin auth failed: {response.status_code}")
        return False

def test_admin_endpoints(formulario_id):
    """Test admin endpoints"""
    if not formulario_id:
        print("❌ Skipping admin tests - no form ID available")
        return False
    
    print("Testing admin endpoints...")
    
    # Test get pending forms
    response = requests.get(
        f"{BASE_URL}/api/admin/formularios/pendientes",
        auth=ADMIN_CREDENTIALS
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Get pending forms: {data['total']} forms")
    else:
        print(f"❌ Get pending forms failed: {response.status_code}")
        return False
    
    # Test get form details
    response = requests.get(
        f"{BASE_URL}/api/admin/formulario/{formulario_id}",
        auth=ADMIN_CREDENTIALS
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Get form details: {data['nombre_completo']}")
    else:
        print(f"❌ Get form details failed: {response.status_code}")
        return False
    
    # Test approve form
    response = requests.put(
        f"{BASE_URL}/api/admin/formulario/{formulario_id}/aprobar",
        auth=ADMIN_CREDENTIALS
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Approve form: {data['message']}")
    else:
        print(f"❌ Approve form failed: {response.status_code}")
        return False
    
    # Test metrics
    response = requests.get(
        f"{BASE_URL}/api/admin/metricas",
        auth=ADMIN_CREDENTIALS
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Get metrics: {data['total_formularios']} total forms")
    else:
        print(f"❌ Get metrics failed: {response.status_code}")
        return False
    
    return True

def main():
    """Main test function"""
    print("🧪 Testing FastAPI Backend Endpoints")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
    except requests.exceptions.RequestException:
        print("❌ Server is not running. Start with: uvicorn app.main:app --reload")
        return
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Health check
    if test_health_check():
        tests_passed += 1
    
    # Test 2: Form submission
    formulario_id = test_form_submission()
    if formulario_id:
        tests_passed += 1
    
    # Test 3: Admin authentication
    if test_admin_auth():
        tests_passed += 1
    
    # Test 4: Admin endpoints
    if test_admin_endpoints(formulario_id):
        tests_passed += 1
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")

if __name__ == "__main__":
    main()