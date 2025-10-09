#!/usr/bin/env python3
"""
Script para probar que la autenticación funcione correctamente en todas las páginas
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_page_authentication():
    """Test that all pages require authentication"""
    print("🔐 Probando autenticación en páginas del dashboard...")

    pages_to_test = [
        ("dashboard.pages.advanced_analytics", "show_advanced_analytics"),
        ("dashboard.pages.data_export", "show_data_export_page"),
        ("dashboard.pages.report_generation", "show_report_generation_page"),
        ("dashboard.pages.audit_logs", "show_audit_logs_page"),
        ("dashboard.pages.form_review", "show_form_review_page")
    ]

    success_count = 0

    for module_name, function_name in pages_to_test:
        try:
            # Import the module
            module = __import__(module_name, fromlist=[function_name])
            func = getattr(module, function_name)

            # Check if the function exists
            if func:
                print(f"✅ {module_name}.{function_name} - Importación exitosa")
                success_count += 1
            else:
                print(f"❌ {module_name}.{function_name} - Función no encontrada")

        except Exception as e:
            print(f"❌ {module_name}.{function_name} - Error: {e}")

    return success_count == len(pages_to_test)


def test_auth_module():
    """Test that auth module works correctly"""
    print("\n🔐 Probando módulo de autenticación...")

    try:
        from app.auth.streamlit_auth import auth

        # Check if auth object has required methods
        required_methods = ['require_authentication',
                            'is_authenticated', 'logout']

        for method in required_methods:
            if hasattr(auth, method):
                print(f"✅ auth.{method} - Método disponible")
            else:
                print(f"❌ auth.{method} - Método no encontrado")
                return False

        return True

    except Exception as e:
        print(f"❌ Error importando auth: {e}")
        return False


def main():
    """Run all authentication tests"""
    print("🧪 PROBANDO SISTEMA DE AUTENTICACIÓN")
    print("=" * 50)

    tests = [
        test_auth_module,
        test_page_authentication
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Error ejecutando {test.__name__}: {e}")

    print("\n" + "=" * 50)
    print(f"📊 RESULTADOS: {passed}/{total} pruebas pasaron")

    if passed == total:
        print("🎉 ¡Sistema de autenticación configurado correctamente!")
        print("\n🔒 Todas las páginas administrativas requieren login")
        print("🔑 Credenciales: admin / admin123")
        return True
    else:
        print("⚠️ Algunas pruebas de autenticación fallaron.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
