#!/usr/bin/env python3
"""
Script de despliegue automatizado para el Sistema de Reportes Docentes
"""

import os
import sys
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

class DeploymentManager:
    """Gestor de despliegue automatizado"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backup_dir = self.project_root / "backups"
        self.data_dir = self.project_root / "data"
        self.logs_dir = self.project_root / "logs"
        
    def print_header(self, message):
        """Imprimir encabezado con formato"""
        print("\n" + "=" * 60)
        print(f"🚀 {message}")
        print("=" * 60)
    
    def print_step(self, step, message):
        """Imprimir paso con formato"""
        print(f"\n{step}. {message}")
        print("-" * 40)
    
    def run_command(self, command, description=""):
        """Ejecutar comando y manejar errores"""
        print(f"Ejecutando: {command}")
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                check=True, 
                capture_output=True, 
                text=True
            )
            if result.stdout:
                print(f"✅ {description}: Exitoso")
                if result.stdout.strip():
                    print(f"   Output: {result.stdout.strip()}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ {description}: Error")
            print(f"   Error: {e.stderr}")
            return False
    
    def check_prerequisites(self):
        """Verificar prerequisitos del sistema"""
        self.print_step("1", "Verificando Prerequisitos")
        
        # Verificar Python
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            print("❌ Python 3.8+ requerido")
            return False
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Verificar pip
        if not self.run_command("pip --version", "Verificar pip"):
            return False
        
        # Verificar git
        if not self.run_command("git --version", "Verificar git"):
            print("⚠️  Git no encontrado - algunas funciones pueden no estar disponibles")
        
        return True
    
    def create_directories(self):
        """Crear directorios necesarios"""
        self.print_step("2", "Creando Directorios")
        
        directories = [
            self.data_dir,
            self.logs_dir,
            self.backup_dir,
            self.project_root / "reports",
            self.project_root / "uploads"
        ]
        
        for directory in directories:
            try:
                directory.mkdir(exist_ok=True)
                print(f"✅ Directorio creado: {directory}")
            except Exception as e:
                print(f"❌ Error creando {directory}: {e}")
                return False
        
        return True
    
    def backup_existing_data(self):
        """Hacer backup de datos existentes"""
        self.print_step("3", "Backup de Datos Existentes")
        
        db_file = self.data_dir / "reportes_docentes.db"
        if db_file.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"reportes_docentes_backup_{timestamp}.db"
            
            try:
                shutil.copy2(db_file, backup_file)
                print(f"✅ Backup creado: {backup_file}")
            except Exception as e:
                print(f"❌ Error en backup: {e}")
                return False
        else:
            print("ℹ️  No hay base de datos existente para respaldar")
        
        return True
    
    def install_dependencies(self):
        """Instalar dependencias"""
        self.print_step("4", "Instalando Dependencias")
        
        # Actualizar pip
        if not self.run_command("pip install --upgrade pip", "Actualizar pip"):
            return False
        
        # Instalar dependencias del proyecto
        if not self.run_command("pip install -r requirements.txt", "Instalar dependencias"):
            return False
        
        return True
    
    def setup_environment(self):
        """Configurar entorno"""
        self.print_step("5", "Configurando Entorno")
        
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"
        
        if not env_file.exists() and env_example.exists():
            try:
                shutil.copy2(env_example, env_file)
                print("✅ Archivo .env creado desde .env.example")
                print("⚠️  IMPORTANTE: Edita .env con tus configuraciones específicas")
            except Exception as e:
                print(f"❌ Error creando .env: {e}")
                return False
        elif env_file.exists():
            print("✅ Archivo .env ya existe")
        else:
            print("⚠️  No se encontró .env.example")
        
        return True
    
    def initialize_database(self):
        """Inicializar base de datos"""
        self.print_step("6", "Inicializando Base de Datos")
        
        init_command = 'python -c "from app.database.connection import init_database; init_database()"'
        if not self.run_command(init_command, "Inicializar base de datos"):
            return False
        
        return True
    
    def run_tests(self):
        """Ejecutar pruebas del sistema"""
        self.print_step("7", "Ejecutando Pruebas del Sistema")
        
        if not self.run_command("python test_sistema_completo.py", "Pruebas integrales"):
            print("⚠️  Las pruebas fallaron - revisa los errores antes de continuar")
            return False
        
        return True
    
    def optimize_system(self):
        """Optimizar sistema"""
        self.print_step("8", "Optimizando Sistema")
        
        optimize_command = 'python -c "from app.database.optimization import optimize_database; optimize_database()"'
        if not self.run_command(optimize_command, "Optimizar base de datos"):
            print("⚠️  Optimización falló - el sistema funcionará pero puede ser más lento")
        
        return True
    
    def generate_deployment_info(self):
        """Generar información de despliegue"""
        self.print_step("9", "Generando Información de Despliegue")
        
        deployment_info = f"""
# Información de Despliegue
Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Sistema: {os.name}
Python: {sys.version}
Directorio: {self.project_root}

## Archivos de Configuración
- .env: {'✅ Existe' if (self.project_root / '.env').exists() else '❌ No existe'}
- .streamlit/config.toml: {'✅ Existe' if (self.project_root / '.streamlit/config.toml').exists() else '❌ No existe'}
- requirements.txt: {'✅ Existe' if (self.project_root / 'requirements.txt').exists() else '❌ No existe'}

## Directorios
- data/: {'✅ Existe' if self.data_dir.exists() else '❌ No existe'}
- logs/: {'✅ Existe' if self.logs_dir.exists() else '❌ No existe'}
- backups/: {'✅ Existe' if self.backup_dir.exists() else '❌ No existe'}

## Base de Datos
- Archivo: {self.data_dir / 'reportes_docentes.db'}
- Existe: {'✅ Sí' if (self.data_dir / 'reportes_docentes.db').exists() else '❌ No'}

## Comandos para Ejecutar
```bash
# Ejecutar aplicación
streamlit run dashboard/streamlit_app.py

# Ejecutar pruebas
python test_sistema_completo.py

# Ver health check
python -c "from app.core.health_check import get_health_status; import json; print(json.dumps(get_health_status(), indent=2))"
```
"""
        
        try:
            with open(self.project_root / "DEPLOYMENT_INFO.md", "w", encoding="utf-8") as f:
                f.write(deployment_info)
            print("✅ Información de despliegue guardada en DEPLOYMENT_INFO.md")
        except Exception as e:
            print(f"⚠️  Error guardando información: {e}")
        
        return True
    
    def deploy_local(self):
        """Despliegue local completo"""
        self.print_header("DESPLIEGUE LOCAL")
        
        steps = [
            self.check_prerequisites,
            self.create_directories,
            self.backup_existing_data,
            self.install_dependencies,
            self.setup_environment,
            self.initialize_database,
            self.run_tests,
            self.optimize_system,
            self.generate_deployment_info
        ]
        
        for step in steps:
            if not step():
                print(f"\n❌ Despliegue falló en: {step.__name__}")
                return False
        
        self.print_success_message()
        return True
    
    def deploy_production_prep(self):
        """Preparar para despliegue en producción"""
        self.print_header("PREPARACIÓN PARA PRODUCCIÓN")
        
        print("📋 Lista de verificación para producción:")
        print()
        
        checklist = [
            "✅ Cambiar SECRET_KEY en configuración de producción",
            "✅ Configurar ADMIN_PASSWORD_HASH seguro",
            "✅ Configurar base de datos PostgreSQL (recomendado)",
            "✅ Configurar variables de entorno en Streamlit Cloud",
            "✅ Verificar que DEBUG=false en producción",
            "✅ Configurar LOG_LEVEL=INFO o WARNING",
            "✅ Revisar configuración de CORS",
            "✅ Configurar backup automático",
            "✅ Configurar monitoreo de health checks",
            "✅ Probar el sistema completamente"
        ]
        
        for item in checklist:
            print(f"  {item}")
        
        print("\n📁 Archivos importantes para Streamlit Cloud:")
        print("  - requirements.txt")
        print("  - packages.txt")
        print("  - .streamlit/config.toml")
        print("  - .streamlit/secrets.toml (configurar en dashboard)")
        print("  - dashboard/streamlit_app.py (archivo principal)")
        
        print("\n🔗 Pasos para Streamlit Cloud:")
        print("  1. Subir código a GitHub")
        print("  2. Ir a share.streamlit.io")
        print("  3. Conectar repositorio")
        print("  4. Configurar secretos")
        print("  5. Desplegar")
        
        return True
    
    def print_success_message(self):
        """Imprimir mensaje de éxito"""
        print("\n" + "🎉" * 20)
        print("¡DESPLIEGUE COMPLETADO EXITOSAMENTE!")
        print("🎉" * 20)
        print()
        print("📋 Próximos pasos:")
        print("  1. Editar .env con tus configuraciones específicas")
        print("  2. Ejecutar: streamlit run dashboard/streamlit_app.py")
        print("  3. Abrir http://localhost:8501 en tu navegador")
        print("  4. Probar el sistema completamente")
        print()
        print("📚 Documentación:")
        print("  - README.md: Documentación completa")
        print("  - DEPLOYMENT_INFO.md: Información de este despliegue")
        print("  - .env.example: Ejemplo de configuración")
        print()
        print("🔧 Comandos útiles:")
        print("  - Pruebas: python test_sistema_completo.py")
        print("  - Health check: python -c \"from app.core.health_check import get_health_status; print(get_health_status())\"")
        print("  - Optimizar BD: python -c \"from app.database.optimization import optimize_database; optimize_database()\"")

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python deploy.py [local|production-prep]")
        print()
        print("Opciones:")
        print("  local         - Despliegue local completo")
        print("  production-prep - Preparar para despliegue en producción")
        sys.exit(1)
    
    manager = DeploymentManager()
    
    if sys.argv[1] == "local":
        success = manager.deploy_local()
    elif sys.argv[1] == "production-prep":
        success = manager.deploy_production_prep()
    else:
        print(f"Opción no válida: {sys.argv[1]}")
        sys.exit(1)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()