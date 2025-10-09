#!/usr/bin/env python3
"""
Script para verificar que todos los módulos principales funcionen correctamente
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_dashboard_modules():
    """Test all dashboard modules"""
    print("🔍 Verificando módulos del dashboard...")
    
    modules_to_test = [
        ("dashboard.pages.advanced_analytics", "show_advanced_analytics"),
        ("dashboard.pages.data_export", "show_data_export_page"),
        ("dashboard.pages.report_generation", "show_report_generation_page"),
        ("dashboard.pages.audit_logs", "show_audit_logs_page"),
    ]
    
    success_count = 0
    total_count = len(modules_to_test)
    
    for module_name, function_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[function_name])
            getattr(module, function_name)
            print(f"✅ {module_name} - OK")
            success_count += 1
        except Exception as e:
            print(f"❌ {module_name} - Error: {e}")
    
    return success_count, total_count

def test_core_modules():
    """Test core application modules"""
    print("\n🔍 Verificando módulos principales...")
    
    modules_to_test = [
        "app.database.connection",
        "app.auth.streamlit_auth",
        "app.database.crud",
        "app.core.health_check",
        "app.startup"
    ]
    
    success_count = 0
    total_count = len(modules_to_test)
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name} - OK")
            success_count += 1
        except Exception as e:
            print(f"❌ {module_name} - Error: {e}")
    
    return success_count, total_count

def main():
    """Run all module tests"""
    print("🧪 VERIFICACIÓN DE MÓDULOS DEL SISTEMA")
    print("=" * 50)
    
    # Test core modules
    core_success, core_total = test_core_modules()
    
    # Test dashboard modules
    dashboard_success, dashboard_total = test_dashboard_modules()
    
    # Summary
    total_success = core_success + dashboard_success
    total_modules = core_total + dashboard_total
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTADOS:")
    print(f"   - Módulos principales: {core_success}/{core_total}")
    print(f"   - Módulos dashboard: {dashboard_success}/{dashboard_total}")
    print(f"   - Total: {total_success}/{total_modules}")
    
    if total_success == total_modules:
        print("\n🎉 ¡Todos los módulos funcionan correctamente!")
        return True
    else:
        print(f"\n⚠️ {total_modules - total_success} módulos tienen problemas")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)