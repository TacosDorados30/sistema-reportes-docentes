#!/usr/bin/env python3
"""
Script para verificar que la base de datos esté completamente limpia
"""

import sqlite3
import os

def verificar_limpieza():
    """Verifica que todas las tablas estén vacías"""
    
    db_path = "reportes_docentes.db"
    
    if not os.path.exists(db_path):
        print(f"❌ No se encontró la base de datos en: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Verificando estado de la base de datos...")
        
        # Obtener lista de todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = cursor.fetchall()
        
        total_registros = 0
        tablas_con_datos = []
        
        print(f"\n📋 Estado de las tablas:")
        
        for tabla in tablas:
            tabla_nombre = tabla[0]
            cursor.execute(f"SELECT COUNT(*) FROM {tabla_nombre};")
            count = cursor.fetchone()[0]
            total_registros += count
            
            if count > 0:
                tablas_con_datos.append((tabla_nombre, count))
                print(f"   ❌ {tabla_nombre}: {count} registros")
            else:
                print(f"   ✅ {tabla_nombre}: vacía")
        
        print(f"\n📊 Resumen:")
        print(f"   Total de tablas: {len(tablas)}")
        print(f"   Total de registros: {total_registros}")
        
        if total_registros == 0:
            print(f"\n🎉 ¡Perfecto! La base de datos está completamente limpia.")
            print(f"   ✅ Todas las tablas están vacías")
            print(f"   ✅ Lista para pruebas desde cero")
            return True
        else:
            print(f"\n⚠️ Aún hay {total_registros} registros en {len(tablas_con_datos)} tablas:")
            for tabla_nombre, count in tablas_con_datos:
                print(f"   - {tabla_nombre}: {count}")
            return False
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error durante la verificación: {str(e)}")
        return False

if __name__ == "__main__":
    verificar_limpieza()