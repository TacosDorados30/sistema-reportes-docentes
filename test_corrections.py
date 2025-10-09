#!/usr/bin/env python3
"""
Script para probar las correcciones aplicadas
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_enum_imports():
    """Test that all enums are properly defined"""
    print("🔍 Probando enums...")
    
    try:
        from app.models.schemas import (
            TipoMovilidad, EstatusPublicacion, 
            TipoReconocimiento, TipoParticipacion
        )
        
        print(f"✅ TipoMovilidad: {list(TipoMovilidad)}")
        print(f"✅ EstatusPublicacion: {list(EstatusPublicacion)}")
        print(f"✅ TipoReconocimiento: {list(TipoReconocimiento)}")
        print(f"✅ TipoParticipacion: {list(TipoParticipacion)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en enums: {e}")
        return False

def test_form_data_creation():
    """Test FormData creation with correct enum values"""
    print("\n🔍 Probando creación de FormData...")
    
    try:
        from app.models.schemas import FormData
        from datetime import date
        
        # Test data with correct enum values
        form_data = FormData(
            nombre_completo="Test User",
            correo_institucional="test@universidad.edu.mx",
            año_academico=2025,
            trimestre="Trimestre 1",
            cursos_capacitacion=[],
            publicaciones=[{
                'autores': 'Test Author',
                'titulo': 'Test Title',
                'evento_revista': 'Test Journal',
                'estatus': 'PUBLICADO'
            }],
            eventos_academicos=[{
                'nombre_evento': 'Test Event',
                'fecha': date.today(),
                'tipo_participacion': 'PONENTE'
            }],
            diseno_curricular=[],
            movilidad=[{
                'descripcion': 'Test Mobility',
                'tipo': 'NACIONAL',
                'fecha': date.today()
            }],
            reconocimientos=[{
                'nombre': 'Test Recognition',
                'tipo': 'PREMIO',
                'fecha': date.today()
            }],
            certificaciones=[]
        )
        
        print("✅ FormData creado exitosamente con enums correctos")
        return True
        
    except Exception as e:
        print(f"❌ Error creando FormData: {e}")
        return False

def test_dashboard_imports():
    """Test dashboard page imports"""
    print("\n🔍 Probando importaciones del dashboard...")
    
    pages_to_test = [
        "dashboard.pages.advanced_analytics",
        "dashboard.pages.data_export", 
        "dashboard.pages.report_generation"
    ]
    
    success_count = 0
    
    for page in pages_to_test:
        try:
            __import__(page)
            print(f"✅ {page}")
            success_count += 1
        except Exception as e:
            print(f"❌ {page}: {e}")
    
    return success_count == len(pages_to_test)

def main():
    """Run all tests"""
    print("🧪 PROBANDO CORRECCIONES APLICADAS")
    print("=" * 40)
    
    tests = [
        test_enum_imports,
        test_form_data_creation,
        test_dashboard_imports
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
        print("🎉 ¡Todas las correcciones funcionan correctamente!")
        return True
    else:
        print("⚠️ Algunas correcciones necesitan revisión.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)