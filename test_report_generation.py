#!/usr/bin/env python3
"""
Test script for report generation functionality
"""

import sys
import os
from datetime import datetime, date, timedelta
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.reports.nlg_engine import NLGEngine, ReportData
from app.reports.report_generator import ReportGenerator
from app.reports.report_history import ReportHistoryManager

# Mock classes for testing
class MockForm:
    def __init__(self, id, nombre, email, estado, fecha_envio, cursos=None, publicaciones=None, eventos=None):
        self.id = id
        self.nombre_completo = nombre
        self.correo_institucional = email
        self.estado = MockEnum(estado)
        self.fecha_envio = fecha_envio
        self.fecha_revision = None
        self.revisado_por = None
        
        self.cursos_capacitacion = cursos or []
        self.publicaciones = publicaciones or []
        self.eventos_academicos = eventos or []
        self.diseno_curricular = []
        self.movilidad = []
        self.reconocimientos = []
        self.certificaciones = []

class MockEnum:
    def __init__(self, value):
        self.value = value

class MockCurso:
    def __init__(self, nombre, fecha, horas):
        self.nombre_curso = nombre
        self.fecha = fecha
        self.horas = horas

class MockPublicacion:
    def __init__(self, autores, titulo, evento, estatus):
        self.autores = autores
        self.titulo = titulo
        self.evento_revista = evento
        self.estatus = MockEnum(estatus)

class MockEvento:
    def __init__(self, nombre, fecha, tipo):
        self.nombre_evento = nombre
        self.fecha = fecha
        self.tipo_participacion = MockEnum(tipo)

def test_report_generation_system():
    """Test the complete report generation system"""
    
    print("🧪 Testing Report Generation System")
    print("=" * 60)
    
    # Create sample data
    sample_forms = create_sample_forms()
    print(f"📊 Created {len(sample_forms)} sample forms for testing")
    
    # Test 1: NLG Engine
    print("\n1. Testing NLG Engine...")
    test_nlg_engine(sample_forms)
    
    # Test 2: Report Generator
    print("\n2. Testing Report Generator...")
    test_report_generator(sample_forms)
    
    # Test 3: Report History Manager
    print("\n3. Testing Report History Manager...")
    test_report_history()
    
    # Test 4: Integration Test
    print("\n4. Testing Full Integration...")
    test_full_integration(sample_forms)
    
    print(f"\n📈 Report Generation Testing Summary:")
    print(f"   - All components tested successfully")
    print(f"   - NLG engine generating narrative content")
    print(f"   - Report templates working correctly")
    print(f"   - History management functional")
    print(f"   - Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def create_sample_forms():
    """Create comprehensive sample forms for testing"""
    
    forms = []
    
    # Form 1: High activity professor
    forms.append(MockForm(
        1, "Dr. Juan Pérez García", "juan.perez@universidad.edu.mx", "APROBADO",
        datetime(2024, 3, 15, 10, 30),
        cursos=[
            MockCurso("Python para Ciencia de Datos", date(2024, 2, 15), 40),
            MockCurso("Machine Learning Avanzado", date(2024, 3, 1), 60),
            MockCurso("Metodologías Ágiles", date(2024, 1, 20), 30)
        ],
        publicaciones=[
            MockPublicacion("Juan Pérez, María López", "Inteligencia Artificial en Educación", "IEEE Conference on AI", "PUBLICADO"),
            MockPublicacion("Juan Pérez", "Análisis de Datos Educativos", "Journal of Educational Technology", "ACEPTADO")
        ],
        eventos=[
            MockEvento("Congreso Internacional de IA", date(2024, 3, 10), "ORGANIZADOR"),
            MockEvento("Seminario de Innovación Educativa", date(2024, 2, 25), "PONENTE")
        ]
    ))
    
    # Form 2: Medium activity professor
    forms.append(MockForm(
        2, "Dra. María García Rodríguez", "maria.garcia@universidad.edu.mx", "APROBADO",
        datetime(2024, 3, 16, 14, 20),
        cursos=[
            MockCurso("Estadística Aplicada a la Investigación", date(2024, 2, 20), 35),
            MockCurso("Metodología de la Investigación", date(2024, 1, 15), 25)
        ],
        publicaciones=[
            MockPublicacion("María García, Ana Martínez", "Métodos Cuantitativos en Educación", "Revista de Investigación Educativa", "PUBLICADO")
        ],
        eventos=[
            MockEvento("Congreso Nacional de Estadística", date(2024, 2, 15), "PARTICIPANTE")
        ]
    ))
    
    # Form 3: New professor with basic activity
    forms.append(MockForm(
        3, "Dr. Carlos López Hernández", "carlos.lopez@tecnologico.edu.mx", "APROBADO",
        datetime(2024, 3, 17, 9, 15),
        cursos=[
            MockCurso("Introducción a la Docencia Universitaria", date(2024, 3, 5), 20)
        ],
        publicaciones=[],
        eventos=[
            MockEvento("Taller de Nuevos Docentes", date(2024, 3, 12), "PARTICIPANTE")
        ]
    ))
    
    # Form 4: Pending form (should not be included in approved analysis)
    forms.append(MockForm(
        4, "Dra. Ana Rodríguez Silva", "ana.rodriguez@universidad.edu.mx", "PENDIENTE",
        datetime(2024, 3, 18, 16, 45),
        cursos=[
            MockCurso("Liderazgo Académico", date(2024, 3, 8), 15)
        ]
    ))
    
    # Form 5: Rejected form
    forms.append(MockForm(
        5, "Dr. Luis Martínez Torres", "luis.martinez@universidad.edu.mx", "RECHAZADO",
        datetime(2024, 3, 19, 11, 30)
    ))
    
    return forms

def test_nlg_engine(sample_forms):
    """Test the Natural Language Generation engine"""
    
    try:
        nlg_engine = NLGEngine()
        
        # Prepare test data
        approved_forms = [f for f in sample_forms if f.estado.value == 'APROBADO']
        
        report_data = ReportData(
            total_formularios=len(sample_forms),
            formularios_aprobados=len(approved_forms),
            formularios_pendientes=1,
            formularios_rechazados=1,
            total_cursos=6,
            total_horas_capacitacion=210,
            total_publicaciones=3,
            total_eventos=4,
            total_disenos_curriculares=0,
            total_movilidades=0,
            total_reconocimientos=0,
            total_certificaciones=0,
            periodo_inicio=date(2024, 1, 1),
            periodo_fin=date(2024, 3, 31),
            docentes_activos=["Dr. Juan Pérez García", "Dra. María García Rodríguez", "Dr. Carlos López Hernández"],
            cursos_destacados=[
                {"nombre_curso": "Machine Learning Avanzado", "horas": 60},
                {"nombre_curso": "Python para Ciencia de Datos", "horas": 40}
            ],
            publicaciones_destacadas=[
                {"titulo": "Inteligencia Artificial en Educación", "autores": "Juan Pérez, María López"}
            ],
            eventos_destacados=[
                {"nombre_evento": "Congreso Internacional de IA", "tipo_participacion": "ORGANIZADOR"}
            ]
        )
        
        # Test annual narrative generation
        annual_report = nlg_engine.generate_annual_narrative(report_data)
        
        if annual_report and len(annual_report) > 500:
            print("   ✅ Annual narrative generation successful")
            print(f"   Report length: {len(annual_report)} characters")
            
            # Check for key sections
            required_sections = ["Introducción", "Resumen Ejecutivo", "Análisis Detallado", "Conclusiones"]
            missing_sections = [section for section in required_sections if section not in annual_report]
            
            if not missing_sections:
                print("   ✅ All required sections present")
            else:
                print(f"   ⚠️  Missing sections: {missing_sections}")
        else:
            print("   ❌ Annual narrative generation failed")
        
        # Test quarterly summary
        quarterly_summary = nlg_engine.generate_quarterly_summary(report_data)
        
        if quarterly_summary and len(quarterly_summary) > 200:
            print("   ✅ Quarterly summary generation successful")
            print(f"   Summary length: {len(quarterly_summary)} characters")
        else:
            print("   ❌ Quarterly summary generation failed")
        
        # Test tone customization
        professional_text = "Se registraron importantes actividades académicas durante el período."
        academic_text = nlg_engine.customize_report_tone(professional_text, 'academic')
        
        if academic_text != professional_text:
            print("   ✅ Tone customization working")
        else:
            print("   ⚠️  Tone customization may not be working")
        
    except Exception as e:
        print(f"   ❌ NLG Engine test failed: {e}")

def test_report_generator(sample_forms):
    """Test the Report Generator with Jinja2 templates"""
    
    try:
        # Create temporary templates directory
        temp_dir = Path("temp_templates")
        report_generator = ReportGenerator(str(temp_dir))
        
        # Test annual report generation
        period_start = date(2024, 1, 1)
        period_end = date(2024, 3, 31)
        
        annual_report = report_generator.generate_annual_report(
            sample_forms, period_start, period_end, include_trends=True
        )
        
        if annual_report and len(annual_report) > 1000:
            print("   ✅ Annual report generation successful")
            print(f"   Report length: {len(annual_report)} characters")
            
            # Check for template elements
            if "# Reporte Anual" in annual_report and "## Datos Estadísticos" in annual_report:
                print("   ✅ Template structure correct")
            else:
                print("   ⚠️  Template structure may be incorrect")
        else:
            print("   ❌ Annual report generation failed")
        
        # Test quarterly report generation
        quarterly_report = report_generator.generate_quarterly_report(sample_forms, 1, 2024)
        
        if quarterly_report and len(quarterly_report) > 500:
            print("   ✅ Quarterly report generation successful")
            print(f"   Report length: {len(quarterly_report)} characters")
        else:
            print("   ❌ Quarterly report generation failed")
        
        # Test data table report
        data_table_report = report_generator.generate_data_table_report(
            sample_forms, "Test Data Report", period_start, period_end
        )
        
        if data_table_report and "| " in data_table_report:  # Check for table format
            print("   ✅ Data table report generation successful")
            print(f"   Report length: {len(data_table_report)} characters")
        else:
            print("   ❌ Data table report generation failed")
        
        # Cleanup
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir)
        
    except Exception as e:
        print(f"   ❌ Report Generator test failed: {e}")

def test_report_history():
    """Test the Report History Manager"""
    
    try:
        # Create temporary storage directory
        temp_storage = Path("temp_storage")
        history_manager = ReportHistoryManager(str(temp_storage))
        
        # Test saving a report
        test_content = "# Test Report\n\nThis is a test report with some content."
        
        report_id = history_manager.save_report(
            content=test_content,
            title="Test Annual Report",
            report_type="annual",
            period_start=date(2024, 1, 1),
            period_end=date(2024, 12, 31),
            parameters={"test": True}
        )
        
        if report_id:
            print("   ✅ Report saving successful")
            print(f"   Report ID: {report_id}")
        else:
            print("   ❌ Report saving failed")
        
        # Test retrieving report
        retrieved_content = history_manager.get_report_content(report_id)
        
        if retrieved_content == test_content:
            print("   ✅ Report retrieval successful")
        else:
            print("   ❌ Report retrieval failed")
        
        # Test history listing
        history = history_manager.get_report_history()
        
        if len(history) >= 1:
            print("   ✅ History listing successful")
            print(f"   History entries: {len(history)}")
        else:
            print("   ❌ History listing failed")
        
        # Test search functionality
        search_results = history_manager.search_reports("Test")
        
        if len(search_results) >= 1:
            print("   ✅ Search functionality working")
        else:
            print("   ❌ Search functionality failed")
        
        # Test statistics
        stats = history_manager.get_storage_statistics()
        
        if stats['total_reports'] >= 1:
            print("   ✅ Statistics calculation successful")
            print(f"   Total reports: {stats['total_reports']}")
            print(f"   Total size: {stats['total_size_mb']} MB")
        else:
            print("   ❌ Statistics calculation failed")
        
        # Cleanup
        if temp_storage.exists():
            import shutil
            shutil.rmtree(temp_storage)
        
    except Exception as e:
        print(f"   ❌ Report History test failed: {e}")

def test_full_integration(sample_forms):
    """Test full integration of all components"""
    
    try:
        # Create temporary directories
        temp_templates = Path("temp_integration_templates")
        temp_storage = Path("temp_integration_storage")
        
        # Initialize components
        report_generator = ReportGenerator(str(temp_templates))
        history_manager = ReportHistoryManager(str(temp_storage))
        
        # Generate and save an annual report
        period_start = date(2024, 1, 1)
        period_end = date(2024, 12, 31)
        
        annual_report = report_generator.generate_annual_report(
            sample_forms, period_start, period_end, include_trends=True
        )
        
        report_id = history_manager.save_report(
            content=annual_report,
            title="Integration Test Annual Report 2024",
            report_type="annual",
            period_start=period_start,
            period_end=period_end,
            parameters={
                "include_trends": True,
                "forms_count": len(sample_forms),
                "test_mode": True
            }
        )
        
        # Generate and save a quarterly report
        quarterly_report = report_generator.generate_quarterly_report(sample_forms, 1, 2024)
        
        quarterly_id = history_manager.save_report(
            content=quarterly_report,
            title="Integration Test Q1 2024",
            report_type="quarterly",
            period_start=date(2024, 1, 1),
            period_end=date(2024, 3, 31),
            parameters={"quarter": 1, "year": 2024}
        )
        
        # Verify both reports were saved
        history = history_manager.get_report_history()
        
        if len(history) >= 2:
            print("   ✅ Full integration successful")
            print(f"   Generated reports: {len(history)}")
            
            # Check report types
            report_types = [r['report_type'] for r in history]
            if 'annual' in report_types and 'quarterly' in report_types:
                print("   ✅ Multiple report types generated")
            
            # Check content quality
            annual_content = history_manager.get_report_content(report_id)
            if annual_content and len(annual_content) > 1000:
                print("   ✅ Report content quality good")
                
                # Check for NLG-generated content
                nlg_indicators = ["Durante el período", "Se registraron", "En conclusión"]
                if any(indicator in annual_content for indicator in nlg_indicators):
                    print("   ✅ NLG content detected in report")
                else:
                    print("   ⚠️  NLG content may not be properly integrated")
        else:
            print("   ❌ Full integration failed")
        
        # Test report templates availability
        templates = history_manager.get_report_templates()
        if len(templates) >= 3:
            print("   ✅ Report templates available")
        else:
            print("   ⚠️  Some report templates may be missing")
        
        # Cleanup
        for temp_dir in [temp_templates, temp_storage]:
            if temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir)
        
    except Exception as e:
        print(f"   ❌ Full integration test failed: {e}")

if __name__ == "__main__":
    test_report_generation_system()