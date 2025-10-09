#!/usr/bin/env python3
"""
Prueba específica del formulario público
"""

import sys
import os
from datetime import date

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import SessionLocal
from app.database.crud import FormularioCRUD
from app.models.schemas import (
    FormData, CursoCapacitacion, Publicacion, EventoAcademico,
    DisenoCurricular, ExperienciaMovilidad, Reconocimiento, Certificacion
)
from app.models.database import (
    EstatusPublicacionEnum, TipoParticipacionEnum, 
    TipoMovilidadEnum, TipoReconocimientoEnum
)

def test_formulario_submission():
    """Test form submission functionality"""
    
    print("🧪 Probando Formulario Público")
    print("=" * 50)
    
    # Create test form data
    form_data = FormData(
        nombre_completo="Dr. María González Pérez",
        correo_institucional="maria.gonzalez@universidad.edu",
        año_academico=2024,
        trimestre="Q4",
        cursos_capacitacion=[
            CursoCapacitacion(
                nombre_curso="Metodologías Activas de Aprendizaje",
                fecha=date(2024, 9, 15),
                horas=40
            ),
            CursoCapacitacion(
                nombre_curso="Tecnologías Educativas Digitales",
                fecha=date(2024, 10, 20),
                horas=30
            )
        ],
        publicaciones=[
            Publicacion(
                autores="González, M., Pérez, J.",
                titulo="Innovación Educativa en el Siglo XXI",
                evento_revista="Revista de Educación Superior",
                estatus=EstatusPublicacionEnum.PUBLICADO
            )
        ],
        eventos_academicos=[
            EventoAcademico(
                nombre_evento="Seminario de Innovación Educativa",
                fecha=date(2024, 11, 5),
                tipo_participacion=TipoParticipacionEnum.ORGANIZADOR
            )
        ],
        diseno_curricular=[
            DisenoCurricular(
                nombre_curso="Fundamentos de Investigación",
                descripcion="Curso diseñado para estudiantes de pregrado"
            )
        ],
        movilidad=[
            ExperienciaMovilidad(
                descripcion="Intercambio académico Universidad Internacional",
                tipo=TipoMovilidadEnum.INTERNACIONAL,
                fecha=date(2024, 8, 15)
            )
        ],
        reconocimientos=[
            Reconocimiento(
                nombre="Mejor Docente del Año",
                tipo=TipoReconocimientoEnum.PREMIO,
                fecha=date(2024, 12, 10)
            )
        ],
        certificaciones=[
            Certificacion(
                nombre="Certificación en Docencia Universitaria",
                fecha_obtencion=date(2024, 6, 1),
                fecha_vencimiento=date(2026, 6, 1),
                vigente=True
            )
        ]
    )
    
    # Test form submission
    print("1. 📝 Probando envío de formulario...")
    
    try:
        db = SessionLocal()
        crud = FormularioCRUD(db)
        
        # Submit form
        submitted_form = crud.create_formulario(form_data)
        
        print(f"   ✅ Formulario enviado exitosamente!")
        print(f"   - ID: {submitted_form.id}")
        print(f"   - Nombre: {submitted_form.nombre_completo}")
        print(f"   - Email: {submitted_form.correo_institucional}")
        print(f"   - Estado: {submitted_form.estado.value}")
        print(f"   - Fecha: {submitted_form.fecha_envio}")
        
        # Verify related data
        print("\n2. 🔍 Verificando datos relacionados...")
        
        if submitted_form.cursos_capacitacion:
            print(f"   ✅ Cursos: {len(submitted_form.cursos_capacitacion)}")
            for curso in submitted_form.cursos_capacitacion:
                print(f"      - {curso.nombre_curso} ({curso.horas}h)")
        
        if submitted_form.publicaciones:
            print(f"   ✅ Publicaciones: {len(submitted_form.publicaciones)}")
            for pub in submitted_form.publicaciones:
                print(f"      - {pub.titulo}")
        
        if submitted_form.eventos_academicos:
            print(f"   ✅ Eventos: {len(submitted_form.eventos_academicos)}")
            for evento in submitted_form.eventos_academicos:
                print(f"      - {evento.nombre_evento}")
        
        if submitted_form.diseno_curricular:
            print(f"   ✅ Diseños curriculares: {len(submitted_form.diseno_curricular)}")
        
        if submitted_form.movilidad:
            print(f"   ✅ Experiencias de movilidad: {len(submitted_form.movilidad)}")
        
        if submitted_form.reconocimientos:
            print(f"   ✅ Reconocimientos: {len(submitted_form.reconocimientos)}")
        
        if submitted_form.certificaciones:
            print(f"   ✅ Certificaciones: {len(submitted_form.certificaciones)}")
        
        db.close()
        
        print("\n✅ Prueba del formulario público EXITOSA!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error en prueba del formulario: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_form_validation():
    """Test form validation"""
    
    print("\n🔍 Probando Validación de Formulario")
    print("=" * 40)
    
    # Test with invalid email
    try:
        invalid_form = FormData(
            nombre_completo="Test User",
            correo_institucional="invalid-email",  # Invalid email
            año_academico=2024,
            trimestre="Q4",
            cursos_capacitacion=[],
            publicaciones=[],
            eventos_academicos=[],
            diseno_curricular=[],
            movilidad=[],
            reconocimientos=[],
            certificaciones=[]
        )
        print("❌ Validación falló: debería rechazar email inválido")
        return False
        
    except Exception as e:
        print("✅ Validación de email funciona correctamente")
    
    # Test with valid minimal data
    try:
        minimal_form = FormData(
            nombre_completo="Dr. Test User",
            correo_institucional="test@universidad.edu",
            año_academico=2024,
            trimestre="Q4",
            cursos_capacitacion=[],
            publicaciones=[],
            eventos_academicos=[],
            diseno_curricular=[],
            movilidad=[],
            reconocimientos=[],
            certificaciones=[]
        )
        print("✅ Formulario mínimo válido acepta correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error con formulario mínimo: {e}")
        return False

def test_database_connection():
    """Test database connection and basic operations"""
    
    print("\n🗄️ Probando Conexión a Base de Datos")
    print("=" * 40)
    
    try:
        db = SessionLocal()
        crud = FormularioCRUD(db)
        
        # Get statistics
        stats = crud.get_estadisticas_generales()
        
        print("✅ Conexión a base de datos exitosa!")
        print(f"   - Total formularios: {stats.get('total_formularios', 0)}")
        print(f"   - Pendientes: {stats.get('pendientes', 0)}")
        print(f"   - Aprobados: {stats.get('aprobados', 0)}")
        print(f"   - Rechazados: {stats.get('rechazados', 0)}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión a base de datos: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando Pruebas del Formulario Público")
    print("=" * 60)
    
    # Initialize application
    try:
        from app.startup import startup_application
        startup_result = startup_application()
        print(f"✅ Aplicación inicializada: {startup_result['status']}")
    except Exception as e:
        print(f"❌ Error al inicializar aplicación: {e}")
        sys.exit(1)
    
    # Run tests
    all_tests_passed = True
    
    try:
        # Test 1: Database connection
        all_tests_passed &= test_database_connection()
        
        # Test 2: Form validation
        all_tests_passed &= test_form_validation()
        
        # Test 3: Form submission
        all_tests_passed &= test_formulario_submission()
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        all_tests_passed = False
    
    # Final results
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("🎉 TODAS LAS PRUEBAS DEL FORMULARIO PÚBLICO PASARON!")
        print("✅ El formulario público está funcionando correctamente")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print("⚠️  Revisar los errores arriba")
    
    print("=" * 60)