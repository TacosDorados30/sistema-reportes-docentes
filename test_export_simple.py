#!/usr/bin/env python3
"""
Simple test for export functionality without database dependencies
"""

import sys
import os
from datetime import datetime, date
from io import BytesIO

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.export_utils import DataExporter

def test_export_basic_functionality():
    """Test basic export functionality with sample data"""
    
    print("🧪 Testing Basic Export Functionality")
    print("=" * 50)
    
    # Initialize exporter
    exporter = DataExporter()
    
    # Create sample data
    sample_data = [
        {
            'ID': 1,
            'Nombre': 'Dr. Juan Pérez',
            'Email': 'juan.perez@universidad.edu.mx',
            'Estado': 'APROBADO',
            'Fecha_Envio': '2024-03-15',
            'Total_Cursos': 3,
            'Total_Publicaciones': 2,
            'Total_Eventos': 1
        },
        {
            'ID': 2,
            'Nombre': 'Dra. María García',
            'Email': 'maria.garcia@universidad.edu.mx',
            'Estado': 'PENDIENTE',
            'Fecha_Envio': '2024-03-16',
            'Total_Cursos': 2,
            'Total_Publicaciones': 1,
            'Total_Eventos': 3
        },
        {
            'ID': 3,
            'Nombre': 'Dr. Carlos López',
            'Email': 'carlos.lopez@universidad.edu.mx',
            'Estado': 'APROBADO',
            'Fecha_Envio': '2024-03-17',
            'Total_Cursos': 4,
            'Total_Publicaciones': 3,
            'Total_Eventos': 2
        }
    ]
    
    # Test 1: CSV Export
    print("\n1. Testing CSV Export...")
    try:
        csv_content = exporter.export_to_csv(sample_data)
        
        if csv_content and len(csv_content) > 0:
            print("✅ CSV export successful")
            print(f"   Content length: {len(csv_content)} characters")
            print(f"   Lines: {csv_content.count(chr(10)) + 1}")
            
            # Verify CSV structure
            lines = csv_content.strip().split('\n')
            if len(lines) >= 2:  # Header + at least one data row
                header = lines[0]
                print(f"   Header: {header}")
                print(f"   Sample row: {lines[1]}")
            
            # Test with filtering
            filtered_data = [d for d in sample_data if d['Estado'] == 'APROBADO']
            filtered_csv = exporter.export_to_csv(filtered_data)
            print(f"   Filtered CSV (APROBADO only): {filtered_csv.count(chr(10))} lines")
            
        else:
            print("❌ CSV export failed - empty content")
    
    except Exception as e:
        print(f"❌ CSV export failed: {e}")
    
    # Test 2: Excel Export Structure
    print("\n2. Testing Excel Export Structure...")
    try:
        # Create multi-sheet data structure
        excel_data = {
            'summary': [
                {'Métrica': 'Total Formularios', 'Valor': 3},
                {'Métrica': 'Formularios Aprobados', 'Valor': 2},
                {'Métrica': 'Formularios Pendientes', 'Valor': 1},
                {'Métrica': 'Tasa de Aprobación (%)', 'Valor': 66.67}
            ],
            'formularios': sample_data,
            'cursos': [
                {'Formulario_ID': 1, 'Docente': 'Dr. Juan Pérez', 'Curso': 'Python Avanzado', 'Horas': 40},
                {'Formulario_ID': 1, 'Docente': 'Dr. Juan Pérez', 'Curso': 'Machine Learning', 'Horas': 60},
                {'Formulario_ID': 2, 'Docente': 'Dra. María García', 'Curso': 'Estadística', 'Horas': 30}
            ],
            'publicaciones': [
                {'Formulario_ID': 1, 'Docente': 'Dr. Juan Pérez', 'Título': 'AI in Education', 'Estatus': 'PUBLICADO'},
                {'Formulario_ID': 2, 'Docente': 'Dra. María García', 'Título': 'Data Science Methods', 'Estatus': 'ACEPTADO'}
            ]
        }
        
        excel_content = exporter.export_to_excel(excel_data, include_charts=False)
        
        if excel_content and len(excel_content.getvalue()) > 0:
            print("✅ Excel export successful")
            print(f"   Content size: {len(excel_content.getvalue())} bytes")
            print(f"   Sheets created: {len(excel_data)} sheets")
            
            # List sheets that would be created
            for sheet_name, sheet_data in excel_data.items():
                print(f"   - {sheet_name}: {len(sheet_data)} records")
        else:
            print("❌ Excel export failed - empty content")
    
    except Exception as e:
        print(f"❌ Excel export failed: {e}")
    
    # Test 3: JSON Export
    print("\n3. Testing JSON Export...")
    try:
        # Test simple JSON export
        json_content = exporter.export_to_json(sample_data, pretty=True)
        
        if json_content and len(json_content) > 0:
            print("✅ JSON export successful")
            print(f"   Content length: {len(json_content)} characters")
            print(f"   Pretty formatted: {json_content.count(chr(10))} lines")
            
            # Test compact JSON
            compact_json = exporter.export_to_json(sample_data, pretty=False)
            print(f"   Compact format: {len(compact_json)} characters")
            
        else:
            print("❌ JSON export failed - empty content")
    
    except Exception as e:
        print(f"❌ JSON export failed: {e}")
    
    # Test 4: Data Filtering and Metadata
    print("\n4. Testing Data Filtering and Metadata...")
    try:
        # Test filtering by status
        approved_only = [d for d in sample_data if d['Estado'] == 'APROBADO']
        pending_only = [d for d in sample_data if d['Estado'] == 'PENDIENTE']
        
        print(f"   Original data: {len(sample_data)} records")
        print(f"   Approved only: {len(approved_only)} records")
        print(f"   Pending only: {len(pending_only)} records")
        
        # Test metadata inclusion
        metadata_export = {
            'metadata': {
                'fecha_exportacion': datetime.now().isoformat(),
                'total_registros': len(sample_data),
                'filtros_aplicados': {
                    'estados': list(set(d['Estado'] for d in sample_data)),
                    'rango_fechas': {
                        'inicio': min(d['Fecha_Envio'] for d in sample_data),
                        'fin': max(d['Fecha_Envio'] for d in sample_data)
                    }
                },
                'version_sistema': '1.0',
                'generado_por': 'Sistema de Reportes Docentes'
            },
            'datos': sample_data
        }
        
        metadata_json = exporter.export_to_json(metadata_export, pretty=True)
        print(f"   Metadata export: {len(metadata_json)} characters")
        print("✅ Metadata and filtering successful")
        
    except Exception as e:
        print(f"❌ Metadata and filtering failed: {e}")
    
    # Test 5: File naming and timestamps
    print("\n5. Testing File Naming and Timestamps...")
    try:
        timestamp = exporter.timestamp
        print(f"   Generated timestamp: {timestamp}")
        
        # Test safe sheet names
        test_names = [
            "Cursos de Capacitación",
            "Diseños/Curriculares",
            "Eventos*Académicos",
            "Reconocimientos[2024]",
            "Certificaciones:Vigentes"
        ]
        
        for name in test_names:
            safe_name = exporter._safe_sheet_name(name)
            print(f"   '{name}' -> '{safe_name}'")
        
        print("✅ File naming and timestamps successful")
        
    except Exception as e:
        print(f"❌ File naming and timestamps failed: {e}")
    
    print(f"\n📈 Basic Export Testing Summary:")
    print(f"   - Sample records processed: {len(sample_data)}")
    print(f"   - Export formats tested: CSV, Excel, JSON")
    print(f"   - Features tested: Filtering, Metadata, File naming")
    print(f"   - Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_export_basic_functionality()