#!/usr/bin/env python3
"""
Script para agregar maestros de ejemplo al sistema
"""

from app.models.database import MaestroAutorizadoDB
from app.database.connection import SessionLocal
import os
import sys
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def agregar_maestros_ejemplo():
    """Agrega maestros de ejemplo al sistema"""
    
    maestros_ejemplo = [
        {
            "nombre_completo": "Dr. Juan Carlos Pérez García",
            "correo_institucional": "juan.perez@universidad.edu.mx"
        },
        {
            "nombre_completo": "Dra. María Elena González López",
            "correo_institucional": "maria.gonzalez@universidad.edu.mx"
        },
        {
            "nombre_completo": "Prof. Carlos Alberto Rodríguez",
            "correo_institucional": "carlos.rodriguez@universidad.edu.mx"
        },
        {
            "nombre_completo": "Dra. Ana Sofía Martínez Hernández",
            "correo_institucional": "ana.martinez@universidad.edu.mx"
        },
        {
            "nombre_completo": "Prof. Luis Fernando Hernández",
            "correo_institucional": "luis.hernandez@universidad.edu.mx"
        }
    ]
    
    print("👥 Agregando maestros de ejemplo...")
    
    db = SessionLocal()
    try:
        agregados = 0
        
        for maestro_data in maestros_ejemplo:
            # Verificar si ya existe
            existe = db.query(MaestroAutorizadoDB).filter(
                MaestroAutorizadoDB.correo_institucional == maestro_data["correo_institucional"]
            ).first()
            
            if existe:
                print(f"⚠️  Ya existe: {maestro_data['nombre_completo']}")
                continue
            
            # Crear nuevo maestro
            nuevo_maestro = MaestroAutorizadoDB(
                nombre_completo=maestro_data["nombre_completo"],
                correo_institucional=maestro_data["correo_institucional"],
                activo=True,
                fecha_creacion=datetime.utcnow(),
                fecha_actualizacion=datetime.utcnow()
            )
            
            db.add(nuevo_maestro)
            agregados += 1
            print(f"✅ Agregado: {maestro_data['nombre_completo']}")
        
        db.commit()
        
        print(f"\n🎯 {agregados} maestros de ejemplo agregados exitosamente")
        
        if agregados > 0:
            print("\n📧 Maestros agregados:")
            for maestro_data in maestros_ejemplo:
                print(f"   • {maestro_data['nombre_completo']} - {maestro_data['correo_institucional']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    agregar_maestros_ejemplo()