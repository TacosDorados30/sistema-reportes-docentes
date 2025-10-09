#!/usr/bin/env python3
"""
Script alternativo para iniciar el Sistema de Reportes Docentes
Versión mejorada con mejor manejo de errores
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
    print("📋 Versión mejorada con correcciones")
    print()

def check_python_version():
    """Verificar versión de Python"""
    if sys.version_info < (3, 8):
        print("❌ Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Verificar dependencias críticas"""
    print("🔍 Verificando dependencias...")
    
    required_packages = [
        ('streamlit', 'Streamlit'),
        ('pandas', 'Pandas'),
        ('plotly', 'Plotly'),
        ('sqlalchemy', 'SQLAlchemy'),
        ('pydantic', 'Pydantic')
    ]
    
    missing = []
    
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} no encontrado")
            missing.append(package)
    
    if missing:
        print(f"\n📦 Instala las dependencias faltantes:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True

def initialize_system():
    """Inicializar el sistema con mejor manejo de errores"""
    print("🚀 Inicializando sistema...")
    
    try:
        # Agregar el directorio raíz al path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Probar importaciones críticas
        from app.database.connection import init_database
        from app.core.health_check import get_simple_health
        
        # Inicializar base de datos
        init_database()
        print("✅ Base de datos inicializada")
        
        # Verificar health check
        health = get_simple_health()
        print(f"✅ Sistema saludable: {health['status']}")
        
        # Crear datos de prueba si es necesario
        create_sample_data()
        
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Ejecuta: pip install -r requirements.txt")
        return False
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
        
        # Verificar si hay datos
        stats = crud.get_estadisticas_generales()
        total_formularios = stats.get('total_formularios', 0)
        
        if total_formularios == 0:
            print("📝 Creando datos de prueba...")
            
            # Crear logs de auditoría básicos
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

def find_available_port():
    """Encontrar un puerto disponible"""
    import socket
    
    ports_to_try = [8501, 8502, 8503, 8504, 8505, 8506, 8507, 8508]
    
    for port in ports_to_try:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                if result != 0:  # Port is available
                    return port
        except Exception:
            continue
    
    # If no specific port is available, let Streamlit choose
    return 0

def start_streamlit():
    """Iniciar Streamlit con configuración optimizada"""
    print("🌐 Iniciando servidor web...")
    
    # Encontrar puerto disponible
    port = find_available_port()
    
    print()
    if port and port != 0:
        print("🔗 URLs del sistema:")
        print(f"   - Principal: http://localhost:{port}")
        print(f"   - Red local: http://127.0.0.1:{port}")
    else:
        print("🔗 URLs del sistema:")
        print("   - Streamlit asignará automáticamente un puerto disponible")
        print("   - La URL exacta se mostrará al iniciar")
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
    
    # Ruta del dashboard
    dashboard_path = Path(__file__).parent / "dashboard" / "streamlit_app.py"
    
    if not dashboard_path.exists():
        print(f"❌ No se encontró el archivo: {dashboard_path}")
        return False
    
    try:
        # Configurar variables de entorno
        env = os.environ.copy()
        env['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'
        env['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'false'
        env['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
        
        # Ejecutar Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path),
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false",
            "--browser.gatherUsageStats", "false"
        ]
        
        # Solo agregar puerto si encontramos uno específico
        if port and port != 0:
            cmd.extend(["--server.port", str(port)])
        
        subprocess.run(cmd, check=True, env=env)
        
        return True
        
    except KeyboardInterrupt:
        print("\n🛑 Sistema detenido por el usuario")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error ejecutando Streamlit: {e}")
        print("\n💡 Sugerencias:")
        print("   - Verifica que Streamlit esté instalado: pip install streamlit")
        print("   - Intenta manualmente: streamlit run dashboard/streamlit_app.py")
        return False
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return False

def main():
    """Función principal mejorada"""
    print_banner()
    
    # Verificar Python
    if not check_python_version():
        return False
    
    # Verificar dependencias
    if not check_dependencies():
        return False
    
    # Inicializar sistema
    if not initialize_system():
        return False
    
    print("\n✅ Sistema listo para usar!")
    print("🌐 Abriendo servidor web...")
    
    # Pequeña pausa
    time.sleep(1)
    
    # Iniciar Streamlit
    return start_streamlit()

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Proceso interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Error crítico: {e}")
        sys.exit(1)