import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.connection import SessionLocal
from app.database.crud import FormularioCRUD
from app.models.database import EstadoFormularioEnum
from app.utils.export_utils import export_forms_to_excel, export_forms_to_csv, DataExporter
from dashboard.components.interactive_filters import InteractiveFilters

def show_data_export_page():
    """Enhanced data export page with advanced options"""
    
    # Require authentication
    from app.auth.streamlit_auth import auth
    if not auth.require_authentication():
        return
    
    st.title("📤 Exportación de Datos")
    st.markdown("Exporte datos del sistema en múltiples formatos con opciones avanzadas de filtrado.")
    
    # Initialize components
    exporter = DataExporter()
    filters = InteractiveFilters()
    
    # Load data
    try:
        all_forms, metrics = load_export_data()
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return
    
    if not all_forms:
        st.warning("No hay datos disponibles para exportar.")
        return
    
    # Sidebar filters
    st.sidebar.header("🎛️ Opciones de Exportación")
    
    # Export format selection
    export_formats = st.sidebar.multiselect(
        "Formatos de exportación:",
        ["CSV", "Excel", "JSON", "Paquete Completo"],
        default=["CSV"]
    )
    
    # Status filter
    status_options = ["TODOS", "APROBADO", "PENDIENTE", "RECHAZADO"]
    selected_statuses = st.sidebar.multiselect(
        "Filtrar por estado:",
        status_options,
        default=["APROBADO"]
    )
    
    # Date range filter
    min_date = min([f.fecha_envio for f in all_forms if f.fecha_envio])
    max_date = max([f.fecha_envio for f in all_forms if f.fecha_envio])
    
    date_range = st.sidebar.date_input(
        "Rango de fechas:",
        value=(min_date.date(), max_date.date()),
        min_value=min_date.date(),
        max_value=max_date.date()
    )
    
    # Advanced filtering options
    with st.sidebar.expander("🔍 Filtros Avanzados"):
        # Activity filters
        st.write("**Filtrar por actividades:**")
        min_activities = st.number_input(
            "Mínimo de actividades totales:",
            min_value=0,
            max_value=100,
            value=0,
            help="Incluir solo formularios con al menos N actividades"
        )
        
        has_courses = st.checkbox("Solo con cursos de capacitación")
        has_publications = st.checkbox("Solo con publicaciones")
        has_events = st.checkbox("Solo con eventos académicos")
        
        # Name and email filters
        st.write("**Filtros de texto:**")
        name_filter = st.text_input(
            "Filtrar por nombre (parcial):",
            placeholder="Ej: García, Juan"
        )
        
        email_domain = st.text_input(
            "Filtrar por dominio de email:",
            placeholder="Ej: universidad.edu.mx"
        )
    
    # Advanced options
    with st.sidebar.expander("⚙️ Opciones Avanzadas"):
        include_detailed = st.checkbox("Incluir datos detallados", value=True)
        include_charts = st.checkbox("Incluir gráficos (Excel)", value=True)
        include_metadata = st.checkbox("Incluir metadatos", value=True)
        
        # Custom filename
        custom_filename = st.text_input(
            "Nombre personalizado (opcional):",
            placeholder="mi_exportacion"
        )
        
        # Export quality options
        st.write("**Opciones de calidad:**")
        csv_encoding = st.selectbox(
            "Codificación CSV:",
            ["UTF-8 con BOM", "UTF-8", "Latin-1"],
            help="UTF-8 con BOM es recomendado para Excel"
        )
    
    # Filter data based on selections
    filtered_forms = filter_forms_for_export(
        all_forms, selected_statuses, date_range,
        min_activities, has_courses, has_publications, has_events,
        name_filter, email_domain
    )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col2:
        # Export summary
        st.subheader("📊 Resumen de Exportación")
        st.metric("Total de registros", len(filtered_forms))
        st.metric("Registros originales", len(all_forms))
        
        if filtered_forms:
            # Status breakdown
            status_counts = {}
            for form in filtered_forms:
                status = form.estado.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            st.write("**Distribución por estado:**")
            for status, count in status_counts.items():
                st.write(f"- {status}: {count}")
        
        # Export buttons
        st.subheader("🚀 Generar Exportación")
        
        if st.button("📥 Generar Archivos", type="primary"):
            generate_exports(
                filtered_forms, metrics, export_formats, 
                include_detailed, include_charts, include_metadata,
                custom_filename, exporter, selected_statuses, date_range
            )
    
    with col1:
        # Preview section
        st.subheader("👀 Vista Previa de Datos")
        
        if filtered_forms:
            # Create preview DataFrame
            preview_data = create_preview_dataframe(filtered_forms)
            
            # Show preview with pagination
            items_per_page = 10
            total_items = len(preview_data)
            
            if total_items > items_per_page:
                start_idx, end_idx = filters.pagination_filter(
                    total_items, 
                    key="export_preview",
                    items_per_page=items_per_page
                )
                preview_subset = preview_data.iloc[start_idx:end_idx]
            else:
                preview_subset = preview_data
            
            st.dataframe(preview_subset, use_container_width=True)
            
            # Data quality indicators
            show_data_quality_indicators(preview_data)
            
        else:
            st.info("No hay datos que coincidan con los filtros seleccionados.")
        
        # Export templates section
        show_export_templates(exporter)

@st.cache_data(ttl=300)
def load_export_data():
    """Load data for export with caching"""
    db = SessionLocal()
    try:
        crud = FormularioCRUD(db)
        all_forms = crud.get_all_formularios(limit=1000)
        metrics = crud.get_metricas_generales()
        return all_forms, metrics
    finally:
        db.close()

def filter_forms_for_export(forms, selected_statuses, date_range, 
                          min_activities=0, has_courses=False, has_publications=False, 
                          has_events=False, name_filter="", email_domain=""):
    """Filter forms based on export criteria with advanced options"""
    
    filtered = forms
    
    # Filter by status
    if "TODOS" not in selected_statuses:
        filtered = [f for f in filtered if f.estado.value in selected_statuses]
    
    # Filter by date range
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered = [
            f for f in filtered 
            if f.fecha_envio and start_date <= f.fecha_envio.date() <= end_date
        ]
    
    # Filter by minimum activities
    if min_activities > 0:
        filtered = [
            f for f in filtered 
            if (len(f.cursos_capacitacion) + len(f.publicaciones) + 
                len(f.eventos_academicos) + len(f.diseno_curricular) + 
                len(f.movilidad) + len(f.reconocimientos) + 
                len(f.certificaciones)) >= min_activities
        ]
    
    # Filter by specific activity types
    if has_courses:
        filtered = [f for f in filtered if len(f.cursos_capacitacion) > 0]
    
    if has_publications:
        filtered = [f for f in filtered if len(f.publicaciones) > 0]
    
    if has_events:
        filtered = [f for f in filtered if len(f.eventos_academicos) > 0]
    
    # Filter by name (partial match, case insensitive)
    if name_filter.strip():
        name_lower = name_filter.lower().strip()
        filtered = [
            f for f in filtered 
            if name_lower in f.nombre_completo.lower()
        ]
    
    # Filter by email domain
    if email_domain.strip():
        domain_lower = email_domain.lower().strip()
        filtered = [
            f for f in filtered 
            if domain_lower in f.correo_institucional.lower()
        ]
    
    return filtered

def create_preview_dataframe(forms):
    """Create DataFrame for preview"""
    
    data = []
    for form in forms:
        # Safely access relationships
        try:
            total_cursos = len(form.cursos_capacitacion) if hasattr(form, 'cursos_capacitacion') and form.cursos_capacitacion else 0
        except:
            total_cursos = 0
            
        try:
            total_publicaciones = len(form.publicaciones) if hasattr(form, 'publicaciones') and form.publicaciones else 0
        except:
            total_publicaciones = 0
            
        try:
            total_eventos = len(form.eventos_academicos) if hasattr(form, 'eventos_academicos') and form.eventos_academicos else 0
        except:
            total_eventos = 0
            
        try:
            total_disenos = len(form.diseno_curricular) if hasattr(form, 'diseno_curricular') and form.diseno_curricular else 0
        except:
            total_disenos = 0
            
        try:
            total_movilidades = len(form.movilidad) if hasattr(form, 'movilidad') and form.movilidad else 0
        except:
            total_movilidades = 0
            
        try:
            total_reconocimientos = len(form.reconocimientos) if hasattr(form, 'reconocimientos') and form.reconocimientos else 0
        except:
            total_reconocimientos = 0
            
        try:
            total_certificaciones = len(form.certificaciones) if hasattr(form, 'certificaciones') and form.certificaciones else 0
        except:
            total_certificaciones = 0
        
        data.append({
            'ID': form.id,
            'Nombre': form.nombre_completo,
            'Email': form.correo_institucional,
            'Estado': form.estado.value,
            'Fecha Envío': form.fecha_envio.strftime('%Y-%m-%d') if form.fecha_envio else '',
            'Cursos': total_cursos,
            'Publicaciones': total_publicaciones,
            'Eventos': total_eventos,
            'Total Items': (total_cursos + total_publicaciones + total_eventos + 
                          total_disenos + total_movilidades + total_reconocimientos + 
                          total_certificaciones)
        })
    
    return pd.DataFrame(data)

def show_data_quality_indicators(df):
    """Show data quality indicators"""
    
    st.subheader("🔍 Indicadores de Calidad")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Completeness
        completeness = (df.notna().sum() / len(df) * 100).mean()
        st.metric("Completitud Promedio", f"{completeness:.1f}%")
    
    with col2:
        # Duplicates (based on email)
        duplicates = df['Email'].duplicated().sum()
        st.metric("Posibles Duplicados", duplicates)
    
    with col3:
        # Activity distribution
        avg_items = df['Total Items'].mean()
        st.metric("Items Promedio", f"{avg_items:.1f}")

def generate_exports(forms, metrics, formats, include_detailed, include_charts, 
                    include_metadata, custom_filename, exporter, selected_statuses, date_range):
    """Generate and provide download links for exports using advanced export functionality"""
    
    if not forms:
        st.error("No hay datos para exportar.")
        return
    
    base_filename = custom_filename if custom_filename else "exportacion_docentes"
    
    # Prepare filters for advanced export
    filters = {}
    if selected_statuses and "TODOS" not in selected_statuses:
        filters['estados'] = selected_statuses
    
    if len(date_range) == 2:
        filters['fecha_inicio'] = date_range[0].isoformat()
        filters['fecha_fin'] = date_range[1].isoformat()
    
    try:
        with st.spinner("Generando archivos de exportación con opciones avanzadas..."):
            
            if "CSV" in formats:
                # Generate enhanced CSV
                csv_content = exporter.export_with_advanced_options(
                    forms, 
                    export_format='csv',
                    filters=filters,
                    include_metadata=include_metadata,
                    custom_filename=base_filename
                )
                
                st.download_button(
                    label="📥 Descargar CSV Avanzado",
                    data=csv_content.getvalue(),
                    file_name=f"{base_filename}_{exporter.timestamp}.csv",
                    mime="text/csv",
                    key="download_csv"
                )
            
            if "Excel" in formats:
                # Generate enhanced Excel
                excel_content = exporter.export_with_advanced_options(
                    forms,
                    export_format='excel',
                    filters=filters,
                    include_metadata=include_metadata,
                    include_charts=include_charts,
                    custom_filename=base_filename
                )
                
                st.download_button(
                    label="📊 Descargar Excel Avanzado",
                    data=excel_content.getvalue(),
                    file_name=f"{base_filename}_{exporter.timestamp}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_excel"
                )
            
            if "JSON" in formats:
                # Generate enhanced JSON
                json_content = exporter.export_with_advanced_options(
                    forms,
                    export_format='json',
                    filters=filters,
                    include_metadata=include_metadata,
                    custom_filename=base_filename
                )
                
                st.download_button(
                    label="📄 Descargar JSON Completo",
                    data=json_content.getvalue(),
                    file_name=f"{base_filename}_{exporter.timestamp}.json",
                    mime="application/json",
                    key="download_json"
                )
            
            if "Paquete Completo" in formats:
                # Generate comprehensive package
                package_content = exporter.export_with_advanced_options(
                    forms,
                    export_format='package',
                    filters=filters,
                    include_metadata=include_metadata,
                    include_charts=include_charts,
                    custom_filename=base_filename
                )
                
                st.download_button(
                    label="📦 Descargar Paquete Completo Avanzado",
                    data=package_content.getvalue(),
                    file_name=f"{base_filename}_{exporter.timestamp}_paquete_completo.zip",
                    mime="application/zip",
                    key="download_package"
                )
        
        # Show export summary
        st.success(f"✅ Archivos generados exitosamente!")
        
        # Display export details
        with st.expander("📋 Detalles de la Exportación"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Datos exportados:**")
                st.write(f"- Total de registros: {len(forms)}")
                st.write(f"- Formatos generados: {', '.join(formats)}")
                st.write(f"- Metadatos incluidos: {'Sí' if include_metadata else 'No'}")
                st.write(f"- Gráficos incluidos: {'Sí' if include_charts else 'No'}")
            
            with col2:
                st.write("**Filtros aplicados:**")
                if filters:
                    for key, value in filters.items():
                        st.write(f"- {key}: {value}")
                else:
                    st.write("- Ningún filtro aplicado")
                
                st.write(f"**Timestamp:** {exporter.timestamp}")
        
    except Exception as e:
        st.error(f"❌ Error al generar exportación: {str(e)}")
        st.exception(e)  # Show full traceback for debugging

def show_export_templates(exporter):
    """Show export templates and examples"""
    
    with st.expander("📋 Plantillas y Ejemplos"):
        st.subheader("Formatos Disponibles")
        
        # CSV example
        st.write("**CSV (Comma Separated Values):**")
        st.code("""
ID,Nombre_Completo,Estado,Fecha_Envio,Total_Cursos
1,Dr. Juan Pérez,APROBADO,2024-03-15 10:30:00,3
2,Dra. María García,PENDIENTE,2024-03-16 14:20:00,2
        """, language="csv")
        
        # Excel structure
        st.write("**Excel (Múltiples hojas):**")
        st.write("- **Resumen**: Métricas generales del sistema")
        st.write("- **Formularios**: Datos principales de cada formulario")
        st.write("- **Cursos**: Detalle de todos los cursos de capacitación")
        st.write("- **Publicaciones**: Detalle de todas las publicaciones")
        st.write("- **Eventos**: Detalle de todos los eventos académicos")
        st.write("- **[Otras categorías]**: Una hoja por cada tipo de actividad")
        
        # JSON structure
        st.write("**JSON (JavaScript Object Notation):**")
        st.code("""
{
  "metadata": {
    "fecha_exportacion": "2024-03-15T10:30:00",
    "total_registros": 150
  },
  "datos": [
    {
      "id": 1,
      "nombre_completo": "Dr. Juan Pérez",
      "estado": "APROBADO",
      "cursos": [...],
      "publicaciones": [...]
    }
  ]
}
        """, language="json")
        
        # Package contents
        st.write("**Paquete Completo (ZIP):**")
        st.write("- Archivo CSV básico")
        st.write("- Archivo Excel detallado con gráficos")
        st.write("- Reporte de métricas en JSON")
        st.write("- Archivo README con documentación")

if __name__ == "__main__":
    show_data_export_page()