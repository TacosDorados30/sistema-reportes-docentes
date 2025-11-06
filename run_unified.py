#!/usr/bin/env python3
"""
Sistema de Reportes Docentes - Launcher Optimizado
Punto de entrada único para el sistema completo
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_environment():
    """Configurar variables de entorno para rendimiento óptimo"""
    # Cargar archivo .env si existe
    try:
        from load_env import load_env_file
        load_env_file()
    except ImportError:
        pass
    
    # Configuración optimizada para Streamlit
    os.environ.update({
        'STREAMLIT_SERVER_ENABLE_CORS': 'false',
        'STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION': 'false',
        'STREAMLIT_BROWSER_GATHER_USAGE_STATS': 'false',
        'STREAMLIT_GLOBAL_DEVELOPMENT_MODE': 'false',
        'STREAMLIT_LOGGER_LEVEL': 'WARNING',
        'STREAMLIT_CLIENT_TOOLBAR_MODE': 'minimal',
        'STREAMLIT_SERVER_MAX_UPLOAD_SIZE': '200',
        'STREAMLIT_SERVER_MAX_MESSAGE_SIZE': '200'
    })

def check_dependencies():
    """Verificar dependencias críticas"""
    try:
        import streamlit, pandas, plotly, sqlalchemy
        return True
    except ImportError:
        print("❌ Faltan dependencias. Ejecuta: pip install -r requirements.txt")
        return False

def initialize_system():
    """Inicializar sistema de forma silenciosa"""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from app.startup import startup_application
        startup_application()
        return True
    except Exception as e:
        print(f"❌ Error inicializando: {e}")
        return False

def start_system():
    """Iniciar el sistema de forma optimizada"""
    print("🚀 Iniciando Sistema de Reportes Docentes...")
    print("🔗 Acceso: http://localhost:8501")
    
    app_path = Path(__file__).parent / "dashboard" / "streamlit_app.py"
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(app_path),
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false",
            "--browser.gatherUsageStats", "false",
            "--server.maxUploadSize", "200",
            "--logger.level", "warning"
        ], check=True, env=os.environ.copy())
        
    except KeyboardInterrupt:
        print("\n🛑 Sistema detenido")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def main():
    """Función principal optimizada"""
    setup_environment()
    
    if not check_dependencies() or not initialize_system():
        return False
    
    start_system()
    return True

if __name__ == "__main__":
    sys.exit(0 if main() else 1)