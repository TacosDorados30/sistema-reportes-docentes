"""
Generador de Reportes Avanzados
Genera reportes detallados del sistema con gráficos y estadísticas
"""

import pandas as pd
from datetime import datetime, timedelta
import json
from io import BytesIO, StringIO
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from typing import List, Dict, Any, Optional
from app.database.connection import SessionLocal
from app.database.crud import FormularioCRUD
from app.models.database import EstadoFormularioEnum


class ReportGenerator:
    """Generador de reportes avanzados del sistema"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.crud = FormularioCRUD(self.db)
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()
    
    def generate_comprehensive_report(self, forms: List, include_charts: bool = True) -> Dict[str, Any]:
        """Genera un reporte completo del sistema"""
        
        report = {
            'metadata': {
                'fecha_generacion': datetime.now().isoformat(),
                'total_formularios': len(forms),
                'periodo_analizado': self._get_period_info(forms)
            },
            'estadisticas_generales': self._calculate_general_stats(forms),
            'distribucion_estados': self._calculate_status_distribution(forms),
            'actividades_por_tipo': self._calculate_activities_by_type(forms),
            'tendencias_temporales': self._calculate_temporal_trends(forms),
            'top_docentes': self._get_top_teachers(forms),
            'metricas_calidad': self._calculate_quality_metrics(forms)
        }
        
        if include_charts:
            report['graficos'] = self._generate_charts(forms)
        
        return report
    
    def generate_excel_report(self, forms: List, filename: str = "reporte_completo.xlsx") -> BytesIO:
        """Genera un reporte completo en Excel con múltiples hojas"""
        
        buffer = BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Hoja 1: Resumen ejecutivo
            summary_df = self._create_summary_dataframe(forms)
            summary_df.to_excel(writer, sheet_name='Resumen Ejecutivo', index=False)
            
            # Hoja 2: Datos principales
            main_df = self._create_main_dataframe(forms)
            main_df.to_excel(writer, sheet_name='Formularios', index=False)
            
            # Hoja 3: Cursos de capacitación
            courses_df = self._create_courses_dataframe(forms)
            if not courses_df.empty:
                courses_df.to_excel(writer, sheet_name='Cursos', index=False)
            
            # Hoja 4: Publicaciones
            publications_df = self._create_publications_dataframe(forms)
            if not publications_df.empty:
                publications_df.to_excel(writer, sheet_name='Publicaciones', index=False)
            
            # Hoja 5: Eventos académicos
            events_df = self._create_events_dataframe(forms)
            if not events_df.empty:
                events_df.to_excel(writer, sheet_name='Eventos', index=False)
            
            # Hoja 6: Estadísticas
            stats_df = self._create_statistics_dataframe(forms)
            stats_df.to_excel(writer, sheet_name='Estadísticas', index=False)
        
        buffer.seek(0)
        return buffer
    
    def _get_period_info(self, forms: List) -> Dict[str, str]:
        """Obtiene información del período analizado"""
        if not forms:
            return {}
        
        dates = [f.fecha_envio for f in forms if f.fecha_envio]
        if not dates:
            return {}
        
        return {
            'fecha_inicio': min(dates).isoformat(),
            'fecha_fin': max(dates).isoformat(),
            'dias_analizados': (max(dates) - min(dates)).days
        }
    
    def _calculate_general_stats(self, forms: List) -> Dict[str, int]:
        """Calcula estadísticas generales"""
        approved_forms = [f for f in forms if f.estado.value == 'APROBADO']
        
        total_activities = 0
        for form in approved_forms:
            try:
                fresh_form = self.crud.get_formulario(form.id)
                if fresh_form:
                    total_activities += (
                        len(fresh_form.cursos_capacitacion or []) +
                        len(fresh_form.publicaciones or []) +
                        len(fresh_form.eventos_academicos or []) +
                        len(fresh_form.diseno_curricular or []) +
                        len(fresh_form.experiencias_movilidad or []) +
                        len(fresh_form.reconocimientos or []) +
                        len(fresh_form.certificaciones or [])
                    )
            except:
                continue
        
        return {
            'total_formularios': len(forms),
            'formularios_aprobados': len(approved_forms),
            'formularios_pendientes': len([f for f in forms if f.estado.value == 'PENDIENTE']),
            'formularios_rechazados': len([f for f in forms if f.estado.value == 'RECHAZADO']),
            'total_actividades': total_activities,
            'promedio_actividades_por_docente': round(total_activities / len(approved_forms), 2) if approved_forms else 0
        }
    
    def _calculate_status_distribution(self, forms: List) -> Dict[str, int]:
        """Calcula la distribución por estados"""
        distribution = {}
        for form in forms:
            status = form.estado.value
            distribution[status] = distribution.get(status, 0) + 1
        return distribution
    
    def _calculate_activities_by_type(self, forms: List) -> Dict[str, int]:
        """Calcula actividades por tipo"""
        activities = {
            'cursos_capacitacion': 0,
            'publicaciones': 0,
            'eventos_academicos': 0,
            'diseno_curricular': 0,
            'experiencias_movilidad': 0,
            'reconocimientos': 0,
            'certificaciones': 0
        }
        
        approved_forms = [f for f in forms if f.estado.value == 'APROBADO']
        
        for form in approved_forms:
            try:
                fresh_form = self.crud.get_formulario(form.id)
                if fresh_form:
                    activities['cursos_capacitacion'] += len(fresh_form.cursos_capacitacion or [])
                    activities['publicaciones'] += len(fresh_form.publicaciones or [])
                    activities['eventos_academicos'] += len(fresh_form.eventos_academicos or [])
                    activities['diseno_curricular'] += len(fresh_form.diseno_curricular or [])
                    activities['experiencias_movilidad'] += len(fresh_form.experiencias_movilidad or [])
                    activities['reconocimientos'] += len(fresh_form.reconocimientos or [])
                    activities['certificaciones'] += len(fresh_form.certificaciones or [])
            except:
                continue
        
        return activities
    
    def _calculate_temporal_trends(self, forms: List) -> Dict[str, Any]:
        """Calcula tendencias temporales"""
        if not forms:
            return {}
        
        # Agrupar por mes
        monthly_data = {}
        for form in forms:
            if form.fecha_envio:
                month_key = form.fecha_envio.strftime('%Y-%m')
                if month_key not in monthly_data:
                    monthly_data[month_key] = {'total': 0, 'aprobados': 0}
                monthly_data[month_key]['total'] += 1
                if form.estado.value == 'APROBADO':
                    monthly_data[month_key]['aprobados'] += 1
        
        return monthly_data
    
    def _get_top_teachers(self, forms: List, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtiene los docentes más activos"""
        approved_forms = [f for f in forms if f.estado.value == 'APROBADO']
        teacher_stats = {}
        
        for form in approved_forms:
            try:
                fresh_form = self.crud.get_formulario(form.id)
                if fresh_form:
                    total_activities = (
                        len(fresh_form.cursos_capacitacion or []) +
                        len(fresh_form.publicaciones or []) +
                        len(fresh_form.eventos_academicos or []) +
                        len(fresh_form.diseno_curricular or []) +
                        len(fresh_form.experiencias_movilidad or []) +
                        len(fresh_form.reconocimientos or []) +
                        len(fresh_form.certificaciones or [])
                    )
                    
                    teacher_stats[form.nombre_completo] = {
                        'nombre': form.nombre_completo,
                        'email': form.correo_institucional,
                        'total_actividades': total_activities,
                        'fecha_envio': form.fecha_envio.isoformat() if form.fecha_envio else None
                    }
            except:
                continue
        
        # Ordenar por total de actividades
        sorted_teachers = sorted(teacher_stats.values(), 
                               key=lambda x: x['total_actividades'], 
                               reverse=True)
        
        return sorted_teachers[:limit]
    
    def _calculate_quality_metrics(self, forms: List) -> Dict[str, float]:
        """Calcula métricas de calidad"""
        if not forms:
            return {}
        
        total_forms = len(forms)
        approved_forms = len([f for f in forms if f.estado.value == 'APROBADO'])
        rejected_forms = len([f for f in forms if f.estado.value == 'RECHAZADO'])
        
        # Calcular tiempo promedio de procesamiento
        processing_times = []
        for form in forms:
            if form.fecha_revision and form.fecha_envio:
                processing_time = (form.fecha_revision - form.fecha_envio).days
                processing_times.append(processing_time)
        
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        return {
            'tasa_aprobacion': round((approved_forms / total_forms) * 100, 2) if total_forms > 0 else 0,
            'tasa_rechazo': round((rejected_forms / total_forms) * 100, 2) if total_forms > 0 else 0,
            'tiempo_promedio_procesamiento_dias': round(avg_processing_time, 2),
            'formularios_con_actividades': len([f for f in forms if self._has_activities(f)]),
            'completitud_promedio': self._calculate_completeness(forms)
        }
    
    def _has_activities(self, form) -> bool:
        """Verifica si un formulario tiene actividades"""
        try:
            fresh_form = self.crud.get_formulario(form.id)
            if fresh_form:
                return (
                    len(fresh_form.cursos_capacitacion or []) > 0 or
                    len(fresh_form.publicaciones or []) > 0 or
                    len(fresh_form.eventos_academicos or []) > 0 or
                    len(fresh_form.diseno_curricular or []) > 0 or
                    len(fresh_form.experiencias_movilidad or []) > 0 or
                    len(fresh_form.reconocimientos or []) > 0 or
                    len(fresh_form.certificaciones or []) > 0
                )
        except:
            pass
        return False
    
    def _calculate_completeness(self, forms: List) -> float:
        """Calcula el porcentaje de completitud promedio"""
        if not forms:
            return 0.0
        
        total_completeness = 0
        for form in forms:
            fields_filled = 0
            total_fields = 3  # nombre, email, fecha_envio
            
            if form.nombre_completo:
                fields_filled += 1
            if form.correo_institucional:
                fields_filled += 1
            if form.fecha_envio:
                fields_filled += 1
            
            completeness = (fields_filled / total_fields) * 100
            total_completeness += completeness
        
        return round(total_completeness / len(forms), 2)
    
    def _generate_charts(self, forms: List) -> Dict[str, str]:
        """Genera gráficos para el reporte"""
        charts = {}
        
        # Gráfico de distribución de estados
        status_dist = self._calculate_status_distribution(forms)
        if status_dist:
            fig = px.pie(
                values=list(status_dist.values()),
                names=list(status_dist.keys()),
                title="Distribución de Estados de Formularios"
            )
            charts['distribucion_estados'] = fig.to_html()
        
        # Gráfico de actividades por tipo
        activities = self._calculate_activities_by_type(forms)
        if activities:
            fig = px.bar(
                x=list(activities.keys()),
                y=list(activities.values()),
                title="Actividades por Tipo"
            )
            fig.update_xaxis(tickangle=45)
            charts['actividades_por_tipo'] = fig.to_html()
        
        return charts
    
    def _create_summary_dataframe(self, forms: List) -> pd.DataFrame:
        """Crea DataFrame de resumen ejecutivo"""
        stats = self._calculate_general_stats(forms)
        quality = self._calculate_quality_metrics(forms)
        
        data = [
            ['Total de Formularios', stats['total_formularios']],
            ['Formularios Aprobados', stats['formularios_aprobados']],
            ['Formularios Pendientes', stats['formularios_pendientes']],
            ['Formularios Rechazados', stats['formularios_rechazados']],
            ['Total de Actividades', stats['total_actividades']],
            ['Promedio Actividades por Docente', stats['promedio_actividades_por_docente']],
            ['Tasa de Aprobación (%)', quality.get('tasa_aprobacion', 0)],
            ['Tiempo Promedio Procesamiento (días)', quality.get('tiempo_promedio_procesamiento_dias', 0)]
        ]
        
        return pd.DataFrame(data, columns=['Métrica', 'Valor'])
    
    def _create_main_dataframe(self, forms: List) -> pd.DataFrame:
        """Crea DataFrame principal con datos de formularios"""
        data = []
        for form in forms:
            data.append({
                'ID': form.id,
                'Nombre Completo': form.nombre_completo,
                'Correo Institucional': form.correo_institucional,
                'Estado': form.estado.value,
                'Fecha Envío': form.fecha_envio.strftime('%Y-%m-%d %H:%M') if form.fecha_envio else '',
                'Fecha Revisión': form.fecha_revision.strftime('%Y-%m-%d %H:%M') if form.fecha_revision else '',
                'Revisado Por': form.revisado_por or ''
            })
        
        return pd.DataFrame(data)
    
    def _create_courses_dataframe(self, forms: List) -> pd.DataFrame:
        """Crea DataFrame de cursos de capacitación"""
        data = []
        for form in forms:
            try:
                fresh_form = self.crud.get_formulario(form.id)
                if fresh_form and fresh_form.cursos_capacitacion:
                    for curso in fresh_form.cursos_capacitacion:
                        data.append({
                            'Formulario ID': form.id,
                            'Docente': form.nombre_completo,
                            'Nombre Curso': curso.nombre_curso,
                            'Fecha': curso.fecha,
                            'Horas': curso.horas
                        })
            except:
                continue
        
        return pd.DataFrame(data)
    
    def _create_publications_dataframe(self, forms: List) -> pd.DataFrame:
        """Crea DataFrame de publicaciones"""
        data = []
        for form in forms:
            try:
                fresh_form = self.crud.get_formulario(form.id)
                if fresh_form and fresh_form.publicaciones:
                    for pub in fresh_form.publicaciones:
                        data.append({
                            'Formulario ID': form.id,
                            'Docente': form.nombre_completo,
                            'Autores': pub.autores,
                            'Título': pub.titulo,
                            'Evento/Revista': pub.evento_revista,
                            'Estatus': pub.estatus.value
                        })
            except:
                continue
        
        return pd.DataFrame(data)
    
    def _create_events_dataframe(self, forms: List) -> pd.DataFrame:
        """Crea DataFrame de eventos académicos"""
        data = []
        for form in forms:
            try:
                fresh_form = self.crud.get_formulario(form.id)
                if fresh_form and fresh_form.eventos_academicos:
                    for evento in fresh_form.eventos_academicos:
                        data.append({
                            'Formulario ID': form.id,
                            'Docente': form.nombre_completo,
                            'Nombre Evento': evento.nombre_evento,
                            'Fecha': evento.fecha,
                            'Tipo Participación': evento.tipo_participacion.value
                        })
            except:
                continue
        
        return pd.DataFrame(data)
    
    def _create_statistics_dataframe(self, forms: List) -> pd.DataFrame:
        """Crea DataFrame de estadísticas detalladas"""
        activities = self._calculate_activities_by_type(forms)
        
        data = []
        for activity_type, count in activities.items():
            data.append({
                'Tipo de Actividad': activity_type.replace('_', ' ').title(),
                'Total': count
            })
        
        return pd.DataFrame(data)