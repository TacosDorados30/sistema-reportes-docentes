#!/usr/bin/env python3
"""
Test script for data processing engine
"""

import sys
import os
from datetime import datetime, date

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import SessionLocal
from app.core.data_processor import DataProcessor
from app.core.metrics_calculator import MetricsCalculator
from app.database.crud import FormularioCRUD
from app.models.schemas import FormData, CursoCapacitacionBase, PublicacionBase

def create_test_data():
    """Create test data for processing"""
    db = SessionLocal()
    try:
        crud = FormularioCRUD(db)
        
        # Create multiple test forms
        test_forms = [
            FormData(
                nombre_completo="Dr. Ana García López",
                correo_institucional="ana.garcia@universidad.edu.mx",
                cursos_capacitacion=[
                    CursoCapacitacionBase(
                        nombre_curso="Machine Learning Avanzado",
                        fecha=date(2024, 2, 15),
                        horas=40
                    ),
                    CursoCapacitacionBase(
                        nombre_curso="Metodologías Ágiles",
                        fecha=date(2024, 4, 10),
                        horas=20
                    )
                ],
                publicaciones=[
                    PublicacionBase(
                        autores="Ana García, Carlos Ruiz",
                        titulo="Deep Learning Applications in Education",
                        evento_revista="IEEE Transactions on Education",
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
                nombre_completo="Mtro. Carlos Ruiz Hernández",
                correo_institucional="carlos.ruiz@universidad.edu.mx",
                cursos_capacitacion=[
                    CursoCapacitacionBase(
                        nombre_curso="Inteligencia Artificial",
                        fecha=date(2024, 3, 20),
                        horas=35
                    )
                ],
                publicaciones=[
                    PublicacionBase(
                        autores="Carlos Ruiz, Ana García",
                        titulo="AI in Higher Education",
                        evento_revista="Computers & Education",
                        estatus="PUBLICADO"
                    )
                ],
                eventos_academicos=[],
                diseno_curricular=[],
                movilidad=[],
                reconocimientos=[],
                certificaciones=[]
            ),
            FormData(
                nombre_completo="Dra. Ana García López",  # Potential duplicate
                correo_institucional="ana.garcia@universidad.edu.mx",
                cursos_capacitacion=[
                    CursoCapacitacionBase(
                        nombre_curso="Python para Data Science",
                        fecha=date(2024, 5, 5),
                        horas=25
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
        
        form_ids = []
        for form_data in test_forms:
            db_form = crud.create_formulario(form_data)
            form_ids.append(db_form.id)
            
            # Approve the forms for testing
            crud.aprobar_formulario(db_form.id, "test_admin")
        
        print(f"✅ Created {len(form_ids)} test forms: {form_ids}")
        return form_ids
        
    finally:
        db.close()

def test_data_processor():
    """Test the data processor functionality"""
    print("Testing DataProcessor...")
    
    db = SessionLocal()
    try:
        processor = DataProcessor(db)
        
        # Get raw data from database
        crud = FormularioCRUD(db)
        formularios = crud.get_all_formularios(limit=100)
        
        # Convert to list of dicts for processing
        raw_data = []
        for form in formularios:
            raw_data.append({
                'id': form.id,
                'nombre_completo': form.nombre_completo,
                'correo_institucional': form.correo_institucional,
                'estado': form.estado.value,
                'fecha_envio': form.fecha_envio,
                'fecha_revision': form.fecha_revision
            })
        
        print(f"Processing {len(raw_data)} records...")
        
        # Test data cleaning
        cleaned_df = processor.clean_data(raw_data)
        print(f"✅ Data cleaning completed. Shape: {cleaned_df.shape}")
        print(f"   Columns: {list(cleaned_df.columns)}")
        
        # Test duplicate detection
        df_with_duplicates = processor.detect_duplicates(cleaned_df)
        duplicates_found = df_with_duplicates['is_duplicate'].sum() if 'is_duplicate' in df_with_duplicates.columns else 0
        print(f"✅ Duplicate detection completed. Found {duplicates_found} potential duplicates")
        
        # Test metrics calculation
        metrics = processor.calculate_metrics(df_with_duplicates, 'current_year')
        print(f"✅ Metrics calculation completed:")
        print(f"   Total formularios: {metrics['total_formularios']}")
        print(f"   Duplicados detectados: {metrics['duplicados_detectados']}")
        
        # Test statistics generation
        stats = processor.generate_statistics(df_with_duplicates)
        print(f"✅ Statistics generation completed:")
        print(f"   Sections generated: {list(stats.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ DataProcessor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_metrics_calculator():
    """Test the metrics calculator functionality"""
    print("\nTesting MetricsCalculator...")
    
    db = SessionLocal()
    try:
        calculator = MetricsCalculator(db)
        
        # Create a sample DataFrame for testing
        import pandas as pd
        sample_data = pd.DataFrame([
            {
                'id': 1,
                'nombre_completo': 'Dr. Test',
                'estado': 'APROBADO',
                'year': 2024,
                'quarter': 2,
                'fecha_envio': datetime(2024, 4, 15)
            },
            {
                'id': 2,
                'nombre_completo': 'Dra. Test2',
                'estado': 'APROBADO',
                'year': 2024,
                'quarter': 2,
                'fecha_envio': datetime(2024, 5, 20)
            }
        ])
        
        # Test quarterly metrics
        quarterly_metrics = calculator.calculate_quarterly_metrics(sample_data, 2, 2024)
        print(f"✅ Quarterly metrics calculated:")
        print(f"   Periodo: {quarterly_metrics['periodo']}")
        print(f"   Formularios procesados: {quarterly_metrics['formularios_procesados']}")
        
        # Test annual metrics
        annual_metrics = calculator.calculate_annual_metrics(sample_data, 2024)
        print(f"✅ Annual metrics calculated:")
        print(f"   Año: {annual_metrics['año']}")
        print(f"   Formularios procesados: {annual_metrics['formularios_procesados']}")
        
        # Test productivity metrics
        detailed_data = {
            'formularios': 2,
            'cursos': {'total': 5, 'total_horas': 100},
            'publicaciones': {'total': 3, 'por_estatus': {'ACEPTADO': 2, 'PUBLICADO': 1}},
            'eventos': {'total': 4, 'por_tipo': {'ORGANIZADOR': 2, 'PARTICIPANTE': 2}}
        }
        
        productivity = calculator.calculate_productivity_metrics(detailed_data)
        print(f"✅ Productivity metrics calculated:")
        print(f"   Cursos por docente: {productivity['eficiencia_capacitacion']['cursos_por_docente']}")
        print(f"   Publicaciones por docente: {productivity['productividad_investigacion']['publicaciones_por_docente']}")
        
        # Test performance indicators
        kpis = calculator.generate_performance_indicators(detailed_data)
        print(f"✅ Performance indicators calculated:")
        print(f"   Indicadores principales: {len(kpis['indicadores_principales'])}")
        print(f"   Áreas de fortaleza: {kpis['areas_fortaleza']}")
        
        return True
        
    except Exception as e:
        print(f"❌ MetricsCalculator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_integration():
    """Test integration between components"""
    print("\nTesting integration...")
    
    db = SessionLocal()
    try:
        processor = DataProcessor(db)
        calculator = MetricsCalculator(db)
        
        # Get data from database
        crud = FormularioCRUD(db)
        formularios = crud.get_all_formularios(limit=10)
        
        if not formularios:
            print("⚠️  No data available for integration test")
            return True
        
        # Process data
        raw_data = [{
            'id': f.id,
            'nombre_completo': f.nombre_completo,
            'correo_institucional': f.correo_institucional,
            'estado': f.estado.value,
            'fecha_envio': f.fecha_envio,
            'year': f.fecha_envio.year,
            'quarter': (f.fecha_envio.month - 1) // 3 + 1
        } for f in formularios]
        
        # Clean and process
        df = processor.clean_data(raw_data)
        df = processor.detect_duplicates(df)
        
        # Calculate metrics
        metrics = processor.calculate_metrics(df)
        stats = processor.generate_statistics(df)
        
        # Use calculator for advanced metrics
        current_year = datetime.now().year
        annual_metrics = calculator.calculate_annual_metrics(df, current_year)
        
        print(f"✅ Integration test completed:")
        print(f"   Processed {len(df)} records")
        print(f"   Generated {len(metrics)} metric categories")
        print(f"   Generated {len(stats)} statistic categories")
        print(f"   Annual metrics for {current_year}: {len(annual_metrics)} sections")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def main():
    """Main test function"""
    print("🧪 Testing Data Processing Engine")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    # Create test data
    try:
        create_test_data()
        tests_passed += 1
        print("✅ Test data creation: PASSED")
    except Exception as e:
        print(f"❌ Test data creation: FAILED - {e}")
    
    # Test DataProcessor
    if test_data_processor():
        tests_passed += 1
        print("✅ DataProcessor: PASSED")
    else:
        print("❌ DataProcessor: FAILED")
    
    # Test MetricsCalculator
    if test_metrics_calculator():
        tests_passed += 1
        print("✅ MetricsCalculator: PASSED")
    else:
        print("❌ MetricsCalculator: FAILED")
    
    # Test Integration
    if test_integration():
        tests_passed += 1
        print("✅ Integration: PASSED")
    else:
        print("❌ Integration: FAILED")
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ All data processing tests passed!")
    else:
        print("❌ Some data processing tests failed!")

if __name__ == "__main__":
    main()