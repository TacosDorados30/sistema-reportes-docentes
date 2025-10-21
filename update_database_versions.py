#!/usr/bin/env python3
"""
Script para actualizar la base de datos con soporte para versiones
Agrega los campos necesarios para el sistema de correcciones
"""

import os
import sys
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import SessionLocal, engine
from sqlalchemy import text, inspect


def update_database_schema():
    """Actualiza el esquema de la base de datos para soportar versiones"""
    
    print("🔄 Actualizando esquema de base de datos para sistema de versiones...")
    
    db = SessionLocal()
    try:
        # Verificar si las columnas ya existen
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('formularios_envio')]
        
        new_columns = [
            'formulario_original_id',
            'version', 
            'token_correccion',
            'es_version_activa'
        ]
        
        columns_to_add = [col for col in new_columns if col not in columns]
        
        if not columns_to_add:
            print("✅ Las columnas ya existen. No se requiere actualización.")
            return True
        
        print(f"📝 Agregando columnas: {', '.join(columns_to_add)}")
        
        # Agregar columnas una por una
        if 'formulario_original_id' in columns_to_add:
            db.execute(text("""
                ALTER TABLE formularios_envio 
                ADD COLUMN formulario_original_id INTEGER
            """))
            print("   ✅ formulario_original_id agregada")
        
        if 'version' in columns_to_add:
            db.execute(text("""
                ALTER TABLE formularios_envio 
                ADD COLUMN version INTEGER DEFAULT 1
            """))
            print("   ✅ version agregada")
        
        if 'token_correccion' in columns_to_add:
            db.execute(text("""
                ALTER TABLE formularios_envio 
                ADD COLUMN token_correccion TEXT
            """))
            print("   ✅ token_correccion agregada")
        
        if 'es_version_activa' in columns_to_add:
            db.execute(text("""
                ALTER TABLE formularios_envio 
                ADD COLUMN es_version_activa BOOLEAN DEFAULT 1
            """))
            print("   ✅ es_version_activa agregada")
        
        # Actualizar registros existentes
        print("📊 Actualizando registros existentes...")
        
        # Establecer version = 1 para todos los registros existentes que no la tengan
        db.execute(text("""
            UPDATE formularios_envio 
            SET version = 1 
            WHERE version IS NULL
        """))
        
        # Establecer es_version_activa = true para todos los registros existentes
        db.execute(text("""
            UPDATE formularios_envio 
            SET es_version_activa = 1 
            WHERE es_version_activa IS NULL
        """))
        
        db.commit()
        
        print("✅ Esquema actualizado exitosamente!")
        print(f"🕒 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error actualizando esquema: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()


def verify_update():
    """Verifica que la actualización se haya aplicado correctamente"""
    
    print("\n🔍 Verificando actualización...")
    
    db = SessionLocal()
    try:
        # Verificar que las columnas existen
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('formularios_envio')]
        
        required_columns = [
            'formulario_original_id',
            'version', 
            'token_correccion',
            'es_version_activa'
        ]
        
        missing_columns = [col for col in required_columns if col not in columns]
        
        if missing_columns:
            print(f"❌ Faltan columnas: {', '.join(missing_columns)}")
            return False
        
        # Verificar datos
        result = db.execute(text("""
            SELECT COUNT(*) as total,
                   COUNT(CASE WHEN version IS NOT NULL THEN 1 END) as with_version,
                   COUNT(CASE WHEN es_version_activa IS NOT NULL THEN 1 END) as with_active
            FROM formularios_envio
        """))
        
        stats = result.fetchone()
        
        print(f"📊 Estadísticas:")
        print(f"   - Total formularios: {stats.total}")
        print(f"   - Con versión: {stats.with_version}")
        print(f"   - Con estado activo: {stats.with_active}")
        
        if stats.total > 0 and stats.with_version == stats.total and stats.with_active == stats.total:
            print("✅ Verificación exitosa!")
            return True
        else:
            print("⚠️  Algunos registros no tienen los valores correctos")
            return False
        
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False
        
    finally:
        db.close()


def main():
    """Función principal"""
    print("🗄️  ACTUALIZACIÓN DE BASE DE DATOS - SISTEMA DE VERSIONES")
    print("=" * 60)
    
    try:
        # Actualizar esquema
        if update_database_schema():
            # Verificar actualización
            if verify_update():
                print("\n🎉 ¡Actualización completada exitosamente!")
                print("💡 El sistema de correcciones ya está disponible.")
            else:
                print("\n⚠️  Actualización completada con advertencias.")
        else:
            print("\n❌ Error en la actualización.")
            
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")


if __name__ == "__main__":
    main()