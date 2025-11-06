"""
Script para actualizar la base de datos con la tabla de notificaciones de email
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import engine, SessionLocal
from app.models.database import Base, NotificacionEmailDB

def update_database():
    """Actualiza la base de datos con la nueva tabla de notificaciones"""
    
    print("🔄 Actualizando base de datos...")
    
    try:
        # Crear todas las tablas (incluyendo la nueva)
        Base.metadata.create_all(bind=engine)
        print("✅ Tabla de notificaciones de email creada exitosamente.")
        
        # Verificar que la tabla se creó correctamente
        db = SessionLocal()
        try:
            # Intentar hacer una consulta simple para verificar
            count = db.query(NotificacionEmailDB).count()
            print(f"ℹ️ La tabla está lista. Actualmente hay {count} notificaciones registradas.")
            print("📧 Funcionalidades disponibles:")
            print("   - Seguimiento de maestros sin formularios")
            print("   - Envío automático de recordatorios")
            print("   - Historial de notificaciones enviadas")
            print("   - Recordatorios masivos por tipo")
                
        finally:
            db.close()
            
        print("🎉 Actualización de base de datos completada.")
        
    except Exception as e:
        print(f"❌ Error actualizando base de datos: {e}")

if __name__ == "__main__":
    update_database()