#!/usr/bin/env python3
"""
Script para ejecutar la aplicación con optimizaciones de rendimiento
"""

import os
import sys
import subprocess

def setup_environment():
    """Configurar variables de entorno para mejor rendimiento"""
    
    # Desactivar optimizaciones costosas
    os.environ["OPTIMIZE_DB"] = "false"
    os.environ["ENABLE_MONITORING"] = "false"
    os.environ["DEBUG"] = "false"
    os.environ["LOG_LEVEL"] = "WARNING"
    
    # Configuración de Streamlit para mejor rendimiento
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "false"
    os.environ["STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION"] = "false"
    
    print("✅ Variables de entorno configuradas para mejor rendimiento")

def run_streamlit():
    """Ejecutar Streamlit con configuración optimizada"""
    
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        "dashboard/streamlit_app.py",
        "--server.headless", "true",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false",
        "--browser.gatherUsageStats", "false",
        "--global.developmentMode", "false"
    ]
    
    print("🚀 Iniciando Streamlit con configuración optimizada...")
    print("📋 Configuraciones aplicadas:")
    print("   - Optimización de BD: DESACTIVADA")
    print("   - Monitoreo: DESACTIVADO") 
    print("   - Debug: DESACTIVADO")
    print("   - CORS: DESACTIVADO")
    print("   - Estadísticas: DESACTIVADAS")
    print("")
    print("🔗 La aplicación debería cargar más rápido ahora")
    print("=" * 50)
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 Aplicación detenida por el usuario")
    except Exception as e:
        print(f"\n❌ Error al ejecutar Streamlit: {e}")

if __name__ == "__main__":
    setup_environment()
    run_streamlit()