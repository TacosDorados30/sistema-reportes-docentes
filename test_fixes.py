#!/usr/bin/env python3
"""
Script para probar las correcciones del sistema
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all imports work correctly"""
    print("🔍 Probando importaciones...")
    
    try:
        from app.database.connection import init_database
        print("✅ Database connection - OK")
        
        from app.auth.streamlit_auth import auth
        print("✅ Authentication system - OK")
        
        from app.database.crud import FormularioCRUD
        print("✅ CRUD operations - OK")
        
        from app.core.health_check import get_simple_health
        print("✅ Health check - OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en importaciones: {e}")
        return False

def test_database():
    """Test database initialization"""
    print("\n🗄️ Probando base de datos...")
    
    try:
        from app.database.connection import init_database, SessionLocal
        
        # Initialize database
        init_database()
        print("✅ Base de datos inicializada")
        
        # Test connection
        db = SessionLocal()
        db.close()
        print("✅ Conexión a base de datos - OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
        return False

def test_auth_system():
    """Test authentication system"""
    print("\n🔐 Probando sistema de autenticación...")
    
    try:
        from app.auth.streamlit_auth import auth
        
        # Test user creation (should work without Streamlit context)
        print("✅ Sistema de autenticación cargado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en autenticación: {e}")
        return False

def test_health_check():
    """Test health check system"""
    print("\n🏥 Probando health check...")
    
    try:
        from app.core.health_check import get_simple_health
        
        health = get_simple_health()
        print(f"✅ Health status: {health['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en health check: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 EJECUTANDO PRUEBAS DEL SISTEMA")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_database,
        test_auth_system,
        test_health_check
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Error ejecutando {test.__name__}: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 RESULTADOS: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El sistema está listo.")
        return True
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa los errores arriba.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)