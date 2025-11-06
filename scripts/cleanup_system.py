#!/usr/bin/env python3
"""
Script para limpiar archivos temporales y optimizar el sistema
"""

import os
import shutil
import sys
from pathlib import Path

def cleanup_pycache():
    """Eliminar archivos __pycache__"""
    print("🧹 Limpiando archivos __pycache__...")
    
    root_dir = Path(__file__).parent.parent
    deleted_count = 0
    
    for pycache_dir in root_dir.rglob("__pycache__"):
        try:
            shutil.rmtree(pycache_dir)
            deleted_count += 1
            print(f"   ✅ Eliminado: {pycache_dir}")
        except Exception as e:
            print(f"   ❌ Error eliminando {pycache_dir}: {e}")
    
    print(f"📊 {deleted_count} directorios __pycache__ eliminados")

def cleanup_logs():
    """Limpiar logs antiguos (mantener solo los últimos 5)"""
    print("📝 Limpiando logs antiguos...")
    
    logs_dir = Path(__file__).parent.parent / "logs"
    if not logs_dir.exists():
        print("   ℹ️ No hay directorio de logs")
        return
    
    log_files = sorted(logs_dir.glob("*.log"), key=os.path.getmtime, reverse=True)
    
    if len(log_files) <= 5:
        print(f"   ℹ️ Solo {len(log_files)} archivos de log, no se elimina nada")
        return
    
    for log_file in log_files[5:]:  # Mantener solo los 5 más recientes
        try:
            log_file.unlink()
            print(f"   ✅ Eliminado: {log_file.name}")
        except Exception as e:
            print(f"   ❌ Error eliminando {log_file}: {e}")

def cleanup_temp_files():
    """Eliminar archivos temporales"""
    print("🗂️ Limpiando archivos temporales...")
    
    root_dir = Path(__file__).parent.parent
    temp_patterns = ["*.tmp", "*.temp", "*.bak", "*.swp", "*~"]
    deleted_count = 0
    
    for pattern in temp_patterns:
        for temp_file in root_dir.rglob(pattern):
            try:
                temp_file.unlink()
                deleted_count += 1
                print(f"   ✅ Eliminado: {temp_file}")
            except Exception as e:
                print(f"   ❌ Error eliminando {temp_file}: {e}")
    
    print(f"📊 {deleted_count} archivos temporales eliminados")

def cleanup_empty_dirs():
    """Eliminar directorios vacíos"""
    print("📁 Limpiando directorios vacíos...")
    
    root_dir = Path(__file__).parent.parent
    deleted_count = 0
    
    # Directorios que no deben eliminarse aunque estén vacíos
    protected_dirs = {"logs", "data", "reports", "uploads", "backups", ".git", ".kiro"}
    
    for dir_path in root_dir.rglob("*"):
        if dir_path.is_dir() and dir_path.name not in protected_dirs:
            try:
                if not any(dir_path.iterdir()):  # Directorio vacío
                    dir_path.rmdir()
                    deleted_count += 1
                    print(f"   ✅ Eliminado: {dir_path}")
            except Exception:
                pass  # Ignorar errores silenciosamente
    
    print(f"📊 {deleted_count} directorios vacíos eliminados")

def optimize_database():
    """Optimizar base de datos SQLite"""
    print("🗄️ Optimizando base de datos...")
    
    db_path = Path(__file__).parent.parent / "reportes_docentes.db"
    
    if not db_path.exists():
        print("   ℹ️ No se encontró base de datos")
        return
    
    try:
        import sqlite3
        
        with sqlite3.connect(str(db_path)) as conn:
            # VACUUM para optimizar y compactar
            conn.execute("VACUUM")
            
            # ANALYZE para actualizar estadísticas
            conn.execute("ANALYZE")
            
            print("   ✅ Base de datos optimizada")
            
    except Exception as e:
        print(f"   ❌ Error optimizando base de datos: {e}")

def show_disk_usage():
    """Mostrar uso de disco del proyecto"""
    print("💾 Uso de disco del proyecto:")
    
    root_dir = Path(__file__).parent.parent
    
    def get_dir_size(path):
        total = 0
        try:
            for entry in path.rglob("*"):
                if entry.is_file():
                    total += entry.stat().st_size
        except Exception:
            pass
        return total
    
    def format_size(bytes_size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024
        return f"{bytes_size:.1f} TB"
    
    # Calcular tamaños por directorio
    directories = ["app", "dashboard", "data", "logs", "reports", "uploads", "venv"]
    
    for dir_name in directories:
        dir_path = root_dir / dir_name
        if dir_path.exists():
            size = get_dir_size(dir_path)
            print(f"   📁 {dir_name}: {format_size(size)}")
    
    # Tamaño total
    total_size = get_dir_size(root_dir)
    print(f"   📊 Total: {format_size(total_size)}")

def main():
    """Función principal de limpieza"""
    print("🧹 LIMPIEZA Y OPTIMIZACIÓN DEL SISTEMA")
    print("=" * 50)
    
    try:
        cleanup_pycache()
        print()
        
        cleanup_logs()
        print()
        
        cleanup_temp_files()
        print()
        
        cleanup_empty_dirs()
        print()
        
        optimize_database()
        print()
        
        show_disk_usage()
        print()
        
        print("✅ Limpieza completada exitosamente!")
        print("🚀 El sistema debería funcionar más rápido ahora")
        
    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)