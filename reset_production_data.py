#!/usr/bin/env python3
"""
Script para borrar datos de la base de datos de PRODUCCIÓN
⚠️ CUIDADO: Este script borra datos de la base de datos en Render
"""

import os
import sys

# Configurar la URL de producción temporalmente
PRODUCTION_DB_URL = "postgresql://reportes_docentes_user:h2hiCIL5rlopnbxx9nTLbTdhhoHJwZfI@dpg-d4aeqqkhg0os7380t3v0-a.oregon-postgres.render.com/reportes_docentes"

# Guardar la URL original
original_db_url = os.environ.get('DATABASE_URL')

# Cambiar temporalmente a producción
os.environ['DATABASE_URL'] = PRODUCTION_DB_URL

# Ahora importar después de cambiar la variable
from app.models.database import (
    FormularioEnvioDB, CursoCapacitacionDB, PublicacionDB,
    EventoAcademicoDB, DisenoCurricularDB, ExperienciaMovilidadDB,
    ReconocimientoDB, CertificacionDB, OtraActividadAcademicaDB,
    MaestroAutorizadoDB, NotificacionEmailDB, AuditLogDB
)
from app.models.audit import AuditLog
from app.database.connection import SessionLocal


def confirmar_accion():
    """Pedir confirmación antes de borrar"""
    print("=" * 60)
    print("⚠️  ADVERTENCIA: BORRADO DE DATOS DE PRODUCCIÓN")
    print("=" * 60)
    print("\nEstás a punto de borrar datos de la base de datos en Render:")
    print(f"🗄️  Base de datos: PostgreSQL en Render")
    print("\n¿Qué se borrará?")
    print("  1. Todos los formularios enviados")
    print("  2. Todas las actividades académicas")
    print("  3. Todos los maestros autorizados")
    print("  4. Todas las notificaciones de email")
    print("  5. Todos los logs de auditoría")
    print("\n⚠️  ESTA ACCIÓN NO SE PUEDE DESHACER")
    print("=" * 60)
    
    respuesta = input("\n¿Estás seguro? Escribe 'SI BORRAR TODO' para confirmar: ")
    return respuesta == "SI BORRAR TODO"


def borrar_audit_logs(db):
    """Borra todos los logs de auditoría"""
    print("\n🗑️  Borrando logs de auditoría...")
    
    # Borrar de ambas tablas de auditoría
    total1 = db.query(AuditLog).count()
    total2 = db.query(AuditLogDB).count()
    total = total1 + total2
    
    print(f"📊 Encontrados: {total} logs de auditoría (audit_logs: {total1}, audit_log: {total2})")
    
    if total == 0:
        print("✅ No hay logs para borrar")
        return
    
    # Borrar ambas tablas
    db.query(AuditLog).delete()
    db.query(AuditLogDB).delete()
    db.commit()
    print(f"✅ {total} logs eliminados")


def borrar_formularios(db):
    """Borra todos los formularios y actividades relacionadas"""
    print("\n🗑️  Borrando formularios y actividades...")
    
    # Contar antes
    total_formularios = db.query(FormularioEnvioDB).count()
    total_cursos = db.query(CursoCapacitacionDB).count()
    total_publicaciones = db.query(PublicacionDB).count()
    total_eventos = db.query(EventoAcademicoDB).count()
    
    print(f"📊 Encontrados:")
    print(f"   - {total_formularios} formularios")
    print(f"   - {total_cursos} cursos")
    print(f"   - {total_publicaciones} publicaciones")
    print(f"   - {total_eventos} eventos")
    
    if total_formularios == 0:
        print("✅ No hay formularios para borrar")
        return
    
    # Borrar en orden (respetando foreign keys)
    db.query(OtraActividadAcademicaDB).delete()
    db.query(CertificacionDB).delete()
    db.query(ReconocimientoDB).delete()
    db.query(ExperienciaMovilidadDB).delete()
    db.query(DisenoCurricularDB).delete()
    db.query(EventoAcademicoDB).delete()
    db.query(PublicacionDB).delete()
    db.query(CursoCapacitacionDB).delete()
    db.query(FormularioEnvioDB).delete()
    
    db.commit()
    print(f"✅ {total_formularios} formularios eliminados")


def borrar_maestros(db):
    """Borra todos los maestros autorizados"""
    print("\n🗑️  Borrando maestros autorizados...")
    
    total = db.query(MaestroAutorizadoDB).count()
    print(f"📊 Encontrados: {total} maestros")
    
    if total == 0:
        print("✅ No hay maestros para borrar")
        return
    
    db.query(MaestroAutorizadoDB).delete()
    db.commit()
    print(f"✅ {total} maestros eliminados")


def borrar_notificaciones(db):
    """Borra todas las notificaciones de email"""
    print("\n🗑️  Borrando notificaciones de email...")
    
    total = db.query(NotificacionEmailDB).count()
    print(f"📊 Encontrados: {total} notificaciones")
    
    if total == 0:
        print("✅ No hay notificaciones para borrar")
        return
    
    db.query(NotificacionEmailDB).delete()
    db.commit()
    print(f"✅ {total} notificaciones eliminadas")


def main():
    """Función principal"""
    
    # Pedir confirmación
    if not confirmar_accion():
        print("\n❌ Operación cancelada")
        return
    
    print("\n🚀 Iniciando borrado de datos...")
    
    db = SessionLocal()
    try:
        # Borrar notificaciones primero (tienen foreign key a maestros)
        borrar_notificaciones(db)
        
        # Borrar logs de auditoría (tienen foreign key a formularios)
        borrar_audit_logs(db)
        
        # Borrar formularios y actividades
        borrar_formularios(db)
        
        # Borrar maestros
        borrar_maestros(db)
        
        print("\n" + "=" * 60)
        print("✅ PROCESO COMPLETADO")
        print("=" * 60)
        print("🎯 Base de datos de producción limpia")
        print("💾 Los datos han sido eliminados permanentemente")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        print("⚠️  Se hizo rollback, algunos datos pueden no haberse borrado")
        
    finally:
        db.close()
        # Restaurar la URL original
        if original_db_url:
            os.environ['DATABASE_URL'] = original_db_url


if __name__ == "__main__":
    main()
