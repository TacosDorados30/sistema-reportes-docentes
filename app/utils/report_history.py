"""
Historial de Reportes
Gestiona el historial de reportes generados y permite su consulta
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import streamlit as st
from pathlib import Path


class ReportHistory:
    """Gestiona el historial de reportes generados"""
    
    def __init__(self, history_dir: str = "reports/history"):
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.history_dir / "report_history.json"
        self._ensure_history_file()
    
    def _ensure_history_file(self):
        """Asegura que el archivo de historial existe"""
        if not self.history_file.exists():
            self._save_history([])
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Carga el historial desde el archivo"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_history(self, history: List[Dict[str, Any]]):
        """Guarda el historial en el archivo"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            st.error(f"Error guardando historial: {e}")
    
    def add_report(self, report_info: Dict[str, Any]) -> str:
        """Añade un nuevo reporte al historial"""
        history = self._load_history()
        
        # Generar ID único
        report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Preparar información del reporte
        report_entry = {
            'id': report_id,
            'fecha_generacion': datetime.now().isoformat(),
            'tipo': report_info.get('tipo', 'general'),
            'formato': report_info.get('formato', 'excel'),
            'total_registros': report_info.get('total_registros', 0),
            'filtros_aplicados': report_info.get('filtros_aplicados', {}),
            'usuario': report_info.get('usuario', 'sistema'),
            'nombre_archivo': report_info.get('nombre_archivo', f"{report_id}.xlsx"),
            'tamaño_archivo': report_info.get('tamaño_archivo', 0),
            'estado': 'completado',
            'descripcion': report_info.get('descripcion', 'Reporte generado automáticamente')
        }
        
        # Añadir al historial
        history.insert(0, report_entry)  # Más recientes primero
        
        # Mantener solo los últimos 100 reportes
        if len(history) > 100:
            history = history[:100]
        
        self._save_history(history)
        return report_id
    
    def get_history(self, limit: Optional[int] = None, 
                   days_back: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtiene el historial de reportes con filtros opcionales"""
        history = self._load_history()
        
        # Filtrar por fecha si se especifica
        if days_back:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            history = [
                report for report in history
                if datetime.fromisoformat(report['fecha_generacion']) >= cutoff_date
            ]
        
        # Aplicar límite si se especifica
        if limit:
            history = history[:limit]
        
        return history
    
    def get_report_by_id(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un reporte específico por ID"""
        history = self._load_history()
        for report in history:
            if report['id'] == report_id:
                return report
        return None
    
    def delete_report(self, report_id: str) -> bool:
        """Elimina un reporte del historial"""
        history = self._load_history()
        original_length = len(history)
        
        history = [report for report in history if report['id'] != report_id]
        
        if len(history) < original_length:
            self._save_history(history)
            return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del historial de reportes"""
        history = self._load_history()
        
        if not history:
            return {
                'total_reportes': 0,
                'reportes_ultima_semana': 0,
                'reportes_ultimo_mes': 0,
                'tipos_mas_comunes': {},
                'formatos_mas_comunes': {}
            }
        
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Contar reportes por período
        reportes_semana = sum(
            1 for report in history
            if datetime.fromisoformat(report['fecha_generacion']) >= week_ago
        )
        
        reportes_mes = sum(
            1 for report in history
            if datetime.fromisoformat(report['fecha_generacion']) >= month_ago
        )
        
        # Contar tipos y formatos
        tipos = {}
        formatos = {}
        
        for report in history:
            tipo = report.get('tipo', 'general')
            formato = report.get('formato', 'excel')
            
            tipos[tipo] = tipos.get(tipo, 0) + 1
            formatos[formato] = formatos.get(formato, 0) + 1
        
        return {
            'total_reportes': len(history),
            'reportes_ultima_semana': reportes_semana,
            'reportes_ultimo_mes': reportes_mes,
            'tipos_mas_comunes': dict(sorted(tipos.items(), key=lambda x: x[1], reverse=True)),
            'formatos_mas_comunes': dict(sorted(formatos.items(), key=lambda x: x[1], reverse=True)),
            'reporte_mas_reciente': history[0]['fecha_generacion'] if history else None
        }
    
    def cleanup_old_reports(self, days_to_keep: int = 90) -> int:
        """Limpia reportes antiguos del historial"""
        history = self._load_history()
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        original_count = len(history)
        history = [
            report for report in history
            if datetime.fromisoformat(report['fecha_generacion']) >= cutoff_date
        ]
        
        removed_count = original_count - len(history)
        
        if removed_count > 0:
            self._save_history(history)
        
        return removed_count
    
    def export_history(self) -> str:
        """Exporta el historial completo como JSON"""
        history = self._load_history()
        return json.dumps(history, indent=2, ensure_ascii=False, default=str)
    
    def show_history_interface(self):
        """Muestra la interfaz del historial en Streamlit"""
        st.subheader("📚 Historial de Reportes")
        
        # Estadísticas del historial
        stats = self.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Reportes", stats['total_reportes'])
        
        with col2:
            st.metric("Última Semana", stats['reportes_ultima_semana'])
        
        with col3:
            st.metric("Último Mes", stats['reportes_ultimo_mes'])
        
        with col4:
            if stats.get('reporte_mas_reciente'):
                fecha_reciente = datetime.fromisoformat(stats['reporte_mas_reciente'])
                st.metric("Más Reciente", fecha_reciente.strftime('%d/%m/%Y'))
            else:
                st.metric("Más Reciente", "N/A")
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            days_filter = st.selectbox(
                "Mostrar reportes de:",
                [("Todos", None), ("Última semana", 7), ("Último mes", 30), ("Últimos 3 meses", 90)],
                format_func=lambda x: x[0]
            )[1]
        
        with col2:
            limit_filter = st.selectbox(
                "Límite de resultados:",
                [("Todos", None), ("10 más recientes", 10), ("25 más recientes", 25), ("50 más recientes", 50)],
                format_func=lambda x: x[0]
            )[1]
        
        with col3:
            if st.button("🧹 Limpiar Antiguos", help="Eliminar reportes de más de 90 días"):
                removed = self.cleanup_old_reports()
                if removed > 0:
                    st.success(f"Se eliminaron {removed} reportes antiguos")
                else:
                    st.info("No hay reportes antiguos para eliminar")
        
        # Obtener y mostrar historial
        history = self.get_history(limit=limit_filter, days_back=days_filter)
        
        if not history:
            st.info("No hay reportes en el historial con los filtros seleccionados.")
            return
        
        # Mostrar tabla de historial
        st.subheader("📋 Lista de Reportes")
        
        for i, report in enumerate(history):
            with st.expander(f"📄 {report['id']} - {report.get('descripcion', 'Sin descripción')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Fecha:** {datetime.fromisoformat(report['fecha_generacion']).strftime('%d/%m/%Y %H:%M')}")
                    st.write(f"**Tipo:** {report.get('tipo', 'N/A')}")
                    st.write(f"**Formato:** {report.get('formato', 'N/A')}")
                    st.write(f"**Registros:** {report.get('total_registros', 0)}")
                
                with col2:
                    st.write(f"**Usuario:** {report.get('usuario', 'N/A')}")
                    st.write(f"**Estado:** {report.get('estado', 'N/A')}")
                    st.write(f"**Archivo:** {report.get('nombre_archivo', 'N/A')}")
                    
                    if report.get('tamaño_archivo'):
                        size_mb = report['tamaño_archivo'] / (1024 * 1024)
                        st.write(f"**Tamaño:** {size_mb:.2f} MB")
                
                # Mostrar filtros aplicados si existen
                if report.get('filtros_aplicados'):
                    st.write("**Filtros aplicados:**")
                    for key, value in report['filtros_aplicados'].items():
                        st.write(f"- {key}: {value}")
                
                # Botón para eliminar
                if st.button(f"🗑️ Eliminar", key=f"delete_{report['id']}"):
                    if self.delete_report(report['id']):
                        st.success("Reporte eliminado del historial")
                        st.rerun()
                    else:
                        st.error("Error al eliminar el reporte")
        
        # Mostrar estadísticas adicionales
        if stats['tipos_mas_comunes'] or stats['formatos_mas_comunes']:
            st.subheader("📊 Estadísticas de Uso")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if stats['tipos_mas_comunes']:
                    st.write("**Tipos más generados:**")
                    for tipo, count in list(stats['tipos_mas_comunes'].items())[:5]:
                        st.write(f"- {tipo}: {count}")
            
            with col2:
                if stats['formatos_mas_comunes']:
                    st.write("**Formatos más usados:**")
                    for formato, count in list(stats['formatos_mas_comunes'].items())[:5]:
                        st.write(f"- {formato}: {count}")
        
        # Opción para exportar historial
        if st.button("📤 Exportar Historial Completo"):
            history_json = self.export_history()
            st.download_button(
                label="💾 Descargar Historial JSON",
                data=history_json,
                file_name=f"historial_reportes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )