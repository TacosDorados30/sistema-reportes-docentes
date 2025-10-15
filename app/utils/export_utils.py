"""
Utilidades de Exportación
Funciones para exportar datos del sistema en diferentes formatos
"""

import pandas as pd
from io import BytesIO, StringIO
import json
import zipfile
from datetime import datetime
from typing import List, Dict, Any, Optional
import streamlit as st
from app.utils.report_generator import ReportGenerator
from app.utils.report_history import ReportHistory


class DataExporter:
    """Clase principal para exportación de datos"""
    
    def __init__(self):
        self.report_generator = ReportGenerator()
        self.report_history = ReportHistory()
    
    def export_to_excel(self, forms: List, filename: str = "export.xlsx", 
                       include_charts: bool = True, include_metadata: bool = True) -> BytesIO:
        """Exporta formularios a Excel con múltiples hojas"""
        try:
            buffer = self.report_generator.generate_excel_report(forms, filename)
            
            # Registrar en historial
            self.report_history.add_report({
                'tipo': 'exportacion_excel',
                'formato': 'excel',
                'total_registros': len(forms),
                'nombre_archivo': filename,
                'tamaño_archivo': len(buffer.getvalue()),
                'descripcion': f'Exportación Excel de {len(forms)} formularios'
            })
            
            return buffer
            
        except Exception as e:
            st.error(f"Error exportando a Excel: {e}")
            return None
    
    def export_to_csv(self, forms: List, filename: str = "export.csv", 
                     encoding: str = "utf-8") -> str:
        """Exporta formularios a CSV"""
        try:
            data = []
            for form in forms:
                data.append({
                    'ID': form.id,
                    'Nombre_Completo': form.nombre_completo,
                    'Correo_Institucional': form.correo_institucional,
                    'Estado': form.estado.value,
                    'Fecha_Envio': form.fecha_envio.strftime('%Y-%m-%d %H:%M') if form.fecha_envio else '',
                    'Fecha_Revision': form.fecha_revision.strftime('%Y-%m-%d %H:%M') if form.fecha_revision else '',
                    'Revisado_Por': form.revisado_por or ''
                })
            
            df = pd.DataFrame(data)
            csv_content = df.to_csv(index=False, encoding=encoding)
            
            # Registrar en historial
            self.report_history.add_report({
                'tipo': 'exportacion_csv',
                'formato': 'csv',
                'total_registros': len(forms),
                'nombre_archivo': filename,
                'tamaño_archivo': len(csv_content.encode(encoding)),
                'descripcion': f'Exportación CSV de {len(forms)} formularios'
            })
            
            return csv_content
            
        except Exception as e:
            st.error(f"Error exportando a CSV: {e}")
            return None
    
    def export_to_json(self, forms: List, filename: str = "export.json", 
                      include_metadata: bool = True) -> str:
        """Exporta formularios a JSON"""
        try:
            # Generar reporte completo
            report = self.report_generator.generate_comprehensive_report(forms, include_charts=False)
            
            # Añadir datos detallados de formularios
            forms_data = []
            for form in forms:
                form_dict = {
                    'id': form.id,
                    'nombre_completo': form.nombre_completo,
                    'correo_institucional': form.correo_institucional,
                    'estado': form.estado.value,
                    'fecha_envio': form.fecha_envio.isoformat() if form.fecha_envio else None,
                    'fecha_revision': form.fecha_revision.isoformat() if form.fecha_revision else None,
                    'revisado_por': form.revisado_por
                }
                forms_data.append(form_dict)
            
            export_data = {
                'metadata': report['metadata'] if include_metadata else {},
                'formularios': forms_data,
                'estadisticas': report.get('estadisticas_generales', {}) if include_metadata else {}
            }
            
            json_content = json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
            
            # Registrar en historial
            self.report_history.add_report({
                'tipo': 'exportacion_json',
                'formato': 'json',
                'total_registros': len(forms),
                'nombre_archivo': filename,
                'tamaño_archivo': len(json_content.encode('utf-8')),
                'descripcion': f'Exportación JSON de {len(forms)} formularios'
            })
            
            return json_content
            
        except Exception as e:
            st.error(f"Error exportando a JSON: {e}")
            return None
    
    def export_complete_package(self, forms: List, base_filename: str = "paquete_completo") -> BytesIO:
        """Exporta un paquete completo con múltiples formatos"""
        try:
            buffer = BytesIO()
            
            with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Excel
                excel_buffer = self.export_to_excel(forms, f"{base_filename}.xlsx")
                if excel_buffer:
                    zip_file.writestr(f"{base_filename}.xlsx", excel_buffer.getvalue())
                
                # CSV
                csv_content = self.export_to_csv(forms, f"{base_filename}.csv")
                if csv_content:
                    zip_file.writestr(f"{base_filename}.csv", csv_content.encode('utf-8'))
                
                # JSON
                json_content = self.export_to_json(forms, f"{base_filename}.json")
                if json_content:
                    zip_file.writestr(f"{base_filename}.json", json_content.encode('utf-8'))
                
                # README
                readme_content = self._generate_readme(forms)
                zip_file.writestr("README.txt", readme_content.encode('utf-8'))
            
            buffer.seek(0)
            
            # Registrar en historial
            self.report_history.add_report({
                'tipo': 'paquete_completo',
                'formato': 'zip',
                'total_registros': len(forms),
                'nombre_archivo': f"{base_filename}.zip",
                'tamaño_archivo': len(buffer.getvalue()),
                'descripcion': f'Paquete completo de {len(forms)} formularios'
            })
            
            return buffer
            
        except Exception as e:
            st.error(f"Error creando paquete completo: {e}")
            return None
    
    def _generate_readme(self, forms: List) -> str:
        """Genera archivo README para el paquete"""
        stats = self.report_generator._calculate_general_stats(forms)
        
        readme = f"""
PAQUETE DE EXPORTACIÓN - SISTEMA DE INFORMES DOCENTES
====================================================

Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total de formularios: {len(forms)}

CONTENIDO DEL PAQUETE:
---------------------
- Excel (.xlsx): Reporte completo con múltiples hojas y estadísticas
- CSV (.csv): Datos básicos en formato de valores separados por comas
- JSON (.json): Datos estructurados con metadatos completos

ESTADÍSTICAS GENERALES:
----------------------
- Formularios aprobados: {stats['formularios_aprobados']}
- Formularios pendientes: {stats['formularios_pendientes']}
- Formularios rechazados: {stats['formularios_rechazados']}
- Total de actividades: {stats['total_actividades']}
- Promedio de actividades por docente: {stats['promedio_actividades_por_docente']}

DESCRIPCIÓN DE ARCHIVOS:
-----------------------

1. ARCHIVO EXCEL:
   - Hoja "Resumen Ejecutivo": Métricas principales del sistema
   - Hoja "Formularios": Datos básicos de todos los formularios
   - Hoja "Cursos": Detalle de cursos de capacitación
   - Hoja "Publicaciones": Detalle de publicaciones académicas
   - Hoja "Eventos": Detalle de eventos académicos
   - Hoja "Estadísticas": Estadísticas detalladas por categoría

2. ARCHIVO CSV:
   - Formato simple compatible con Excel y otras herramientas
   - Codificación UTF-8
   - Separador: coma (,)

3. ARCHIVO JSON:
   - Estructura completa de datos
   - Incluye metadatos y estadísticas
   - Formato estándar para integración con otros sistemas

NOTAS IMPORTANTES:
-----------------
- Los datos están filtrados según los criterios seleccionados al momento de la exportación
- Las fechas están en formato ISO (YYYY-MM-DD HH:MM:SS)
- Los archivos mantienen la integridad referencial de los datos originales

Para soporte técnico o consultas sobre este paquete, contacte al administrador del sistema.
        """
        
        return readme.strip()
    
    def get_export_history(self) -> ReportHistory:
        """Obtiene el historial de exportaciones"""
        return self.report_history


# Funciones de compatibilidad para mantener la API existente
def export_forms_to_excel(forms: List, filename: str = "export.xlsx") -> BytesIO:
    """Función de compatibilidad para exportar a Excel"""
    exporter = DataExporter()
    return exporter.export_to_excel(forms, filename)


def export_forms_to_csv(forms: List, filename: str = "export.csv") -> str:
    """Función de compatibilidad para exportar a CSV"""
    exporter = DataExporter()
    return exporter.export_to_csv(forms, filename)