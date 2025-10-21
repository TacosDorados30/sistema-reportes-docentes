#!/usr/bin/env python3
"""
Script simple para borrar todos los formularios del dashboard
"""

from app.models.database import (
    FormularioEnvioDB, CursoCapacitacionDB, PublicacionDB,
    EventoAcademicoDB, DisenoCurricularDB, ExperienciaMovilidadDB,
    ReconocimientoDB, CertificacionDB
)
from app.database.connection import SessionLocal
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def borrar_datos():
    """Borra todos los formularios para limpiar el dashboard"""

    print("🗑️  Borrando datos del dashboard...")

    db = SessionLocal()
    try:
        # Contar antes
        total = db.query(FormularioEnvioDB).count()
        print(f"📊 Formularios encontrados: {total}")

        if total == 0:
            print("✅ Ya está limpio")
            return

        # Borrar todo
        db.query(CertificacionDB).delete()
        db.query(ReconocimientoDB).delete()
        db.query(ExperienciaMovilidadDB).delete()
        db.query(DisenoCurricularDB).delete()
        db.query(EventoAcademicoDB).delete()
        db.query(PublicacionDB).delete()
        db.query(CursoCapacitacionDB).delete()
        db.query(FormularioEnvioDB).delete()

        db.commit()

        print(f"✅ {total} formularios eliminados")
        print("🎯 Dashboard limpio para pruebas")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    borrar_datos()
