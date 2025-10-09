#!/usr/bin/env python3
"""
Script para iniciar solo el formulario público de docentes
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Mostrar banner del formulario público"""
    print("📝" * 30)
    print("📝  FORMULARIO PÚBLICO DOCENTES  📝")
    print("📝" * 30)
    print("🎯 Solo formulario - Sin autenticación")
    print()

def check_dependencies():
    """Verificar dependencias básicas"""
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
    
    return True

def initialize_system():
    """Inicializar solo la base de datos"""
    print("🚀 Inicializando base de datos...")
    
    # Agregar el directorio raíz al path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from app.database.connection import init_database
        init_database()
        print("✅ Base de datos inicializada")
        return True
        
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        return False

def start_public_form():
    """Iniciar el formulario público"""
    print("🌐 Iniciando formulario público...")
    print()
    print("🔗 URL del formulario:")
    print("   - http://localhost:8501")
    print()
    print("📋 Características:")
    print("   ✅ Acceso directo sin login")
    print("   ✅ Formulario completo para docentes")
    print("   ✅ Validaciones en tiempo real")
    print("   ✅ Confirmación de envío")
    print()
    print("🚀 Iniciando aplicación...")
    print("   (Presiona Ctrl+C para detener)")
    print()
    
    # Ruta del formulario público
    form_path = Path(__file__).parent / "dashboard" / "public_form.py"
    
    try:
        # Configurar variables de entorno
        env = os.environ.copy()
        env['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'
        env['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'false'
        env['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
        
        # Ejecutar Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(form_path),
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false",
            "--browser.gatherUsageStats", "false"
        ], check=True, env=env)
        
    except KeyboardInterrupt:
        print("\n🛑 Formulario detenido por el usuario")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error ejecutando Streamlit: {e}")
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
    
    print("\n✅ Sistema listo!")
    print("📝 Abriendo formulario público...")
    
    # Pequeña pausa
    time.sleep(1)
    
    # Iniciar formulario
    start_public_form()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)