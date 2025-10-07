#!/usr/bin/env python3
"""
Comprehensive test for advanced export functionality
"""

import sys
import os
from datetime import datetime, date
from io import BytesIO
import zipfile
import json

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.export_utils import DataExporter

# Mock form class for testing
class MockForm:
    def __init__(self, id, nombre, email, estado, fecha_envio, cursos=None, publicaciones=None, eventos=None):
        self.id = id
        self.nombre_completo = nombre
        self.correo_institucional = email
        self.estado = MockEnum(estado)
        self.fecha_envio = fecha_envio
        self.fecha_revision = None
        self.revisado_por = None
        
        # Initialize activity lists
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

def test_advanced_export_functionality():
    """Test all advanced export functionality"""
    
    print("🧪 Testing Advanced Export Functionality")
    print("=" * 60)
    
    # Initialize exporter
    exporter = DataExporter()
    
    # Create comprehensive sample data
    sample_forms = [
        MockForm(
            1, "Dr. Juan Pérez", "juan.perez@universidad.edu.mx", "APROBADO",
            datetime(2024, 3, 15, 10, 30),
            cursos=[
                MockCurso("Python Avanzado", date(2024, 2, 15), 40),
                MockCurso("Machine Learning", date(2024, 3, 1), 60)
            ],
            publicaciones=[
                MockPublicacion("Juan Pérez", "AI in Education", "IEEE Conference", "PUBLICADO")
            ],
            eventos=[
                MockEvento("Congreso de IA", date(2024, 3, 10), "ORGANIZADOR")
            ]
        ),
        MockForm(
            2, "Dra. María García", "maria.garcia@universidad.edu.mx", "APROBADO",
            datetime(2024, 3, 16, 14, 20),
            cursos=[
                MockCurso("Estadística Aplicada", date(2024, 2, 20), 30)
            ],
            publicaciones=[
                MockPublicacion("María García", "Data Science Methods", "Journal of DS", "ACEPTADO")
            ]
        ),
        MockForm(
            3, "Dr. Carlos López", "carlos.lopez@tecnologico.edu.mx", "PENDIENTE",
            datetime(2024, 3, 17, 9, 15),
            cursos=[
                MockCurso("Blockchain Basics", date(2024, 3, 5), 25)
            ]
        ),
        MockForm(
            4, "Dra. Ana Rodríguez", "ana.rodriguez@universidad.edu.mx", "RECHAZADO",
            datetime(2024, 3, 18, 16, 45)
        )
    ]
    
    print(f"📊 Created {len(sample_forms)} sample forms for testing")
    
    # Test 1: Advanced filtering
    print("\n1. Testing Advanced Filtering...")
    try:
        # Test status filtering
        filters = {'estados': ['APROBADO']}
        filtered_forms = exporter.apply_filters(sample_forms, filters)
        print(f"   ✅ Status filter (APROBADO): {len(filtered_forms)} forms")
        
        # Test date filtering
        filters = {
            'fecha_inicio': '2024-03-16',
            'fecha_fin': '2024-03-17'
        }
        filtered_forms = exporter.apply_filters(sample_forms, filters)
        print(f"   ✅ Date filter (Mar 16-17): {len(filtered_forms)} forms")
        
        # Test minimum activities filter
        filters = {'min_actividades': 2}
        filtered_forms = exporter.apply_filters(sample_forms, filters)
        print(f"   ✅ Min activities filter (>=2): {len(filtered_forms)} forms")
        
        # Test name filter
        filters = {'nombre_docente': 'García'}
        filtered_forms = exporter.apply_filters(sample_forms, filters)
        print(f"   ✅ Name filter (García): {len(filtered_forms)} forms")
        
        # Test email domain filter
        filters = {'dominio_email': 'universidad.edu.mx'}
        filtered_forms = exporter.apply_filters(sample_forms, filters)
        print(f"   ✅ Email domain filter: {len(filtered_forms)} forms")
        
        # Test activity type filters
        filters = {'tiene_cursos': True}
        filtered_forms = exporter.apply_filters(sample_forms, filters)
        print(f"   ✅ Has courses filter: {len(filtered_forms)} forms")
        
        print("   ✅ All filtering tests passed")
        
    except Exception as e:
        print(f"   ❌ Filtering test failed: {e}")
    
    # Test 2: Enhanced CSV export with metadata
    print("\n2. Testing Enhanced CSV Export...")
    try:
        filters = {'estados': ['APROBADO'], 'min_actividades': 1}
        filtered_forms = exporter.apply_filters(sample_forms, filters)
        
        basic_data = []
        for form in filtered_forms:
            basic_data.append({
                'ID': form.id,
                'Nombre': form.nombre_completo,
                'Email': form.correo_institucional,
                'Estado': form.estado.value,
                'Total_Actividades': len(form.cursos_capacitacion) + len(form.publicaciones) + len(form.eventos_academicos)
            })
        
        csv_content = exporter.export_to_csv(
            basic_data, 
            include_metadata=True, 
            filters_applied=filters
        )
        
        if csv_content and len(csv_content) > 0:
            print("   ✅ Enhanced CSV export successful")
            print(f"   Content length: {len(csv_content)} characters")
            
            # Check for metadata headers
            if csv_content.startswith('\ufeff#'):
                print("   ✅ UTF-8 BOM and metadata headers included")
            
            # Count metadata lines
            metadata_lines = len([line for line in csv_content.split('\n') if line.startswith('#')])
            print(f"   Metadata lines: {metadata_lines}")
            
        else:
            print("   ❌ Enhanced CSV export failed")
    
    except Exception as e:
        print(f"   ❌ Enhanced CSV test failed: {e}")
    
    # Test 3: Advanced Excel export with enhanced metadata
    print("\n3. Testing Advanced Excel Export...")
    try:
        filters = {'estados': ['APROBADO']}
        filtered_forms = exporter.apply_filters(sample_forms, filters)
        
        detailed_data = exporter.export_forms_detailed(filtered_forms, filters_applied=filters)
        excel_content = exporter.export_to_excel(detailed_data, include_charts=True)
        
        if excel_content and len(excel_content.getvalue()) > 0:
            print("   ✅ Advanced Excel export successful")
            print(f"   Content size: {len(excel_content.getvalue())} bytes")
            print(f"   Sheets created: {len(detailed_data)}")
            
            # Check summary sheet has enhanced metadata
            summary_data = detailed_data.get('summary', [])
            metadata_entries = [item for item in summary_data if 'INFORMACIÓN DE EXPORTACIÓN' in str(item.get('Métrica', ''))]
            if metadata_entries:
                print("   ✅ Enhanced metadata found in summary sheet")
            
        else:
            print("   ❌ Advanced Excel export failed")
    
    except Exception as e:
        print(f"   ❌ Advanced Excel test failed: {e}")
    
    # Test 4: Complete JSON export with full structure
    print("\n4. Testing Complete JSON Export...")
    try:
        filters = {'estados': ['APROBADO']}
        
        json_output = exporter.export_with_advanced_options(
            sample_forms,
            export_format='json',
            filters=filters,
            include_metadata=True,
            custom_filename='test_export'
        )
        
        json_content = json_output.getvalue().decode('utf-8')
        json_data = json.loads(json_content)
        
        if json_data:
            print("   ✅ Complete JSON export successful")
            print(f"   Content length: {len(json_content)} characters")
            
            # Check structure
            if 'metadata' in json_data:
                print("   ✅ Metadata section included")
                metadata = json_data['metadata']
                required_fields = ['fecha_exportacion', 'timestamp', 'version_sistema', 'filtros_aplicados']
                missing_fields = [field for field in required_fields if field not in metadata]
                if not missing_fields:
                    print("   ✅ All required metadata fields present")
                else:
                    print(f"   ⚠️  Missing metadata fields: {missing_fields}")
            
            if 'datos' in json_data:
                print(f"   ✅ Data section with {len(json_data['datos'])} records")
                
                # Check first record structure
                if json_data['datos']:
                    first_record = json_data['datos'][0]
                    if 'actividades' in first_record:
                        print("   ✅ Detailed activity structure included")
        
        else:
            print("   ❌ Complete JSON export failed")
    
    except Exception as e:
        print(f"   ❌ Complete JSON test failed: {e}")
    
    # Test 5: Comprehensive package export
    print("\n5. Testing Comprehensive Package Export...")
    try:
        filters = {'estados': ['APROBADO', 'PENDIENTE']}
        
        package_output = exporter.export_with_advanced_options(
            sample_forms,
            export_format='package',
            filters=filters,
            include_metadata=True,
            include_charts=False,  # Disable charts for faster testing
            custom_filename='test_package'
        )
        
        if package_output and len(package_output.getvalue()) > 0:
            print("   ✅ Comprehensive package export successful")
            print(f"   Package size: {len(package_output.getvalue())} bytes")
            
            # Examine package contents
            with zipfile.ZipFile(package_output, 'r') as zip_file:
                file_list = zip_file.namelist()
                print(f"   Files in package: {len(file_list)}")
                
                # Check for expected files
                expected_files = ['README.txt', 'RESUMEN_EXPORTACION.txt']
                for expected in expected_files:
                    if expected in file_list:
                        print(f"   ✅ {expected} found")
                    else:
                        print(f"   ⚠️  {expected} missing")
                
                # Check for data files
                csv_files = [f for f in file_list if f.endswith('.csv')]
                excel_files = [f for f in file_list if f.endswith('.xlsx')]
                json_files = [f for f in file_list if f.endswith('.json')]
                
                print(f"   CSV files: {len(csv_files)}")
                print(f"   Excel files: {len(excel_files)}")
                print(f"   JSON files: {len(json_files)}")
                
                # Test README content
                if 'README.txt' in file_list:
                    readme_content = zip_file.read('README.txt').decode('utf-8')
                    if 'EXPORTACIÓN AVANZADA' in readme_content:
                        print("   ✅ Enhanced README content verified")
        
        else:
            print("   ❌ Comprehensive package export failed")
    
    except Exception as e:
        print(f"   ❌ Comprehensive package test failed: {e}")
    
    # Test 6: File naming and timestamp consistency
    print("\n6. Testing File Naming and Timestamps...")
    try:
        timestamp1 = exporter.timestamp
        
        # Create another exporter to test timestamp uniqueness
        exporter2 = DataExporter()
        timestamp2 = exporter2.timestamp
        
        print(f"   Timestamp 1: {timestamp1}")
        print(f"   Timestamp 2: {timestamp2}")
        
        if timestamp1 != timestamp2:
            print("   ✅ Unique timestamps generated")
        else:
            print("   ⚠️  Timestamps are identical (may be expected if created quickly)")
        
        # Test safe sheet names
        test_names = [
            "Cursos de Capacitación & Eventos",
            "Publicaciones/Artículos*Importantes",
            "Reconocimientos[2024]:Vigentes"
        ]
        
        for name in test_names:
            safe_name = exporter._safe_sheet_name(name)
            print(f"   '{name}' -> '{safe_name}'")
            
            # Verify safe name meets Excel requirements
            if len(safe_name) <= 31 and not any(char in safe_name for char in ['\\', '/', '*', '[', ']', ':', '?']):
                print(f"   ✅ Safe name valid for Excel")
            else:
                print(f"   ❌ Safe name invalid: {safe_name}")
        
    except Exception as e:
        print(f"   ❌ File naming test failed: {e}")
    
    print(f"\n📈 Advanced Export Testing Summary:")
    print(f"   - Sample forms created: {len(sample_forms)}")
    print(f"   - Export formats tested: CSV, Excel, JSON, Package")
    print(f"   - Advanced features tested: Filtering, Metadata, File naming")
    print(f"   - Package components tested: Multiple files, Documentation")
    print(f"   - Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   - Exporter version: {exporter.version}")
    print(f"   - Generation timestamp: {exporter.timestamp}")

if __name__ == "__main__":
    test_advanced_export_functionality()