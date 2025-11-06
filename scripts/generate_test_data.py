#!/usr/bin/env python3
"""
Script para generar datos de prueba para el sistema de informes docentes
"""

import sys
import os
from datetime import datetime, date, timedelta
import random
from faker import Faker

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connection import SessionLocal
from app.database.crud import FormularioCRUD
from app.models.database import (
    EstadoFormularioEnum, EstatusPublicacionEnum, TipoParticipacionEnum,
    TipoMovilidadEnum, TipoReconocimientoEnum, MaestroAutorizadoDB
)

# Initialize Faker for Spanish locale
fake = Faker('es_ES')

def create_authorized_teachers(db, teachers):
    """Create authorized teachers whitelist"""
    try:
        # Check if teachers already exist
        existing_teachers = db.query(MaestroAutorizadoDB).all()
        existing_emails = {teacher.correo_institucional for teacher in existing_teachers}
        
        teachers_created = 0
        
        for nombre, email in teachers:
            if email not in existing_emails:
                # Create new authorized teacher
                maestro = MaestroAutorizadoDB(
                    nombre_completo=nombre,
                    correo_institucional=email,
                    activo=True,
                    fecha_creacion=datetime.utcnow(),
                    fecha_actualizacion=datetime.utcnow()
                )
                db.add(maestro)
                teachers_created += 1
                print(f"   ✅ Maestro autorizado: {nombre}")
            else:
                print(f"   ⚠️  Ya existe: {nombre}")
        
        # Add some additional teachers that haven't submitted forms yet
        additional_teachers = [
            ("Dra. Patricia Elena Vásquez", "patricia.vasquez@universidad.edu"),
            ("Prof. Ricardo Antonio Mendoza", "ricardo.mendoza@universidad.edu"),
            ("Dr. Eduardo Francisco Ramírez", "eduardo.ramirez@universidad.edu"),
            ("Dra. Mónica Isabel Herrera", "monica.herrera@universidad.edu"),
            ("Prof. Daniel Alejandro Cruz", "daniel.cruz@universidad.edu"),
        ]
        
        for nombre, email in additional_teachers:
            if email not in existing_emails:
                maestro = MaestroAutorizadoDB(
                    nombre_completo=nombre,
                    correo_institucional=email,
                    activo=True,
                    fecha_creacion=datetime.utcnow(),
                    fecha_actualizacion=datetime.utcnow()
                )
                db.add(maestro)
                teachers_created += 1
                print(f"   ✅ Maestro autorizado (sin formularios): {nombre}")
        
        db.commit()
        print(f"📋 Lista blanca creada: {teachers_created} maestros autorizados")
        
    except Exception as e:
        print(f"❌ Error creando lista blanca: {e}")
        db.rollback()
        raise

def generate_test_data():
    """Generate comprehensive test data for the system"""
    
    db = SessionLocal()
    crud = FormularioCRUD(db)
    
    try:
        print("🚀 Generando datos de prueba...")
        
        # Sample teacher names and emails
        teachers = [
            ("Dr. María Elena González", "maria.gonzalez@universidad.edu"),
            ("Prof. Carlos Alberto Rodríguez", "carlos.rodriguez@universidad.edu"),
            ("Dra. Ana Patricia López", "ana.lopez@universidad.edu"),
            ("Dr. José Manuel Hernández", "jose.hernandez@universidad.edu"),
            ("Prof. Laura Isabel Martínez", "laura.martinez@universidad.edu"),
            ("Dr. Roberto Carlos Sánchez", "roberto.sanchez@universidad.edu"),
            ("Dra. Carmen Rosa Jiménez", "carmen.jimenez@universidad.edu"),
            ("Prof. Miguel Ángel Torres", "miguel.torres@universidad.edu"),
            ("Dra. Silvia Patricia Morales", "silvia.morales@universidad.edu"),
            ("Dr. Fernando José Castillo", "fernando.castillo@universidad.edu"),
            ("Prof. Gabriela María Vargas", "gabriela.vargas@universidad.edu"),
            ("Dr. Alejandro David Ruiz", "alejandro.ruiz@universidad.edu"),
        ]
        
        # 1. First, create the whitelist of authorized teachers
        print("📋 Creando lista blanca de maestros autorizados...")
        create_authorized_teachers(db, teachers)
        
        # Generate data for different years and quarters
        years = [2023, 2024, 2025]
        quarters = ["Trimestre 1", "Trimestre 2", "Trimestre 3", "Trimestre 4"]
        
        total_forms = 0
        
        for year in years:
            for quarter in quarters:
                # Generate 3-5 forms per quarter
                forms_this_quarter = random.randint(3, 5)
                
                for _ in range(forms_this_quarter):
                    teacher = random.choice(teachers)
                    
                    # Create form data
                    form_data = {
                        "nombre_completo": teacher[0],
                        "correo_institucional": teacher[1],
                        "año_academico": year,
                        "trimestre": quarter,
                        "estado": random.choice(["APROBADO", "PENDIENTE", "RECHAZADO"]),
                        "fecha_envio": generate_random_date_in_quarter(year, quarter),
                        "fecha_revision": None,
                        "revisado_por": None
                    }
                    
                    # Add revision data if approved or rejected
                    if form_data["estado"] != "PENDIENTE":
                        form_data["fecha_revision"] = form_data["fecha_envio"] + timedelta(days=random.randint(1, 7))
                        form_data["revisado_por"] = "Administrador"
                    
                    # Generate activities
                    form_data["cursos_capacitacion"] = generate_cursos_capacitacion()
                    form_data["publicaciones"] = generate_publicaciones()
                    form_data["eventos_academicos"] = generate_eventos_academicos()
                    form_data["diseno_curricular"] = generate_diseno_curricular()
                    form_data["movilidad"] = generate_movilidad()
                    form_data["reconocimientos"] = generate_reconocimientos()
                    form_data["certificaciones"] = generate_certificaciones()
                    form_data["otras_actividades"] = generate_otras_actividades()
                    
                    # Create the form
                    formulario = crud.create_formulario_completo(form_data)
                    if formulario:
                        total_forms += 1
                        print(f"✅ Formulario creado: {teacher[0]} - {year} {quarter}")
                    else:
                        print(f"❌ Error creando formulario para {teacher[0]} - {year} {quarter}")
        
        print(f"\n🎉 ¡Datos de prueba generados exitosamente!")
        print(f"📊 Total de formularios creados: {total_forms}")
        
        # Show summary statistics
        stats = crud.get_estadisticas_generales()
        print(f"\n📈 Estadísticas del sistema:")
        print(f"   - Total formularios: {stats['total_formularios']}")
        print(f"   - Pendientes: {stats['pendientes']}")
        print(f"   - Aprobados: {stats['aprobados']}")
        print(f"   - Rechazados: {stats['rechazados']}")
        
        # Show whitelist statistics
        total_authorized = db.query(MaestroAutorizadoDB).count()
        active_authorized = db.query(MaestroAutorizadoDB).filter(MaestroAutorizadoDB.activo == True).count()
        print(f"\n👥 Estadísticas de maestros autorizados:")
        print(f"   - Total maestros autorizados: {total_authorized}")
        print(f"   - Maestros activos: {active_authorized}")
        print(f"   - Maestros con formularios: {len(set(f.correo_institucional for f in crud.get_all_formularios(limit=1000)))}")
        
        # Show some authorized teachers
        print(f"\n📋 Algunos maestros autorizados:")
        sample_teachers = db.query(MaestroAutorizadoDB).limit(5).all()
        for teacher in sample_teachers:
            status = "✅ Activo" if teacher.activo else "❌ Inactivo"
            print(f"   - {teacher.nombre_completo} ({teacher.correo_institucional}) {status}")
        
    except Exception as e:
        print(f"❌ Error generando datos de prueba: {e}")
        db.rollback()
    finally:
        db.close()

def generate_random_date_in_quarter(year: int, quarter: str) -> datetime:
    """Generate a random date within the specified quarter"""
    quarter_map = {
        "Trimestre 1": (1, 3),
        "Trimestre 2": (4, 6),
        "Trimestre 3": (7, 9),
        "Trimestre 4": (10, 12)
    }
    
    start_month, end_month = quarter_map[quarter]
    
    # Random month within quarter
    month = random.randint(start_month, end_month)
    
    # Random day within month
    if month in [1, 3, 5, 7, 8, 10, 12]:
        max_day = 31
    elif month in [4, 6, 9, 11]:
        max_day = 30
    else:  # February
        max_day = 29 if year % 4 == 0 else 28
    
    day = random.randint(1, max_day)
    
    # Random time
    hour = random.randint(8, 18)
    minute = random.randint(0, 59)
    
    return datetime(year, month, day, hour, minute)

def generate_cursos_capacitacion():
    """Generate sample training courses"""
    courses = [
        "Metodologías Activas de Aprendizaje",
        "Tecnologías Educativas Digitales",
        "Evaluación por Competencias",
        "Diseño Curricular Basado en Competencias",
        "Investigación Educativa",
        "Gestión de Aulas Virtuales",
        "Pedagogía Inclusiva",
        "Neuroeducación y Aprendizaje",
        "Liderazgo Académico",
        "Innovación Educativa"
    ]
    
    num_courses = random.randint(1, 4)
    selected_courses = random.sample(courses, num_courses)
    
    result = []
    for course in selected_courses:
        result.append({
            "nombre_curso": course,
            "fecha": fake.date_between(start_date='-1y', end_date='today').isoformat(),
            "horas": random.choice([20, 30, 40, 50, 60, 80, 100])
        })
    
    return result

def generate_publicaciones():
    """Generate sample publications"""
    if random.random() < 0.3:  # 30% chance of no publications
        return []
    
    publication_titles = [
        "Innovación en Metodologías de Enseñanza Superior",
        "El Impacto de la Tecnología en el Aprendizaje",
        "Estrategias de Evaluación Formativa",
        "Desarrollo de Competencias Digitales en Docentes",
        "Pedagogía Inclusiva en el Aula Universitaria",
        "Investigación-Acción en Contextos Educativos",
        "Neurociencia y Educación: Nuevos Paradigmas",
        "Gestión del Conocimiento en Instituciones Educativas"
    ]
    
    journals = [
        "Revista de Educación Superior",
        "Journal of Educational Innovation",
        "Revista Iberoamericana de Educación",
        "Educational Technology & Society",
        "Revista de Investigación Educativa",
        "International Journal of Educational Research"
    ]
    
    num_pubs = random.randint(1, 3)
    result = []
    
    for _ in range(num_pubs):
        # Generate co-authors
        num_authors = random.randint(1, 4)
        authors = [fake.name() for _ in range(num_authors)]
        
        result.append({
            "autores": ", ".join(authors),
            "titulo": random.choice(publication_titles),
            "evento_revista": random.choice(journals),
            "estatus": random.choice(["ACEPTADO", "EN_REVISION", "PUBLICADO"])
        })
    
    return result

def generate_eventos_academicos():
    """Generate sample academic events"""
    if random.random() < 0.2:  # 20% chance of no events
        return []
    
    events = [
        "Congreso Internacional de Educación Superior",
        "Simposio de Innovación Educativa",
        "Conferencia de Tecnología Educativa",
        "Encuentro de Investigación Pedagógica",
        "Seminario de Metodologías Activas",
        "Foro de Buenas Prácticas Docentes",
        "Workshop de Evaluación Educativa",
        "Coloquio de Neuroeducación"
    ]
    
    num_events = random.randint(1, 3)
    result = []
    
    for _ in range(num_events):
        result.append({
            "nombre_evento": random.choice(events),
            "fecha": fake.date_between(start_date='-1y', end_date='today').isoformat(),
            "tipo_participacion": random.choice(["ORGANIZADOR", "PARTICIPANTE", "PONENTE"])
        })
    
    return result

def generate_diseno_curricular():
    """Generate sample curriculum design"""
    if random.random() < 0.4:  # 40% chance of no curriculum design
        return []
    
    courses = [
        "Fundamentos de Programación",
        "Metodología de la Investigación",
        "Estadística Aplicada",
        "Diseño de Sistemas",
        "Gestión de Proyectos",
        "Ética Profesional",
        "Comunicación Efectiva",
        "Emprendimiento e Innovación"
    ]
    
    num_designs = random.randint(1, 2)
    result = []
    
    for _ in range(num_designs):
        course = random.choice(courses)
        result.append({
            "nombre_curso": course,
            "descripcion": f"Diseño curricular completo para la materia {course}, incluyendo objetivos, contenidos, metodología y evaluación."
        })
    
    return result

def generate_movilidad():
    """Generate sample mobility experiences"""
    if random.random() < 0.7:  # 70% chance of no mobility
        return []
    
    experiences = [
        "Intercambio académico con Universidad de Barcelona",
        "Estancia de investigación en MIT",
        "Programa de movilidad docente con Universidad Nacional de Colombia",
        "Conferencia magistral en Universidad de Chile",
        "Colaboración internacional con Oxford University",
        "Participación en programa Erasmus+"
    ]
    
    result = []
    experience = random.choice(experiences)
    
    result.append({
        "descripcion": experience,
        "tipo": "INTERNACIONAL" if any(word in experience.lower() for word in ["internacional", "mit", "oxford", "barcelona", "erasmus"]) else "NACIONAL",
        "fecha": fake.date_between(start_date='-2y', end_date='today').isoformat()
    })
    
    return result

def generate_reconocimientos():
    """Generate sample recognitions"""
    if random.random() < 0.6:  # 60% chance of no recognitions
        return []
    
    recognitions = [
        ("Mejor Docente del Año", "PREMIO"),
        ("Reconocimiento a la Excelencia Académica", "DISTINCION"),
        ("Doctorado Honoris Causa", "GRADO"),
        ("Premio a la Innovación Educativa", "PREMIO"),
        ("Distinción por Trayectoria Académica", "DISTINCION"),
        ("Miembro Honorario de la Academia", "DISTINCION")
    ]
    
    recognition = random.choice(recognitions)
    
    return [{
        "nombre": recognition[0],
        "tipo": recognition[1],
        "fecha": fake.date_between(start_date='-3y', end_date='today').isoformat()
    }]

def generate_certificaciones():
    """Generate sample certifications"""
    if random.random() < 0.3:  # 30% chance of no certifications
        return []
    
    certifications = [
        "Certificación en Google for Education",
        "Microsoft Certified Educator",
        "Certificación en Moodle",
        "Canvas Certified Educator",
        "Certificación en Design Thinking",
        "Scrum Master Certification",
        "Certificación en Metodologías Ágiles",
        "AWS Certified Cloud Practitioner"
    ]
    
    num_certs = random.randint(1, 2)
    selected_certs = random.sample(certifications, num_certs)
    
    result = []
    for cert in selected_certs:
        result.append({
            "nombre": cert,
            "fecha_obtencion": fake.date_between(start_date='-2y', end_date='today').isoformat()
        })
    
    return result

def generate_otras_actividades():
    """Generate sample other academic activities"""
    if random.random() < 0.4:  # 40% chance of no other activities
        return []
    
    activities = [
        ("Asesoría y Titulación", "Dirección de tesis de licenciatura", "Asesoría académica para estudiantes en proceso de titulación"),
        ("Solicitudes Atendidas", "Atención a solicitudes estudiantiles", "Resolución de consultas académicas y administrativas"),
        ("Comités Académicos", "Participación en Comité Curricular", "Colaboración en revisión y actualización de planes de estudio"),
        ("Evaluación Externa", "Evaluador de proyectos de investigación", "Revisión y evaluación de propuestas de investigación"),
        ("Mentoría Docente", "Programa de mentoría para nuevos profesores", "Acompañamiento y orientación a docentes de reciente ingreso"),
        ("Vinculación Empresarial", "Coordinación de prácticas profesionales", "Gestión de convenios y seguimiento de estudiantes en empresas"),
        ("Divulgación Científica", "Conferencias magistrales", "Presentaciones de divulgación científica para público general"),
        ("Gestión Académica", "Coordinación de programa académico", "Administración y seguimiento de programas educativos")
    ]
    
    num_activities = random.randint(1, 3)
    selected_activities = random.sample(activities, num_activities)
    
    result = []
    for categoria, titulo, descripcion in selected_activities:
        result.append({
            "categoria": categoria,
            "titulo": titulo,
            "descripcion": descripcion,
            "fecha": fake.date_between(start_date='-1y', end_date='today').isoformat(),
            "cantidad": random.randint(1, 10) if categoria in ["Solicitudes Atendidas", "Asesoría y Titulación"] else None,
            "observaciones": "Actividad completada satisfactoriamente" if random.random() < 0.3 else None
        })
    
    return result

if __name__ == "__main__":
    print("🎯 Generador de Datos de Prueba - Sistema de Informes Docentes")
    print("=" * 60)
    
    # Ask for confirmation
    response = input("¿Desea generar datos de prueba? (s/n): ").lower().strip()
    
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        generate_test_data()
    else:
        print("❌ Operación cancelada.")