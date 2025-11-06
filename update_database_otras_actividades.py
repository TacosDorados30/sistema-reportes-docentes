"""
Script para actualizar la base de datos con la tabla de otras actividades académicas
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import engine, SessionLocal
from app.models.database import Base, OtraActividadAcademicaDB

def update_database():
    """Actualiza la base de datos con la nueva tabla de otras actividades académicas"""
    
    print("🔄 Actualizando base de datos...")
    
    try:
        # Crear todas las tablas (incluyendo la nueva)
        Base.metadata.create_all(bind=engine)
        print("✅ Tabla de otras actividades académicas creada exitosamente.")
        
        # Verificar que la tabla se creó correctamente
        db = SessionLocal()
        try:
            # Intentar hacer una consulta simple para verificar
            count = db.query(OtraActividadAcademicaDB).count()
            print(f"ℹ️ La tabla está lista. Actualmente hay {count} otras actividades registradas.")
            print("📝 Los maestros ahora pueden agregar actividades como:")
            print("   - Asesoría y titulación")
            print("   - Número de solicitudes atendidas")
            print("   - Certificaciones con temáticas específicas")
            print("   - Cualquier otra actividad académica")
                
        finally:
            db.close()
            
        print("🎉 Actualización de base de datos completada.")
        
    except Exception as e:
        print(f"❌ Error actualizando base de datos: {e}")

if __name__ == "__main__":
    update_database()