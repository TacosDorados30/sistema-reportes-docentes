#!/usr/bin/env python3
"""
Script simple para borrar todos los maestros autorizados
"""

from app.models.database import MaestroAutorizadoDB
from app.database.connection import SessionLocal
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def borrar_maestros():
    """Borra todos los maestros autorizados"""

    print("🗑️  Borrando maestros autorizados...")

    db = SessionLocal()
    try:
        # Contar antes
        total = db.query(MaestroAutorizadoDB).count()
        print(f"📊 Maestros encontrados: {total}")

        if total == 0:
            print("✅ Ya está limpio")
            return

        # Borrar todos los maestros autorizados
        db.query(MaestroAutorizadoDB).delete()
        db.commit()

        print(f"✅ {total} maestros eliminados")
        print("🎯 Lista de maestros limpia")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    borrar_maestros()
