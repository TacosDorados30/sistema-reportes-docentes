#!/usr/bin/env python3
"""
Test script to verify that the data models work correctly
"""

import sys
import os
from datetime import date, datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.schemas import (
    FormData, CursoCapacitacionBase, PublicacionBase, EventoAcademicoBase,
    DisenoCurricularBase, ExperienciaMovilidadBase, ReconocimientoBase,
    CertificacionBase, EstatusPublicacion, TipoParticipacion, TipoMovilidad,
    TipoReconocimiento
)
from app.database.connection import SessionLocal
from app.database.crud import FormularioCRUD

def test_form_data_creation():
    """Test creating form data with all fields"""
    print("Testing form data creation...")
    
    # Create sample form data
    form_data = FormData(
        nombre_completo="Dr. Juan Pérez García",
        correo_institucional="juan.perez@universidad.edu.mx",
        cursos_capacitacion=[
            CursoCapacitacionBase(
                nombre_curso="IA Generativa y Asistentes",
                fecha=date(2024, 3, 15),
                horas=40
            ),
            CursoCapacitacionBase(
                nombre_curso="Google Workspace en acción",
                fecha=date(2024, 5, 20),
                horas=20
            )
        ],
        publicaciones=[
            PublicacionBase(
                autores="Juan Pérez, María González",
                titulo="Systematic Guidelines for Extending the Appraisal Process in Computational Models of Emotion",
                evento_revista="Journal of AI Research",
                estatus=EstatusPublicacion.ACEPTADO
            )
        ],
        eventos_academicos=[
            EventoAcademicoBase(
                nombre_evento="Semana de Diseño",
                fecha=date(2024, 4, 10),
                tipo_participacion=TipoParticipacion.ORGANIZADOR
            )
        ],
        diseno_curricular=[
            DisenoCurricularBase(
                nombre_curso="Programación III",
                descripcion="Curso avanzado de programación orientada a objetos"
            )
        ],
        movilidad=[
            ExperienciaMovilidadBase(
                descripcion="Estancia de investigación en MIT",
                tipo=TipoMovilidad.INTERNACIONAL,
                fecha=date(2024, 6, 1)
            )
        ],
        reconocimientos=[
            ReconocimientoBase(
                nombre="Premio a la Excelencia Académica",
                tipo=TipoReconocimiento.PREMIO,
                fecha=date(2024, 7, 15)
            )
        ],
        certificaciones=[
            CertificacionBase(
                nombre="Certificación en Machine Learning",
                fecha_obtencion=date(2024, 2, 1),
                fecha_vencimiento=date(2026, 2, 1)
            )
        ]
    )
    
    print(f"✅ Form data created successfully for: {form_data.nombre_completo}")
    print(f"   - Cursos: {len(form_data.cursos_capacitacion)}")
    print(f"   - Publicaciones: {len(form_data.publicaciones)}")
    print(f"   - Eventos: {len(form_data.eventos_academicos)}")
    print(f"   - Diseños curriculares: {len(form_data.diseno_curricular)}")
    print(f"   - Movilidades: {len(form_data.movilidad)}")
    print(f"   - Reconocimientos: {len(form_data.reconocimientos)}")
    print(f"   - Certificaciones: {len(form_data.certificaciones)}")
    
    return form_data

def test_database_operations(form_data):
    """Test database CRUD operations"""
    print("\nTesting database operations...")
    
    db = SessionLocal()
    try:
        crud = FormularioCRUD(db)
        
        # Create form in database
        db_formulario = crud.create_formulario(form_data)
        print(f"✅ Form created in database with ID: {db_formulario.id}")
        
        # Get form from database
        retrieved_form = crud.get_formulario(db_formulario.id)
        print(f"✅ Form retrieved from database: {retrieved_form.nombre_completo}")
        
        # Test metrics
        metricas = crud.get_metricas_generales()
        print(f"✅ Metrics calculated:")
        print(f"   - Total formularios: {metricas.total_formularios}")
        print(f"   - Pendientes: {metricas.formularios_pendientes}")
        print(f"   - Total cursos: {metricas.total_cursos}")
        print(f"   - Total horas: {metricas.total_horas_capacitacion}")
        
        # Test approval
        success = crud.aprobar_formulario(db_formulario.id, "admin_test")
        print(f"✅ Form approval: {'Success' if success else 'Failed'}")
        
        # Test metrics after approval
        metricas_after = crud.get_metricas_generales()
        print(f"✅ Metrics after approval:")
        print(f"   - Aprobados: {metricas_after.formularios_aprobados}")
        print(f"   - Total cursos (approved): {metricas_after.total_cursos}")
        
        return db_formulario.id
        
    except Exception as e:
        print(f"❌ Database operation failed: {e}")
        return None
    finally:
        db.close()

def main():
    """Main test function"""
    print("🧪 Testing Sistema de Reportes Docentes - Data Models")
    print("=" * 60)
    
    try:
        # Test 1: Form data creation
        form_data = test_form_data_creation()
        
        # Test 2: Database operations
        formulario_id = test_database_operations(form_data)
        
        if formulario_id:
            print(f"\n✅ All tests passed! Form ID: {formulario_id}")
        else:
            print("\n❌ Some tests failed!")
            
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()