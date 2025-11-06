"""
Script para limpiar los maestros de ejemplo de la base de datos
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import SessionLocal
from app.database.crud import MaestroAutorizadoCRUD

def clean_example_maestros():
    """Elimina todos los maestros de ejemplo de la base de datos"""
    
    print("🧹 Limpiando maestros de ejemplo...")
    
    db = SessionLocal()
    crud = MaestroAutorizadoCRUD(db)
    
    try:
        # Obtener todos los maestros
        maestros = crud.get_all_maestros()
        
        if not maestros:
            print("ℹ️ No hay maestros en la base de datos.")
            return
        
        print(f"📋 Encontrados {len(maestros)} maestros:")
        for maestro in maestros:
            print(f"  - {maestro.nombre_completo} ({maestro.correo_institucional})")
        
        # Confirmar eliminación
        print("\n⚠️ ¿Está seguro de que desea eliminar TODOS los maestros?")
        print("Esto eliminará todos los maestros de la base de datos.")
        
        # Eliminar todos los maestros
        deleted_count = 0
        for maestro in maestros:
            if crud.delete_maestro(maestro.id):
                print(f"  ✅ Eliminado: {maestro.nombre_completo}")
                deleted_count += 1
            else:
                print(f"  ❌ Error eliminando: {maestro.nombre_completo}")
        
        print(f"\n🎉 Se eliminaron {deleted_count} maestros exitosamente.")
        print("📝 Ahora puede agregar los maestros reales desde la página 'Maestros Autorizados'.")
        
    except Exception as e:
        print(f"❌ Error limpiando maestros: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    clean_example_maestros()