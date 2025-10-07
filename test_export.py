#!/usr/bin/env python3
"""
Test script for export functionality
"""

import sys
import os
from datetime import datetime, date

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import SessionLocal
from app.database.crud import FormularioCRUD
from app.utils.export_utils import DataExporter
from app.models.schemas import FormData, CursoCapacitacionBase, PublicacionBase

def test_export_functionality():
    """Test the export functionality"""
    
    print("🧪 Testing Export Functionality")
    print("=" * 50)
    
    # Initialize exporter
    exporter = DataExporter()
    
    # Load data from database
    db = SessionLocal()
    try:
        crud = FormularioCRUD(db)
        
        # Get forms and metrics
        forms = crud.get_all_formularios(limit=10)
        metrics = crud.get_metricas_generales()
        
        print(f"📊 Loaded {len(forms)} forms for testing")
        
        if not forms:
            print("⚠️  No forms available for testing. Creating sample data...")
            create_sample_data(crud)
            forms = crud.get_all_formularios(limit=10)
        
        # Test CSV export
        print("\n1. Testing CSV Export...")
        try:
            basic_data = []
            for form in forms:
                basic_data.append({
                    'ID': form.id,
                    'Nombre': form.nombre_completo,
                    'Estado': form.estado.value,
                    'Fecha': form.fecha_envio.strftime('%Y-%m-%d') if form.fecha_envio else ''
                })
            
            csv_content = exporter.export_to_csv(basic_data)
            
            if csv_content:
                print("✅ CSV export successful")
                print(f"   Content length: {len(csv_content)} characters")
                print(f"   Sample: {csv_content[:100]}...")
            else:
                print("❌ CSV export failed - empty content")
        
        except Exception as e:
            print(f"❌ CSV export failed: {e}")
        
        # Test Excel export
        print("\n2. Testing Excel Export...")
        try:
            detailed_data = exporter.export_forms_detailed(forms)
            excel_content = exporter.export_to_excel(detailed_data, include_charts=False)
            
            if excel_content and excel_content.getvalue():
                print("✅ Excel export successful")
                print(f"   Content size: {len(excel_content.getvalue())} bytes")
                print(f"   Sheets created: {len(detailed_data)} sheets")
            else:
                print("❌ Excel export failed - empty content")
        
        except Exception as e:
            print(f"❌ Excel export failed: {e}")
        
        # Test JSON export
        print("\n3. Testing JSON Export...")
        try:
            metrics_report = exporter.export_metrics_report(metrics)
            json_content = exporter.export_to_json(metrics_report)
            
            if json_content:
                print("✅ JSON export successful")
                print(f"   Content length: {len(json_content)} characters")
                print(f"   Sample: {json_content[:150]}...")
            else:
                print("❌ JSON export failed - empty content")
        
        except Exception as e:
            print(f"❌ JSON export failed: {e}")
        
        # Test complete package
        print("\n4. Testing Complete Package Export...")
        try:
            package_content = exporter.create_export_package(
                forms, metrics, include_detailed=True, include_charts=False
            )
            
            if package_content and package_content.getvalue():
                print("✅ Package export successful")
                print(f"   Package size: {len(package_content.getvalue())} bytes")
            else:
                print("❌ Package export failed - empty content")
        
        except Exception as e:
            print(f"❌ Package export failed: {e}")
        
        # Test detailed export structure
        print("\n5. Testing Detailed Export Structure...")
        try:
            detailed_data = exporter.export_forms_detailed(forms)
            
            expected_sheets = [
                'summary', 'formularios', 'cursos', 'publicaciones', 
                'eventos', 'disenos_curriculares', 'movilidad', 
                'reconocimientos', 'certificaciones'
            ]
            
            missing_sheets = []
            for sheet in expected_sheets:
                if sheet not in detailed_data:
                    missing_sheets.append(sheet)
            
            if not missing_sheets:
                print("✅ All expected sheets present in detailed export")
                for sheet, data in detailed_data.items():
                    print(f"   - {sheet}: {len(data)} records")
            else:
                print(f"❌ Missing sheets: {missing_sheets}")
        
        except Exception as e:
            print(f"❌ Detailed export structure test failed: {e}")
        
        print(f"\n📈 Export Testing Summary:")
        print(f"   - Forms processed: {len(forms)}")
        print(f"   - Metrics available: {bool(metrics)}")
        print(f"   - Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    finally:
        db.close()

def create_sample_data(crud):
    """Create sample data for testing"""
    
    sample_forms = [
        FormData(
            nombre_completo="Dr. Test Usuario 1",
            correo_institucional="test1@universidad.edu.mx",
            cursos_capacitacion=[
                CursoCapacitacionBase(
                    nombre_curso="Curso de Prueba 1",
                    fecha=date(2024, 3, 15),
                    horas=20
                )
            ],
            publicaciones=[
                PublicacionBase(
                    autores="Test Usuario 1",
                    titulo="Artículo de Prueba 1",
                    evento_revista="Revista Test",
                    estatus="ACEPTADO"
                )
            ],
            eventos_academicos=[],
            diseno_curricular=[],
            movilidad=[],
            reconocimientos=[],
            certificaciones=[]
        ),
        FormData(
            nombre_completo="Dra. Test Usuario 2",
            correo_institucional="test2@universidad.edu.mx",
            cursos_capacitacion=[
                CursoCapacitacionBase(
                    nombre_curso="Curso de Prueba 2",
                    fecha=date(2024, 4, 10),
                    horas=30
                )
            ],
            publicaciones=[],
            eventos_academicos=[],
            diseno_curricular=[],
            movilidad=[],
            reconocimientos=[],
            certificaciones=[]
        )
    ]
    
    for form_data in sample_forms:
        db_form = crud.create_formulario(form_data)
        crud.aprobar_formulario(db_form.id, "test_admin")
    
    print("✅ Sample data created for testing")

if __name__ == "__main__":
    test_export_functionality()