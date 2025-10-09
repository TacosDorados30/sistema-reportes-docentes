#!/usr/bin/env python3
"""
Script para migrar la base de datos y agregar campos de período académico
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def migrate_database():
    """Add academic period columns to existing database"""
    
    db_path = "data/reportes_docentes.db"
    
    if not os.path.exists(db_path):
        print("❌ Base de datos no encontrada. Se creará automáticamente al iniciar el sistema.")
        return True
    
    print("🔄 Migrando base de datos para agregar campos de período académico...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(formularios_envio)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'año_academico' not in columns:
            print("➕ Agregando columna año_academico...")
            cursor.execute("ALTER TABLE formularios_envio ADD COLUMN año_academico INTEGER DEFAULT 2025")
            
        if 'trimestre' not in columns:
            print("➕ Agregando columna trimestre...")
            cursor.execute("ALTER TABLE formularios_envio ADD COLUMN trimestre TEXT DEFAULT 'Trimestre 1'")
        
        # Update existing records with default values
        cursor.execute("""
            UPDATE formularios_envio 
            SET año_academico = 2025, trimestre = 'Trimestre 1' 
            WHERE año_academico IS NULL OR trimestre IS NULL
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Migración completada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        return False

def main():
    """Run migration"""
    print("🗄️ MIGRACIÓN DE BASE DE DATOS")
    print("=" * 40)
    
    if migrate_database():
        print("\n🎉 ¡Migración exitosa!")
        print("📋 Campos agregados:")
        print("   - año_academico (INTEGER)")
        print("   - trimestre (TEXT)")
        print("\n💡 Los formularios existentes tienen valores por defecto:")
        print("   - Año: 2025")
        print("   - Trimestre: Trimestre 1")
        return True
    else:
        print("\n❌ La migración falló")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)