"""
Script para actualizar la base de datos con la tabla de maestros autorizados
"""

from app.database.crud import MaestroAutorizadoCRUD
from app.models.database import Base, MaestroAutorizadoDB
from app.database.connection import engine, SessionLocal
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def update_database():
    """Actualiza la base de datos con la nueva tabla de maestros autorizados"""

    print("🔄 Actualizando base de datos...")

    try:
        # Crear todas las tablas (incluyendo la nueva)
        Base.metadata.create_all(bind=engine)
        print("✅ Tabla de maestros autorizados creada exitosamente.")

        # Verificar el estado de la tabla
        db = SessionLocal()
        crud = MaestroAutorizadoCRUD(db)

        try:
            existing_maestros = crud.get_all_maestros()
            print(
                f"ℹ️ La tabla está lista. Actualmente hay {len(existing_maestros)} maestros registrados.")
            print(
                "📝 Use la página 'Maestros Autorizados' en el dashboard para agregar maestros.")

        finally:
            db.close()

        print("🎉 Actualización de base de datos completada.")

    except Exception as e:
        print(f"❌ Error actualizando base de datos: {e}")


if __name__ == "__main__":
    update_database()
