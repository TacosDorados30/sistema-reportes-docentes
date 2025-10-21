#!/usr/bin/env python3
"""
Script para crear la tabla de historial de formularios
"""

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import engine
from app.models.form_history import Base


def create_history_table():
    """Crea la tabla de historial de formularios"""
    
    print("🗄️  Creando tabla de historial de formularios...")
    
    try:
        # Crear todas las tablas definidas en Base
        Base.metadata.create_all(bind=engine)
        
        print("✅ Tabla de historial creada exitosamente!")
        print("📋 Tabla: formularios_historial")
        print("🎯 Funcionalidad: Mantener historial de versiones sin crear nuevos IDs")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando tabla: {e}")
        return False


if __name__ == "__main__":
    create_history_table()