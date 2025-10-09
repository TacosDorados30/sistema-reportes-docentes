"""
Export utilities for data export functionality
"""

import pandas as pd
from io import BytesIO, StringIO
from typing import List
from app.models.database import FormularioEnvioDB, EstadoFormularioEnum


def export_forms_to_excel(forms: List[FormularioEnvioDB]) -> bytes:
    """Export forms to Excel format"""
    try:
        # Create Excel file
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Main forms sheet
            forms_data = []
            for form in forms:
                forms_data.append({
                    'ID': form.id,
                    'Nombre': form.nombre_completo,
                    'Email': form.correo_institucional,
                    'Año Académico': getattr(form, 'año_academico', ''),
                    'Trimestre': getattr(form, 'trimestre', ''),
                    'Estado': form.estado.value,
                    'Fecha Envío': form.fecha_envio.strftime('%Y-%m-%d') if form.fecha_envio else '',
                    'Fecha Revisión': form.fecha_revision.strftime('%Y-%m-%d') if form.fecha_revision else '',
                    'Revisado Por': form.revisado_por or ''
                })
            
            if forms_data:
                forms_df = pd.DataFrame(forms_data)
                forms_df.to_excel(writer, sheet_name='Formularios', index=False)
            
            # Courses sheet
            courses_data = []
            for form in forms:
                for curso in form.cursos_capacitacion or []:
                    courses_data.append({
                        'Formulario ID': form.id,
                        'Docente': form.nombre_completo,
                        'Curso': curso.nombre_curso,
                        'Fecha': curso.fecha.strftime('%Y-%m-%d') if curso.fecha else '',
                        'Horas': curso.horas
                    })
            
            if courses_data:
                courses_df = pd.DataFrame(courses_data)
                courses_df.to_excel(writer, sheet_name='Cursos', index=False)
            
            # Publications sheet
            pubs_data = []
            for form in forms:
                for pub in form.publicaciones or []:
                    pubs_data.append({
                        'Formulario ID': form.id,
                        'Docente': form.nombre_completo,
                        'Autores': pub.autores,
                        'Título': pub.titulo,
                        'Evento/Revista': pub.evento_revista,
                        'Estatus': pub.estatus.value if hasattr(pub.estatus, 'value') else str(pub.estatus)
                    })
            
            if pubs_data:
                pubs_df = pd.DataFrame(pubs_data)
                pubs_df.to_excel(writer, sheet_name='Publicaciones', index=False)
        
        output.seek(0)
        return output.getvalue()
        
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        return b""


def export_forms_to_csv(forms: List[FormularioEnvioDB]) -> str:
    """Export forms to CSV format"""
    try:
        # Create comprehensive data
        all_data = []
        for form in forms:
            base_data = {
                'formulario_id': form.id,
                'nombre_completo': form.nombre_completo,
                'correo_institucional': form.correo_institucional,
                'año_academico': getattr(form, 'año_academico', ''),
                'trimestre': getattr(form, 'trimestre', ''),
                'estado': form.estado.value,
                'fecha_envio': form.fecha_envio.strftime('%Y-%m-%d') if form.fecha_envio else '',
                'fecha_revision': form.fecha_revision.strftime('%Y-%m-%d') if form.fecha_revision else '',
                'revisado_por': form.revisado_por or ''
            }
            
            # Add activity counts
            base_data.update({
                'total_cursos': len(form.cursos_capacitacion or []),
                'total_publicaciones': len(form.publicaciones or []),
                'total_eventos': len(form.eventos_academicos or []),
                'total_disenos': len(form.diseno_curricular or []),
                'total_movilidades': len(form.movilidad or []),
                'total_reconocimientos': len(form.reconocimientos or []),
                'total_certificaciones': len(form.certificaciones or [])
            })
            
            all_data.append(base_data)
        
        if all_data:
            df = pd.DataFrame(all_data)
            output = StringIO()
            df.to_csv(output, index=False, encoding='utf-8')
            return output.getvalue()
        else:
            return "No data available"
        
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return ""