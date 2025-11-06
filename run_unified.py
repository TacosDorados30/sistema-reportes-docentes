#!/usr/bin/env python3
"""
Script unificado para el Sistema de Reportes Docentes
Maneja tanto el formulario público como el dashboard administrativo
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def setup_environment():
    """Configurar variables de entorno silenciosamente"""
    # Cargar archivo .env si existe
    try:
        from load_env import load_env_file
        load_env_file()
    except ImportError:
        pass
    
    # Variables para optimizar rendimiento
    env_vars = {
        'STREAMLIT_SERVER_ENABLE_CORS': 'false',
        'STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION': 'false',
        'STREAMLIT_BROWSER_GATHER_USAGE_STATS': 'false',
        'STREAMLIT_SERVER_ENABLE_STATIC_SERVING': 'true',
        'STREAMLIT_GLOBAL_DEVELOPMENT_MODE': 'false',
        'STREAMLIT_LOGGER_LEVEL': 'WARNING',
        'STREAMLIT_CLIENT_TOOLBAR_MODE': 'minimal',
        'STREAMLIT_SERVER_MAX_UPLOAD_SIZE': '200',
        'STREAMLIT_SERVER_MAX_MESSAGE_SIZE': '200'
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value

def check_dependencies():
    """Verificar dependencias básicas silenciosamente"""
    try:
        import streamlit
        import pandas
        return True
    except ImportError:
        print("❌ Error: Faltan dependencias. Ejecuta: pip install -r requirements.txt")
        return False

def initialize_system():
    """Inicializar el sistema silenciosamente"""
    # Agregar el directorio raíz al path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from app.startup import startup_application
        result = startup_application()
        return True
        
    except Exception as e:
        print(f"❌ Error inicializando sistema: {e}")
        return False

def start_unified_system():
    """Iniciar el sistema unificado"""
    print("🔗 URLs de acceso:")
    print("   📝 Formulario Público: http://localhost:8501")
    print("   � Dash board Admin:    http://localhost:8501?admin=true")
    print()
    
    # Ruta del archivo principal
    app_path = Path(__file__).parent / "dashboard" / "streamlit_app.py"
    
    try:
        # Configurar variables de entorno adicionales
        env = os.environ.copy()
        
        # Ejecutar Streamlit con configuración optimizada
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(app_path),
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false",
            "--browser.gatherUsageStats", "false",
            "--server.maxUploadSize", "200",
            "--server.maxMessageSize", "200",
            "--logger.level", "warning"
        ], check=True, env=env)
        
    except KeyboardInterrupt:
        print("\n🛑 Sistema detenido por el usuario")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error ejecutando Streamlit: {e}")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")

def main():
    """Función principal"""
    # Configurar entorno silenciosamente
    setup_environment()
    
    # Verificar dependencias
    if not check_dependencies():
        return False
    
    # Inicializar sistema
    if not initialize_system():
        return False
    
    # Iniciar sistema
    start_unified_system()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)