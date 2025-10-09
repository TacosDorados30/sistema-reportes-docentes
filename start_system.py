#!/usr/bin/env python3
"""
Script para iniciar el Sistema de Reportes Docentes
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Mostrar banner del sistema"""
    print("🎓" * 30)
    print("🎓  SISTEMA DE REPORTES DOCENTES  🎓")
    print("🎓" * 30)
    print()
    print("📋 Preparando el sistema...")

def check_dependencies():
    """Verificar dependencias"""
    print("🔍 Verificando dependencias...")
    
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__}")
    except ImportError:
        print("❌ Streamlit no encontrado")
        return False
    
    try:
        import pandas
        print(f"✅ Pandas {pandas.__version__}")
    except ImportError:
        print("❌ Pandas no encontrado")
        return False
    
    try:
        import plotly
        print(f"✅ Plotly {plotly.__version__}")
    except ImportError:
        print("❌ Plotly no encontrado")
        return False
    
    return True

def initialize_system():
    """Inicializar el sistema"""
    print("🚀 Inicializando sistema...")
    
    # Agregar el directorio raíz al path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Inicializar base de datos
        from app.database.connection import init_database
        init_database()
        print("✅ Base de datos inicializada")
        
        # Verificar health check
        from app.core.health_check import get_simple_health
        health = get_simple_health()
        print(f"✅ Sistema saludable: {health['status']}")
        
        # Crear datos de prueba si no existen
        create_sample_data()
        
        return True
        
    except Exception as e:
        print(f"❌ Error inicializando sistema: {e}")
        return False

def create_sample_data():
    """Crear datos de prueba si la base de datos está vacía"""
    print("📊 Verificando datos de prueba...")
    
    try:
        from app.database.connection import SessionLocal
        from app.database.crud import FormularioCRUD
        
        db = SessionLocal()
        crud = FormularioCRUD(db)
        
        stats = crud.get_estadisticas_generales()
        total_formularios = stats.get('total_formularios', 0)
        
        if total_formularios == 0:
            print("📝 Creando datos de prueba...")
            
            # Crear algunos logs de auditoría de ejemplo
            from app.core.simple_audit import simple_audit
            from app.models.audit import AuditActionEnum
            
            simple_audit.log_action(
                AuditActionEnum.SYSTEM_ACCESS,
                "Sistema iniciado correctamente",
                "system",
                "Sistema"
            )
            
            simple_audit.log_login("admin", "Administrador", True)
            
            print("✅ Datos de prueba creados")
        else:
            print(f"✅ Base de datos contiene {total_formularios} formularios")
        
        db.close()
        
    except Exception as e:
        print(f"⚠️  Error creando datos de prueba: {e}")

def start_streamlit():
    """Iniciar Streamlit"""
    print("🌐 Iniciando servidor web...")
    print()
    print("🔗 URLs disponibles:")
    print("   - El puerto se asignará automáticamente")
    print("   - Streamlit mostrará la URL exacta al iniciar")
    print()
    print("🔑 Credenciales de administrador:")
    print("   - Usuario: admin")
    print("   - Contraseña: admin123")
    print()
    print("📋 Funcionalidades disponibles:")
    print("   ✅ Formulario público para docentes")
    print("   ✅ Panel administrativo")
    print("   ✅ Visualizaciones interactivas")
    print("   ✅ Exportación de datos")
    print("   ✅ Generación de reportes")
    print("   ✅ Logs de auditoría")
    print()
    print("🚀 Iniciando aplicación...")
    print("   (Presiona Ctrl+C para detener)")
    print()
    
    # Cambiar al directorio del dashboard
    dashboard_path = Path(__file__).parent / "dashboard" / "streamlit_app.py"
    
    try:
        # Ejecutar Streamlit con configuración mejorada
        env = os.environ.copy()
        env['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'
        env['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'false'
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path),
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ], check=True, env=env)
        
    except KeyboardInterrupt:
        print("\n🛑 Sistema detenido por el usuario")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error ejecutando Streamlit: {e}")
        print("\n💡 Sugerencias:")
        print("   - Verifica que no haya otro servidor corriendo")
        print("   - Intenta ejecutar: streamlit run dashboard/streamlit_app.py")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")

def main():
    """Función principal"""
    print_banner()
    
    # Verificar dependencias
    if not check_dependencies():
        print("\n❌ Faltan dependencias. Ejecuta: pip install -r requirements.txt")
        return False
    
    # Inicializar sistema
    if not initialize_system():
        print("\n❌ Error inicializando sistema")
        return False
    
    print("\n✅ Sistema listo para usar!")
    print("🌐 Abriendo servidor web...")
    
    # Pequeña pausa para que el usuario lea
    time.sleep(2)
    
    # Iniciar Streamlit
    start_streamlit()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)