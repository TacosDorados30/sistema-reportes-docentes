#!/usr/bin/env python3
"""
Script de verificación de despliegue
Verifica que todos los componentes del sistema estén funcionando correctamente
"""

import sys
import os
import requests
import time
from datetime import datetime
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class DeploymentVerifier:
    """Verificador de despliegue"""
    
    def __init__(self, base_url="http://localhost:8501"):
        self.base_url = base_url
        self.results = {}
        
    def print_header(self, message):
        """Imprimir encabezado"""
        print("\n" + "=" * 60)
        print(f"🔍 {message}")
        print("=" * 60)
    
    def print_test(self, test_name, success, details=""):
        """Imprimir resultado de test"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        self.results[test_name] = {
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
    
    def test_system_health(self):
        """Test de salud del sistema"""
        self.print_header("VERIFICACIÓN DE SALUD DEL SISTEMA")
        
        try:
            from app.core.health_check import get_health_status
            health = get_health_status()
            
            overall_status = health.get("status", "unknown")
            self.print_test(
                "System Health Check", 
                overall_status in ["healthy", "warning"],
                f"Status: {overall_status}"
            )
            
            # Verificar componentes individuales
            if "checks" in health:
                for component, check in health["checks"].items():
                    component_status = check.get("status", "unknown")
                    self.print_test(
                        f"Component: {component}",
                        component_status == "healthy",
                        f"Status: {component_status}, Message: {check.get('message', 'N/A')}"
                    )
            
        except Exception as e:
            self.print_test("System Health Check", False, f"Error: {e}")
    
    def test_database_connectivity(self):
        """Test de conectividad de base de datos"""
        self.print_header("VERIFICACIÓN DE BASE DE DATOS")
        
        try:
            from app.database.connection import SessionLocal
            from app.database.crud import FormularioCRUD
            
            db = SessionLocal()
            crud = FormularioCRUD(db)
            
            # Test básico de consulta
            stats = crud.get_estadisticas_generales()
            self.print_test(
                "Database Connection",
                stats is not None,
                f"Stats: {stats}"
            )
            
            # Test de formularios pendientes
            pendientes = crud.get_formularios_pendientes()
            self.print_test(
                "Database Queries",
                isinstance(pendientes, list),
                f"Pending forms: {len(pendientes)}"
            )
            
            db.close()
            
        except Exception as e:
            self.print_test("Database Connection", False, f"Error: {e}")
    
    def test_audit_system(self):
        """Test del sistema de auditoría"""
        self.print_header("VERIFICACIÓN DE SISTEMA DE AUDITORÍA")
        
        try:
            from app.core.simple_audit import simple_audit
            from app.models.audit import AuditActionEnum
            
            # Test de logging básico
            log_id = simple_audit.log_action(
                AuditActionEnum.SYSTEM_ACCESS,
                "Deployment verification test",
                "deployment_verifier",
                "Deployment Verifier"
            )
            
            self.print_test(
                "Audit Logging",
                log_id is not None,
                f"Log ID: {log_id}"
            )
            
        except Exception as e:
            self.print_test("Audit Logging", False, f"Error: {e}")
    
    def test_web_interface(self):
        """Test de interfaz web"""
        self.print_header("VERIFICACIÓN DE INTERFAZ WEB")
        
        try:
            # Test de página principal
            response = requests.get(self.base_url, timeout=10)
            self.print_test(
                "Main Page Access",
                response.status_code == 200,
                f"Status Code: {response.status_code}"
            )
            
            # Test de health endpoint (si existe)
            try:
                health_response = requests.get(f"{self.base_url}/health", timeout=5)
                self.print_test(
                    "Health Endpoint",
                    health_response.status_code == 200,
                    f"Status Code: {health_response.status_code}"
                )
            except:
                self.print_test(
                    "Health Endpoint",
                    False,
                    "Endpoint not available (normal for Streamlit)"
                )
            
        except requests.exceptions.ConnectionError:
            self.print_test(
                "Web Interface",
                False,
                f"Cannot connect to {self.base_url}. Is the server running?"
            )
        except Exception as e:
            self.print_test("Web Interface", False, f"Error: {e}")
    
    def test_file_system(self):
        """Test del sistema de archivos"""
        self.print_header("VERIFICACIÓN DE SISTEMA DE ARCHIVOS")
        
        required_dirs = ["data", "logs", "reports", "uploads"]
        
        for directory in required_dirs:
            dir_path = Path(directory)
            exists = dir_path.exists() and dir_path.is_dir()
            
            # Test de escritura
            writable = False
            if exists:
                try:
                    test_file = dir_path / ".write_test"
                    test_file.write_text("test")
                    test_file.unlink()
                    writable = True
                except:
                    pass
            
            self.print_test(
                f"Directory: {directory}",
                exists and writable,
                f"Exists: {exists}, Writable: {writable}"
            )
    
    def test_configuration(self):
        """Test de configuración"""
        self.print_header("VERIFICACIÓN DE CONFIGURACIÓN")
        
        try:
            from app.config import settings
            
            # Test de configuración básica
            self.print_test(
                "App Configuration",
                bool(settings.app_name),
                f"App: {settings.app_name}, Version: {settings.app_version}"
            )
            
            self.print_test(
                "Environment Configuration",
                settings.environment in ["development", "production", "testing"],
                f"Environment: {settings.environment}"
            )
            
            self.print_test(
                "Database Configuration",
                bool(settings.database_url),
                f"Database: {settings.database_url.split('://')[0]}://***"
            )
            
            # Verificar configuración de seguridad en producción
            if settings.is_production:
                security_ok = (
                    settings.secret_key != "dev-secret-key-change-in-production" and
                    not settings.debug
                )
                self.print_test(
                    "Production Security",
                    security_ok,
                    f"Debug: {settings.debug}, Secret Key Changed: {settings.secret_key != 'dev-secret-key-change-in-production'}"
                )
            
        except Exception as e:
            self.print_test("Configuration", False, f"Error: {e}")
    
    def test_export_system(self):
        """Test del sistema de exportación"""
        self.print_header("VERIFICACIÓN DE SISTEMA DE EXPORTACIÓN")
        
        try:
            from app.utils.export_utils import DataExporter
            
            exporter = DataExporter()
            
            # Test con datos de ejemplo
            test_data = [
                {"nombre": "Test User", "email": "test@example.com", "cursos": 1}
            ]
            
            # Test CSV export
            csv_result = exporter.export_to_csv(test_data, "deployment_test")
            self.print_test(
                "CSV Export",
                csv_result is not None and len(csv_result) > 0,
                f"CSV Length: {len(csv_result) if csv_result else 0}"
            )
            
        except Exception as e:
            self.print_test("Export System", False, f"Error: {e}")
    
    def test_report_generation(self):
        """Test de generación de reportes"""
        self.print_header("VERIFICACIÓN DE GENERACIÓN DE REPORTES")
        
        try:
            from app.reports.nlg_engine import NLGEngine
            
            nlg = NLGEngine()
            
            # Test de generación de texto
            test_data = {
                "total_docentes": 5,
                "total_cursos": 25,
                "total_horas": 500
            }
            
            report_text = nlg.generar_resumen_actividades(test_data)
            self.print_test(
                "Report Generation",
                report_text is not None and len(report_text) > 50,
                f"Report Length: {len(report_text) if report_text else 0}"
            )
            
        except Exception as e:
            self.print_test("Report Generation", False, f"Error: {e}")
    
    def run_all_tests(self):
        """Ejecutar todas las verificaciones"""
        print("🚀 VERIFICACIÓN DE DESPLIEGUE")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Base URL: {self.base_url}")
        
        # Ejecutar todos los tests
        tests = [
            self.test_system_health,
            self.test_database_connectivity,
            self.test_audit_system,
            self.test_file_system,
            self.test_configuration,
            self.test_export_system,
            self.test_report_generation,
            self.test_web_interface,  # Al final porque puede fallar si no está corriendo
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                test_name = test.__name__.replace("test_", "").replace("_", " ").title()
                self.print_test(test_name, False, f"Unexpected error: {e}")
        
        # Resumen final
        self.print_summary()
    
    def print_summary(self):
        """Imprimir resumen de resultados"""
        self.print_header("RESUMEN DE VERIFICACIÓN")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total de pruebas: {total_tests}")
        print(f"Pruebas exitosas: {passed_tests}")
        print(f"Pruebas fallidas: {failed_tests}")
        print(f"Porcentaje de éxito: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ PRUEBAS FALLIDAS:")
            for test_name, result in self.results.items():
                if not result["success"]:
                    print(f"  - {test_name}: {result['details']}")
        
        print("\n" + "="*60)
        if failed_tests == 0:
            print("🎉 ¡DESPLIEGUE VERIFICADO EXITOSAMENTE!")
            print("✨ Todos los componentes están funcionando correctamente")
        elif failed_tests <= 2:
            print("⚠️  DESPLIEGUE MAYORMENTE EXITOSO")
            print("🔧 Algunos componentes menores necesitan atención")
        else:
            print("❌ DESPLIEGUE CON PROBLEMAS")
            print("🚨 Varios componentes necesitan corrección")
        
        return failed_tests == 0

def main():
    """Función principal"""
    base_url = "http://localhost:8501"
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    verifier = DeploymentVerifier(base_url)
    success = verifier.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()