#!/usr/bin/env python3
"""
Script para agregar datos de ejemplo para probar el detalle por maestro
"""

from app.models.database import (
    FormularioEnvioDB, CursoCapacitacionDB, PublicacionDB,
    EventoAcademicoDB, CertificacionDB, EstadoFormularioEnum,
    EstatusPublicacionEnum, TipoParticipacionEnum
)
from app.database.connection import SessionLocal
import sys
import os
from datetime import datetime, date

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def create_sample_data():
    """Crear datos de ejemplo para probar el detalle por maestro"""

    print("📝 Creando datos de ejemplo...")

    db = SessionLocal()
    try:
        # Maestro 1: Dr. Juan Pérez
        form1 = FormularioEnvioDB(
            nombre_completo="Dr. Juan Pérez García",
            correo_institucional="juan.perez@universidad.edu",
            año_academico=2024,
            trimestre="Trimestre 3",
            estado=EstadoFormularioEnum.APROBADO,
            fecha_envio=datetime(2024, 9, 15, 10, 30),
            fecha_revision=datetime(2024, 9, 20, 14, 15),
            revisado_por="admin",
            version=1,
            es_version_activa=True
        )

        db.add(form1)
        db.flush()  # Para obtener el ID

        # Cursos para Juan Pérez
        curso1 = CursoCapacitacionDB(
            formulario_id=form1.id,
            nombre_curso="Metodologías Ágiles en Educación",
            fecha=date(2024, 8, 15),
            horas=40
        )

        curso2 = CursoCapacitacionDB(
            formulario_id=form1.id,
            nombre_curso="Tecnologías Educativas Avanzadas",
            fecha=date(2024, 7, 20),
            horas=30
        )

        # Publicaciones para Juan Pérez
        pub1 = PublicacionDB(
            formulario_id=form1.id,
            autores="Juan Pérez García, María López",
            titulo="Innovación en Metodologías de Enseñanza",
            evento_revista="Revista de Educación Superior",
            estatus=EstatusPublicacionEnum.PUBLICADO
        )

        # Eventos para Juan Pérez
        evento1 = EventoAcademicoDB(
            formulario_id=form1.id,
            nombre_evento="Congreso Internacional de Educación",
            fecha=date(2024, 8, 10),
            tipo_participacion=TipoParticipacionEnum.PONENTE
        )

        # Certificaciones para Juan Pérez
        cert1 = CertificacionDB(
            formulario_id=form1.id,
            nombre="Certificación en Docencia Universitaria",
            fecha_obtencion=date(2024, 6, 15)
        )

        db.add_all([curso1, curso2, pub1, evento1, cert1])

        # Maestro 2: Dra. María González
        form2 = FormularioEnvioDB(
            nombre_completo="Dra. María González López",
            correo_institucional="maria.gonzalez@universidad.edu",
            año_academico=2024,
            trimestre="Trimestre 3",
            estado=EstadoFormularioEnum.PENDIENTE,
            fecha_envio=datetime(2024, 10, 1, 9, 45),
            version=1,
            es_version_activa=True
        )

        db.add(form2)
        db.flush()

        # Cursos para María González
        curso3 = CursoCapacitacionDB(
            formulario_id=form2.id,
            nombre_curso="Investigación Cualitativa en Educación",
            fecha=date(2024, 9, 5),
            horas=50
        )

        # Publicaciones para María González
        pub2 = PublicacionDB(
            formulario_id=form2.id,
            autores="María González López",
            titulo="Estrategias de Evaluación Formativa",
            evento_revista="Congreso Nacional de Pedagogía",
            estatus=EstatusPublicacionEnum.EN_REVISION
        )

        pub3 = PublicacionDB(
            formulario_id=form2.id,
            autores="María González López, Carlos Ruiz",
            titulo="Impacto de la Tecnología en el Aprendizaje",
            evento_revista="Revista Educativa Digital",
            estatus=EstatusPublicacionEnum.ACEPTADO
        )

        # Certificaciones para María González
        cert2 = CertificacionDB(
            formulario_id=form2.id,
            nombre="Especialización en Evaluación Educativa",
            fecha_obtencion=date(2024, 5, 20)
        )

        cert3 = CertificacionDB(
            formulario_id=form2.id,
            nombre="Certificación Internacional en E-Learning",
            fecha_obtencion=date(2024, 7, 10)
        )

        db.add_all([curso3, pub2, pub3, cert2, cert3])

        # Maestro 3: Mtro. Carlos Rodríguez
        form3 = FormularioEnvioDB(
            nombre_completo="Mtro. Carlos Rodríguez Hernández",
            correo_institucional="carlos.rodriguez@universidad.edu",
            año_academico=2024,
            trimestre="Trimestre 2",
            estado=EstadoFormularioEnum.APROBADO,
            fecha_envio=datetime(2024, 6, 20, 16, 20),
            fecha_revision=datetime(2024, 6, 25, 11, 30),
            revisado_por="admin",
            version=1,
            es_version_activa=True
        )

        db.add(form3)
        db.flush()

        # Eventos para Carlos Rodríguez
        evento2 = EventoAcademicoDB(
            formulario_id=form3.id,
            nombre_evento="Seminario de Innovación Educativa",
            fecha=date(2024, 5, 15),
            tipo_participacion=TipoParticipacionEnum.ORGANIZADOR
        )

        evento3 = EventoAcademicoDB(
            formulario_id=form3.id,
            nombre_evento="Workshop de Metodologías Activas",
            fecha=date(2024, 6, 8),
            tipo_participacion=TipoParticipacionEnum.PONENTE
        )

        # Cursos para Carlos Rodríguez
        curso4 = CursoCapacitacionDB(
            formulario_id=form3.id,
            nombre_curso="Liderazgo Académico",
            fecha=date(2024, 4, 12),
            horas=25
        )

        db.add_all([evento2, evento3, curso4])

        db.commit()

        print("✅ Datos de ejemplo creados exitosamente:")
        print("   👨‍🏫 Dr. Juan Pérez García - APROBADO (2 cursos, 1 publicación, 1 evento, 1 certificación)")
        print("   👩‍🏫 Dra. María González López - PENDIENTE (1 curso, 2 publicaciones, 2 certificaciones)")
        print("   👨‍🏫 Mtro. Carlos Rodríguez Hernández - APROBADO (1 curso, 2 eventos)")
        print()
        print("🎯 Ahora puede probar la funcionalidad 'Detalle por Maestro' en Generación de Reportes")

    except Exception as e:
        print(f"❌ Error creando datos: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_sample_data()
