#!/usr/bin/env python3
"""
Prueba rápida del sistema antes de ejecutar
"""

import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def quick_system_test():
    """Prueba rápida de componentes críticos"""
    
    print("⚡ PRUEBA RÁPIDA DEL SISTEMA")
    print("=" * 40)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Importaciones básicas
    total_tests += 1
    try:
        import streamlit as st
        import pandas as pd
        import plotly.express as px
        print("✅ Librerías principales importadas")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Error importando librerías: {e}")
    
    # Test 2: Configuración
    total_tests += 1
    try:
        from app.config import settings
        print(f"✅ Configuración cargada - Entorno: {settings.environment}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
    
    # Test 3: Base de datos
    total_tests += 1
    try:
        from app.database.connection import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        print("✅ Base de datos conectada")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
    
    # Test 4: Auditoría
    total_tests += 1
    try:
        from app.core.simple_audit import simple_audit
        from app.models.audit import AuditActionEnum
        log_id = simple_audit.log_action(
            AuditActionEnum.SYSTEM_ACCESS,
            "Quick test execution",
            "quick_test",
            "Quick Test"
        )
        print("✅ Sistema de auditoría funcionando")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Error en auditoría: {e}")
    
    # Test 5: Health check
    total_tests += 1
    try:
        from app.core.health_check import get_simple_health
        health = get_simple_health()
        print(f"✅ Health check: {health['status']}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Error en health check: {e}")
    
    # Test 6: Archivos de configuración
    total_tests += 1
    try:
        config_files = [
            ".streamlit/config.toml",
            "requirements.txt",
            "dashboard/streamlit_app.py"
        ]
        
        missing_files = [f for f in config_files if not os.path.exists(f)]
        
        if not missing_files:
            print("✅ Archivos de configuración presentes")
            tests_passed += 1
        else:
            print(f"❌ Archivos faltantes: {missing_files}")
    except Exception as e:
        print(f"❌ Error verificando archivos: {e}")
    
    # Resumen
    print("\n" + "=" * 40)
    print(f"📊 RESULTADO: {tests_passed}/{total_tests} pruebas exitosas")
    
    if tests_passed == total_tests:
        print("🎉 ¡SISTEMA LISTO PARA EJECUTAR!")
        return True
    elif tests_passed >= total_tests - 1:
        print("⚠️  Sistema mayormente listo (problemas menores)")
        return True
    else:
        print("❌ Sistema necesita correcciones")
        return False

if __name__ == "__main__":
    success = quick_system_test()
    
    if success:
        print("\n🚀 Para ejecutar el sistema:")
        print("   python start_system.py")
        print("\n🌐 O directamente:")
        print("   streamlit run dashboard/streamlit_app.py")
    else:
        print("\n🔧 Corrige los errores antes de ejecutar")
    
    sys.exit(0 if success else 1)