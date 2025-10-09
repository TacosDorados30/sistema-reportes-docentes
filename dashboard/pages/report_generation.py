from dashboard.components.interactive_filters import InteractiveFilters
from app.reports.report_history import ReportHistoryManager
from app.reports.report_generator import ReportGenerator
from app.database.crud import FormularioCRUD
from app.database.connection import SessionLocal
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))


def show_report_generation_page():
    """Report generation page with NLG capabilities"""

    # Require authentication
    from app.auth.streamlit_auth import StreamlitAuth
    auth = StreamlitAuth()
    if not auth.require_authentication():
        return

    st.title("📄 Generación de Reportes")
    st.markdown(
        "Genere reportes narrativos automáticos usando técnicas de procesamiento de lenguaje natural.")

    # Initialize components
    report_generator = ReportGenerator()
    history_manager = ReportHistoryManager()
    filters = InteractiveFilters()

    # Load data
    try:
        all_forms, metrics = load_report_data()
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return

    if not all_forms:
        st.warning("No hay datos disponibles para generar reportes.")
        return

    # Sidebar configuration
    st.sidebar.header("🎛️ Configuración de Reporte")

    # Report type selection
    report_type = st.sidebar.selectbox(
        "Tipo de reporte:",
        ["annual", "quarterly", "data_table"],
        format_func=lambda x: {
            "annual": "📊 Reporte Anual Narrativo",
            "quarterly": "📈 Resumen Trimestral",
            "data_table": "📋 Reporte de Datos Tabulares"
        }[x]
    )

    # Period selection
    if report_type == "quarterly":
        col1, col2 = st.sidebar.columns(2)
        with col1:
            year = st.selectbox("Año:", range(2020, 2030),
                                index=4)  # Default to 2024
        with col2:
            quarter = st.selectbox("Trimestre:", [1, 2, 3, 4])
    else:
        # Date range for annual or custom reports
        min_date = min(
            [f.fecha_envio for f in all_forms if f.fecha_envio]).date()
        max_date = max(
            [f.fecha_envio for f in all_forms if f.fecha_envio]).date()

        date_range = st.sidebar.date_input(
            "Período del reporte:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

    # Additional options
    with st.sidebar.expander("⚙️ Opciones Avanzadas"):
        include_trends = st.checkbox(
            "Incluir análisis de tendencias", value=True)
        include_highlights = st.checkbox(
            "Incluir elementos destacados", value=True)
        report_tone = st.selectbox(
            "Tono del reporte:",
            ["professional", "academic", "executive"],
            format_func=lambda x: {
                "professional": "Profesional",
                "academic": "Académico",
                "executive": "Ejecutivo"
            }[x]
        )

        custom_title = st.text_input(
            "Título personalizado (opcional):",
            placeholder="Reporte de Actividades Docentes"
        )

    # Main content area
    tab1, tab2, tab3 = st.tabs(
        ["🔧 Generar Reporte", "📚 Historial", "📊 Estadísticas"])

    with tab1:
        # Report generation interface
        st.subheader("Generación de Reporte")

        # Filter data based on period
        if report_type == "quarterly":
            period_start, period_end = get_quarter_dates(quarter, year)
            filtered_forms = filter_forms_by_period(
                all_forms, period_start, period_end)
            period_text = f"{get_quarter_name(quarter)} {year}"
        else:
            if len(date_range) == 2:
                period_start, period_end = date_range
                filtered_forms = filter_forms_by_period(
                    all_forms, period_start, period_end)
                period_text = f"{period_start.strftime('%B %Y')} - {period_end.strftime('%B %Y')}"
            else:
                st.warning("Por favor seleccione un rango de fechas válido.")
                return

        # Show preview information
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Período", period_text)
        with col2:
            st.metric("Formularios", len(filtered_forms))
        with col3:
            approved_count = len(
                [f for f in filtered_forms if f.estado.value == 'APROBADO'])
            st.metric("Aprobados", approved_count)

        if filtered_forms:
            # Show data preview
            with st.expander("👀 Vista Previa de Datos"):
                preview_df = create_preview_dataframe(filtered_forms)
                st.dataframe(preview_df.head(10), use_container_width=True)

                # Activity summary
                st.subheader("Resumen de Actividades")
                activity_summary = calculate_activity_summary(filtered_forms)

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Cursos", activity_summary['cursos'])
                with col2:
                    st.metric("Publicaciones",
                              activity_summary['publicaciones'])
                with col3:
                    st.metric("Eventos", activity_summary['eventos'])
                with col4:
                    st.metric("Total Horas", activity_summary['horas'])

            # Export format selection
            st.subheader("📤 Opciones de Exportación")

            col1, col2 = st.columns(2)

            with col1:
                # Generate markdown report
                if st.button("🚀 Generar Reporte Markdown", type="primary"):
                    generate_and_display_report(
                        report_generator, history_manager, filtered_forms,
                        report_type, period_start, period_end,
                        include_trends, include_highlights, report_tone, custom_title
                    )

            with col2:
                # Multi-format export options
                export_format = st.selectbox(
                    "Formato de exportación:",
                    ["PDF", "Excel", "PowerPoint"],
                    help="Seleccione el formato para exportar el reporte"
                )

                if st.button(f"📄 Exportar como {export_format}"):
                    st.info(f"Función de exportación a {export_format} en desarrollo")
                    # export_multiformat_report(
                    #     report_generator, filtered_forms, report_type,
                    #     period_start, period_end, export_format.lower(),
                    #     custom_title, include_highlights, include_metadata=True
                    # )

        else:
            st.info("No hay datos disponibles para el período seleccionado.")

    with tab2:
        # Report history
        show_report_history(history_manager)

    with tab3:
        # Storage statistics
        show_storage_statistics(history_manager)


@st.cache_data(ttl=300)
def load_report_data():
    """Load data for report generation with caching"""
    db = SessionLocal()
    try:
        crud = FormularioCRUD(db)
        all_forms = crud.get_all_formularios(limit=1000)
        metrics = crud.get_metricas_generales()
        return all_forms, metrics
    finally:
        db.close()


def filter_forms_by_period(forms, start_date, end_date):
    """Filter forms by date period"""
    return [
        f for f in forms
        if f.fecha_envio and start_date <= f.fecha_envio.date() <= end_date
    ]


def get_quarter_dates(quarter, year):
    """Get start and end dates for a quarter"""
    quarter_starts = {
        1: (1, 1), 2: (4, 1), 3: (7, 1), 4: (10, 1)
    }
    quarter_ends = {
        1: (3, 31), 2: (6, 30), 3: (9, 30), 4: (12, 31)
    }

    start_month, start_day = quarter_starts[quarter]
    end_month, end_day = quarter_ends[quarter]

    return (
        date(year, start_month, start_day),
        date(year, end_month, end_day)
    )


def get_quarter_name(quarter):
    """Get quarter name in Spanish"""
    names = {1: 'Primer Trimestre', 2: 'Segundo Trimestre',
             3: 'Tercer Trimestre', 4: 'Cuarto Trimestre'}
    return names[quarter]


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
        
        data.append({
            'ID': form.id,
            'Docente': form.nombre_completo,
            'Estado': form.estado.value,
            'Fecha': form.fecha_envio.strftime('%Y-%m-%d') if form.fecha_envio else '',
            'Cursos': total_cursos,
            'Publicaciones': total_publicaciones,
            'Eventos': total_eventos
        })

    return pd.DataFrame(data)


def generate_simple_report(forms, title, report_type, period_start, period_end):
    """Generate a simple text report"""
    
    # Calculate basic statistics
    total_forms = len(forms)
    approved_forms = [f for f in forms if f.estado.value == 'APROBADO']
    pending_forms = [f for f in forms if f.estado.value == 'PENDIENTE']
    rejected_forms = [f for f in forms if f.estado.value == 'RECHAZADO']
    
    # Calculate activity summary
    activity_summary = calculate_activity_summary(forms)
    
    # Generate report content
    report_lines = [
        f"# {title}",
        "",
        f"**Período:** {period_start.strftime('%Y-%m-%d')} - {period_end.strftime('%Y-%m-%d')}",
        f"**Fecha de generación:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Resumen Ejecutivo",
        "",
        f"- **Total de formularios:** {total_forms}",
        f"- **Formularios aprobados:** {len(approved_forms)}",
        f"- **Formularios pendientes:** {len(pending_forms)}",
        f"- **Formularios rechazados:** {len(rejected_forms)}",
        "",
        "## Actividades Académicas",
        "",
        f"- **Cursos de capacitación:** {activity_summary['cursos']}",
        f"- **Publicaciones:** {activity_summary['publicaciones']}",
        f"- **Eventos académicos:** {activity_summary['eventos']}",
        f"- **Total de horas de capacitación:** {activity_summary['horas']}",
        "",
        "## Detalles por Docente",
        ""
    ]
    
    # Add details for each approved form
    for i, form in enumerate(approved_forms[:10], 1):  # Limit to first 10
        try:
            cursos_count = len(form.cursos_capacitacion) if hasattr(form, 'cursos_capacitacion') and form.cursos_capacitacion else 0
        except:
            cursos_count = 0
            
        try:
            pub_count = len(form.publicaciones) if hasattr(form, 'publicaciones') and form.publicaciones else 0
        except:
            pub_count = 0
            
        try:
            eventos_count = len(form.eventos_academicos) if hasattr(form, 'eventos_academicos') and form.eventos_academicos else 0
        except:
            eventos_count = 0
        
        periodo = f"{form.año_academico} - {form.trimestre}" if hasattr(form, 'año_academico') and hasattr(form, 'trimestre') else "N/A"
        
        report_lines.extend([
            f"### {i}. {form.nombre_completo}",
            f"- **Email:** {form.correo_institucional}",
            f"- **Período:** {periodo}",
            f"- **Cursos:** {cursos_count}",
            f"- **Publicaciones:** {pub_count}",
            f"- **Eventos:** {eventos_count}",
            ""
        ])
    
    if len(approved_forms) > 10:
        report_lines.append(f"*... y {len(approved_forms) - 10} docentes más*")
    
    report_lines.extend([
        "",
        "---",
        "",
        f"*Reporte generado automáticamente por el Sistema de Reportes Docentes*",
        f"*Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
    ])
    
    return "\n".join(report_lines)

def calculate_activity_summary(forms):
    """Calculate activity summary for approved forms"""
    approved_forms = [f for f in forms if f.estado.value == 'APROBADO']

    total_cursos = 0
    total_publicaciones = 0
    total_eventos = 0
    total_horas = 0
    
    for f in approved_forms:
        # Safely access relationships
        try:
            cursos = f.cursos_capacitacion if hasattr(f, 'cursos_capacitacion') and f.cursos_capacitacion else []
            total_cursos += len(cursos)
            total_horas += sum(c.horas for c in cursos if hasattr(c, 'horas') and c.horas)
        except:
            pass
            
        try:
            publicaciones = f.publicaciones if hasattr(f, 'publicaciones') and f.publicaciones else []
            total_publicaciones += len(publicaciones)
        except:
            pass
            
        try:
            eventos = f.eventos_academicos if hasattr(f, 'eventos_academicos') and f.eventos_academicos else []
            total_eventos += len(eventos)
        except:
            pass

    return {
        'cursos': total_cursos,
        'publicaciones': total_publicaciones,
        'eventos': total_eventos,
        'horas': total_horas
    }


def generate_and_display_report(report_generator, history_manager, forms,
                                report_type, period_start, period_end,
                                include_trends, include_highlights, report_tone, custom_title):
    """Generate report and display results"""

    try:
        with st.spinner("Generando reporte con técnicas de NLG..."):

            # Generate title
            if custom_title:
                title = custom_title
            else:
                if report_type == "annual":
                    title = f"Reporte Anual de Actividades Docentes {period_start.year}"
                elif report_type == "quarterly":
                    quarter = ((period_start.month - 1) // 3) + 1
                    title = f"Resumen Trimestral Q{quarter} {period_start.year}"
                else:
                    title = f"Reporte de Datos {period_start.strftime('%B %Y')}"

            # Generate simple report content
            report_content = generate_simple_report(forms, title, report_type, period_start, period_end)

            # Customize tone if needed
            if report_tone != "professional":
                report_content = report_generator.nlg_engine.customize_report_tone(
                    report_content, report_tone
                )

            # Save to history
            report_id = history_manager.save_report(
                content=report_content,
                title=title,
                report_type=report_type,
                period_start=period_start,
                period_end=period_end,
                parameters={
                    'include_trends': include_trends,
                    'include_highlights': include_highlights,
                    'report_tone': report_tone,
                    'forms_count': len(forms)
                }
            )

            st.success(f"✅ Reporte generado exitosamente! ID: {report_id}")

            # Display report
            st.subheader("📄 Reporte Generado")

            # Add download button
            st.download_button(
                label="📥 Descargar Reporte",
                data=report_content,
                file_name=f"{title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown",
                key="download_report"
            )

            # Display content
            st.markdown(report_content)

            # Show generation details
            with st.expander("ℹ️ Detalles de Generación"):
                st.write(f"**ID del reporte:** {report_id}")
                st.write(f"**Tipo:** {report_type}")
                st.write(f"**Período:** {period_start} - {period_end}")
                st.write(f"**Formularios procesados:** {len(forms)}")
                st.write(f"**Tono:** {report_tone}")
                st.write(
                    f"**Fecha de generación:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        st.error(f"❌ Error al generar reporte: {str(e)}")
        st.exception(e)


def show_report_history(history_manager):
    """Show report history interface"""

    st.subheader("📚 Historial de Reportes")

    # Get history
    history = history_manager.get_report_history(limit=50)

    if not history:
        st.info("No hay reportes generados aún.")
        return

    # Filter options
    col1, col2 = st.columns(2)

    with col1:
        type_filter = st.selectbox(
            "Filtrar por tipo:",
            ["Todos", "annual", "quarterly", "data_table"],
            format_func=lambda x: {
                "Todos": "Todos los tipos",
                "annual": "Reportes Anuales",
                "quarterly": "Reportes Trimestrales",
                "data_table": "Reportes de Datos"
            }.get(x, x)
        )

    with col2:
        search_query = st.text_input(
            "Buscar reportes:", placeholder="Título, resumen...")

    # Apply filters
    filtered_history = history
    if type_filter != "Todos":
        filtered_history = [
            r for r in filtered_history if r['report_type'] == type_filter]

    if search_query:
        filtered_history = history_manager.search_reports(search_query)

    # Display reports
    for report in filtered_history[:20]:  # Show first 20
        with st.expander(f"📄 {report['title']} ({report['generation_date'][:10]})"):

            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"**Tipo:** {report['report_type']}")
                st.write(
                    f"**Período:** {report['period_start'][:10]} - {report['period_end'][:10]}")
                st.write(f"**Resumen:** {report['summary']}")
                st.write(f"**Tamaño:** {report['file_size']} bytes")

            with col2:
                # Action buttons
                if st.button("👁️ Ver", key=f"view_{report['id']}"):
                    content = history_manager.get_report_content(report['id'])
                    if content:
                        st.markdown("---")
                        st.markdown(content)

                if st.button("📥 Descargar", key=f"download_{report['id']}"):
                    content = history_manager.get_report_content(report['id'])
                    if content:
                        st.download_button(
                            label="Descargar archivo",
                            data=content,
                            file_name=f"{report['title'].replace(' ', '_')}.md",
                            mime="text/markdown",
                            key=f"dl_{report['id']}"
                        )

                if st.button("🗑️ Eliminar", key=f"delete_{report['id']}"):
                    if history_manager.delete_report(report['id']):
                        st.success("Reporte eliminado")
                        st.rerun()


def show_storage_statistics(history_manager):
    """Show storage statistics"""

    st.subheader("📊 Estadísticas de Almacenamiento")

    stats = history_manager.get_storage_statistics()

    # Main metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Reportes", stats['total_reports'])
    with col2:
        st.metric("Tamaño Total", f"{stats['total_size_mb']} MB")
    with col3:
        st.metric("Reportes Recientes", stats['recent_reports_count'])
    with col4:
        if stats['total_reports'] > 0:
            avg_size = stats['total_size_mb'] / stats['total_reports']
            st.metric("Tamaño Promedio", f"{avg_size:.2f} MB")

    # Reports by type
    if stats['reports_by_type']:
        st.subheader("Distribución por Tipo")

        type_df = pd.DataFrame([
            {'Tipo': tipo, 'Cantidad': cantidad}
            for tipo, cantidad in stats['reports_by_type'].items()
        ])

        st.bar_chart(type_df.set_index('Tipo'))

    # Timeline
    if stats['oldest_report'] and stats['newest_report']:
        st.subheader("Línea de Tiempo")
        st.write(f"**Primer reporte:** {stats['oldest_report'][:10]}")
        st.write(f"**Último reporte:** {stats['newest_report'][:10]}")

    # Cleanup options
    st.subheader("🧹 Mantenimiento")

    col1, col2 = st.columns(2)

    with col1:
        days_to_keep = st.number_input(
            "Días a conservar:",
            min_value=30,
            max_value=3650,
            value=365
        )

        if st.button("Limpiar Reportes Antiguos"):
            deleted_count = history_manager.cleanup_old_reports(days_to_keep)
            st.success(f"Se eliminaron {deleted_count} reportes antiguos")

    with col2:
        if st.button("Exportar Metadatos"):
            metadata = history_manager.export_history_metadata()
            st.download_button(
                label="Descargar Metadatos",
                data=metadata,
                file_name=f"report_metadata_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )


if __name__ == "__main__":
    show_report_generation_page()


def export_multiformat_report(report_generator, forms, report_type,
                              period_start, period_end, export_format,
                              custom_title, include_charts, include_metadata):
    """Export report in multiple formats (PDF, Excel, PowerPoint)"""

    try:
        with st.spinner(f"Generando reporte en formato {export_format.upper()}..."):

            # Generate title
            if custom_title:
                title = custom_title
            else:
                if report_type == "annual":
                    title = f"Reporte Anual de Actividades Docentes {period_start.year}"
                elif report_type == "quarterly":
                    quarter = ((period_start.month - 1) // 3) + 1
                    title = f"Resumen Trimestral Q{quarter} {period_start.year}"
                else:
                    title = f"Reporte de Datos {period_start.strftime('%B %Y')}"

            # Export report
            if export_format == 'pdf':
                export_format_name = 'PDF'
                mime_type = 'application/pdf'
                file_extension = 'pdf'
            elif export_format == 'excel':
                export_format_name = 'Excel'
                mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                file_extension = 'xlsx'
            elif export_format == 'powerpoint':
                export_format_name = 'PowerPoint'
                mime_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
                file_extension = 'pptx'
            else:
                st.error(f"Formato no soportado: {export_format}")
                return

            # Generate the export
            exported_content = report_generator.export_report_to_format(
                forms=forms,
                report_type=report_type,
                period_start=period_start,
                period_end=period_end,
                export_format=export_format,
                title=title,
                include_charts=include_charts,
                include_metadata=include_metadata
            )

            # Create filename
            safe_title = title.replace(' ', '_').replace('/', '_')
            filename = f"{safe_title}_{datetime.now().strftime('%Y%m%d')}.{file_extension}"

            # Provide download
            st.success(
                f"✅ Reporte en formato {export_format_name} generado exitosamente!")

            st.download_button(
                label=f"📥 Descargar {export_format_name}",
                data=exported_content.getvalue(),
                file_name=filename,
                mime=mime_type,
                key=f"download_{export_format}"
            )

            # Show export details
            with st.expander("ℹ️ Detalles de Exportación"):
                st.write(f"**Formato:** {export_format_name}")
                st.write(f"**Título:** {title}")
                st.write(f"**Período:** {period_start} - {period_end}")
                st.write(f"**Formularios procesados:** {len(forms)}")
                st.write(
                    f"**Gráficos incluidos:** {'Sí' if include_charts else 'No'}")
                st.write(
                    f"**Metadatos incluidos:** {'Sí' if include_metadata else 'No'}")
                st.write(
                    f"**Tamaño del archivo:** {len(exported_content.getvalue())} bytes")
                st.write(
                    f"**Fecha de generación:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                # Format-specific information
                if export_format == 'pdf':
                    st.write("**Características PDF:**")
                    st.write("- Formato profesional con estilos personalizados")
                    st.write("- Gráficos integrados usando ReportLab")
                    st.write("- Tablas formateadas con colores institucionales")
                    st.write("- Metadatos incluidos en sección dedicada")

                elif export_format == 'excel':
                    st.write("**Características Excel:**")
                    st.write("- Múltiples hojas con datos organizados")
                    st.write("- Gráficos interactivos en hoja dedicada")
                    st.write("- Formato profesional con colores y estilos")
                    st.write("- Tablas con filtros y formato automático")

                elif export_format == 'powerpoint':
                    st.write("**Características PowerPoint:**")
                    st.write("- Presentación con diapositivas estructuradas")
                    st.write("- Gráficos integrados en diapositivas")
                    st.write("- Diseño profesional con colores institucionales")
                    st.write("- Contenido organizado por secciones")

    except Exception as e:
        st.error(
            f"❌ Error al generar reporte en formato {export_format}: {str(e)}")
        st.exception(e)  # Show full traceback for debugging
