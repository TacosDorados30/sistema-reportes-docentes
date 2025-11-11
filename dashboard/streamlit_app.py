
import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required modules
from app.database.connection import SessionLocal
from app.database.crud import FormularioCRUD
from app.models.database import EstadoFormularioEnum
from app.auth.streamlit_auth import auth
from app.core.data_processor import DataProcessor
from app.core.metrics_calculator import MetricsCalculator

# Lazy imports for better performance
@st.cache_resource
def get_pandas():
    import pandas as pd
    return pd

@st.cache_resource  
def get_plotly():
    import plotly.express as px
    import plotly.graph_objects as go
    return px, go

# Initialize app once
if 'app_initialized' not in st.session_state:
    try:
        from app.startup import startup_application
        startup_application()
        st.session_state.app_initialized = True
    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()

# Page config
st.set_page_config(
    page_title="Sistema de Reportes Docentes",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)


@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data():
    """Load data from database with caching"""
    db = SessionLocal()
    try:
        crud = FormularioCRUD(db)

        # Get limited forms for better performance
        all_forms = crud.get_all_formularios(
            limit=50)  # Reduced from 1000 to 50

        # Get metrics
        metrics = crud.get_metricas_generales()

        return all_forms, metrics
    finally:
        db.close()


# Cache for 10 minutes (longer for less frequent changes)
@st.cache_data(ttl=600)
def load_metrics_only():
    """Load only metrics with longer caching"""
    db = SessionLocal()
    try:
        crud = FormularioCRUD(db)
        return crud.get_metricas_generales()
    finally:
        db.close()


# Cache for 1 minute (more frequent updates for pending forms)
@st.cache_data(ttl=60)
def get_pending_forms():
    """Get pending forms for review"""
    db = SessionLocal()
    try:
        crud = FormularioCRUD(db)
        # Reduced limit
        return crud.get_formularios_by_estado(EstadoFormularioEnum.PENDIENTE, limit=20)
    finally:
        db.close()


def approve_form(form_id: int):
    """Approve a form with comprehensive error handling"""
    from app.core.error_handler import error_handler, DatabaseError, ValidationError
    from app.core.logging_middleware import app_logger
    from app.core.validators import DatabaseValidator

    # Validate input
    if not DatabaseValidator.validate_id(form_id):
        error_handler.log_error(
            ValidationError("Invalid form ID", "form_id"),
            "approve_form",
            auth.get_current_user().get("username") if auth.get_current_user() else None
        )
        return False

    db = SessionLocal()
    try:
        crud = FormularioCRUD(db)
        user_info = auth.get_current_user()
        user_id = user_info.get("username") if user_info else "unknown"

        app_logger.log_operation(
            "form_approval_start",
            {"form_id": form_id},
            user_id=user_id
        )

        # Get form details for logging
        form = crud.get_formulario(form_id)
        if not form:
            error_msg = f"Form with ID {form_id} not found"
            app_logger.log_operation(
                "form_approval_failed",
                {"form_id": form_id, "reason": "form_not_found"},
                "WARNING",
                user_id
            )
            return False

        # Check if form is in valid state for approval
        if form.estado.value != "PENDIENTE":
            error_msg = f"Form {form_id} is not in pending state (current: {form.estado.value})"
            app_logger.log_operation(
                "form_approval_failed",
                {"form_id": form_id, "reason": "invalid_state",
                    "current_state": form.estado.value},
                "WARNING",
                user_id
            )
            return False

        success = crud.aprobar_formulario(form_id, "streamlit_admin")

        if success:
            # Log the approval action
            try:
                from app.core.simple_audit import simple_audit
                if user_info:
                    simple_audit.log_form_approval(
                        form_id=form_id,
                        form_owner=form.nombre_completo,
                        approved_by=user_info["name"]
                    )

                app_logger.log_operation(
                    "form_approval_success",
                    {"form_id": form_id, "form_owner": form.nombre_completo},
                    user_id=user_id
                )

            except Exception as e:
                error_handler.log_error(
                    e, "audit_logging_in_approval", user_id)
        else:
            app_logger.log_operation(
                "form_approval_failed",
                {"form_id": form_id, "reason": "database_operation_failed"},
                "ERROR",
                user_id
            )

        return success

    except Exception as e:
        db_error = error_handler.handle_database_error(
            e,
            "approve_form",
            auth.get_current_user().get("username") if auth.get_current_user() else None
        )
        app_logger.log_operation(
            "form_approval_error",
            {"form_id": form_id, "error": str(db_error)},
            "ERROR",
            auth.get_current_user().get("username") if auth.get_current_user() else None
        )
        return False
    finally:
        db.close()


def reject_form(form_id: int, comment: str = ""):
    """Reject a form with comprehensive error handling"""
    from app.core.error_handler import error_handler, DatabaseError, ValidationError
    from app.core.logging_middleware import app_logger
    from app.core.validators import DatabaseValidator

    # Validate input
    if not DatabaseValidator.validate_id(form_id):
        error_handler.log_error(
            ValidationError("Invalid form ID", "form_id"),
            "reject_form",
            auth.get_current_user().get("username") if auth.get_current_user() else None
        )
        return False

    # Sanitize comment
    if comment:
        comment = DatabaseValidator.sanitize_string(comment, 1000)

    db = SessionLocal()
    try:
        crud = FormularioCRUD(db)
        user_info = auth.get_current_user()
        user_id = user_info.get("username") if user_info else "unknown"

        app_logger.log_operation(
            "form_rejection_start",
            {"form_id": form_id, "has_comment": bool(comment)},
            user_id=user_id
        )

        # Get form details for logging
        form = crud.get_formulario(form_id)
        if not form:
            error_msg = f"Form with ID {form_id} not found"
            app_logger.log_operation(
                "form_rejection_failed",
                {"form_id": form_id, "reason": "form_not_found"},
                "WARNING",
                user_id
            )
            return False

        # Check if form is in valid state for rejection
        if form.estado.value != "PENDIENTE":
            error_msg = f"Form {form_id} is not in pending state (current: {form.estado.value})"
            app_logger.log_operation(
                "form_rejection_failed",
                {"form_id": form_id, "reason": "invalid_state",
                    "current_state": form.estado.value},
                "WARNING",
                user_id
            )
            return False

        success = crud.rechazar_formulario(form_id, "streamlit_admin", comment)

        if success:
            # Log the rejection action
            try:
                from app.core.simple_audit import simple_audit
                if user_info:
                    simple_audit.log_form_rejection(
                        form_id=form_id,
                        form_owner=form.nombre_completo,
                        rejected_by=user_info["name"],
                        reason=comment
                    )

                app_logger.log_operation(
                    "form_rejection_success",
                    {"form_id": form_id, "form_owner": form.nombre_completo,
                        "comment_length": len(comment) if comment else 0},
                    user_id=user_id
                )

            except Exception as e:
                error_handler.log_error(
                    e, "audit_logging_in_rejection", user_id)
        else:
            app_logger.log_operation(
                "form_rejection_failed",
                {"form_id": form_id, "reason": "database_operation_failed"},
                "ERROR",
                user_id
            )

        return success

    except Exception as e:
        db_error = error_handler.handle_database_error(
            e,
            "reject_form",
            auth.get_current_user().get("username") if auth.get_current_user() else None
        )
        app_logger.log_operation(
            "form_rejection_error",
            {"form_id": form_id, "error": str(db_error)},
            "ERROR",
            auth.get_current_user().get("username") if auth.get_current_user() else None
        )
        return False
    finally:
        db.close()


def main():
    """Main application - handles both public form and admin dashboard"""

    # Check if we should show the public form or admin dashboard
    try:
        # Try new Streamlit syntax
        query_params = st.query_params
        show_admin = query_params.get("admin", "false").lower() == "true"
    except AttributeError:
        # Use old Streamlit syntax
        query_params = st.experimental_get_query_params()
        show_admin = query_params.get("admin", ["false"])[0].lower() == "true"

    # Also check session state for admin mode
    if 'admin_mode' not in st.session_state:
        st.session_state.admin_mode = show_admin

    # Allow switching modes
    if show_admin:
        st.session_state.admin_mode = True

    if st.session_state.admin_mode:
        show_admin_dashboard()
    else:
        show_public_form()


def show_public_form():
    """Show the public form for teachers"""
    # Import and show the public form
    from dashboard.formulario import main as formulario_main
    formulario_main()


def show_admin_dashboard():
    """Show the admin dashboard"""
    # Initialize session state with persistence support
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None

    # Check authentication status first
    if not auth.is_authenticated():
        # Hide sidebar completely before login
        st.markdown("""
        <style>
            /* Hide sidebar completely before login */
            .css-1d391kg, .css-1lcbmhc, .css-1cypcdb, .css-17eq0hr, 
            [data-testid="stSidebar"], .stSidebar, section[data-testid="stSidebar"] {
                display: none !important;
                visibility: hidden !important;
                width: 0px !important;
                min-width: 0px !important;
            }
            
            /* Hide sidebar toggle button */
            .css-1rs6os, .css-17ziqus, [data-testid="collapsedControl"],
            button[kind="header"] {
                display: none !important;
                visibility: hidden !important;
            }
            
            /* Expand main content to full width */
            .css-18e3th9, .css-1d391kg, .main, .block-container {
                padding-left: 1rem !important;
                margin-left: 0rem !important;
            }
        </style>
        """, unsafe_allow_html=True)

        # Show login form
        auth.show_login_form()

        return

    # Only show the dashboard UI after successful authentication
    show_authenticated_dashboard()


def show_authenticated_dashboard():
    """Show the main dashboard after authentication"""

    # Load custom CSS for authenticated users and show sidebar
    st.markdown("""
    <style>
        /* Show sidebar after login */
        .css-1d391kg, .css-1lcbmhc, .css-1cypcdb, .css-17eq0hr, 
        [data-testid="stSidebar"], .stSidebar, section[data-testid="stSidebar"] {
            display: block !important;
            visibility: visible !important;
        }
        
        /* Show sidebar toggle button */
        .css-1rs6os, .css-17ziqus, [data-testid="collapsedControl"],
        button[kind="header"] {
            display: block !important;
            visibility: visible !important;
        }
        
        .main-header {
            font-size: 2.5rem;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #1f77b4;
        }
        .status-pending {
            color: #ff9800;
        }
        .status-approved {
            color: #4caf50;
        }
        .status-rejected {
            color: #f44336;
        }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown('<h1 class="main-header">📊 Sistema de Reportes Docentes</h1>',
                unsafe_allow_html=True)

    # Show user menu in sidebar
    auth.show_user_menu()
    auth.show_admin_menu()

    # Check for admin page requests
    if st.session_state.get('show_password_change'):
        auth.show_password_change()
        if st.button("← Volver al Dashboard"):
            st.session_state.show_password_change = False
            st.rerun()
        return

    # Load data with optimized caching - always show main dashboard
    try:
        # For main dashboard, use cached metrics only for better performance
        metrics = load_metrics_only()
        all_forms = []  # Load forms only when needed
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return

    # Always show main dashboard
    show_main_dashboard(all_forms, metrics)


def show_main_dashboard(all_forms, metrics):
    """Show main dashboard with overview metrics"""

    st.header("📈 Resumen General")

    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Formularios",
            value=metrics.total_formularios,
            delta=None
        )

    with col2:
        st.metric(
            label="Pendientes",
            value=metrics.formularios_pendientes,
            delta=None,
            help="Formularios esperando revisión"
        )

    with col3:
        st.metric(
            label="Aprobados",
            value=metrics.formularios_aprobados,
            delta=None
        )

    with col4:
        st.metric(
            label="Rechazados",
            value=metrics.formularios_rechazados,
            delta=None
        )

    # Charts section
    st.header("📊 Visualizaciones")

    col1, col2 = st.columns(2)

    with col1:
        # Status distribution pie chart
        status_data = {
            'Estado': ['Pendientes', 'Aprobados', 'Rechazados'],
            'Cantidad': [
                metrics.formularios_pendientes,
                metrics.formularios_aprobados,
                metrics.formularios_rechazados
            ]
        }

        px, go = get_plotly()
        fig_pie = px.pie(
            values=status_data['Cantidad'],
            names=status_data['Estado'],
            title="Distribución por Estado",
            color_discrete_map={
                'Pendientes': '#ff9800',
                'Aprobados': '#4caf50',
                'Rechazados': '#f44336'
            }
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # Academic activities bar chart
        activities_data = {
            'Actividad': ['Cursos', 'Publicaciones', 'Eventos', 'Diseños', 'Movilidades', 'Reconocimientos', 'Certificaciones', 'Otras'],
            'Cantidad': [
                metrics.total_cursos,
                metrics.total_publicaciones,
                metrics.total_eventos,
                metrics.total_disenos_curriculares,
                metrics.total_movilidades,
                metrics.total_reconocimientos,
                metrics.total_certificaciones,
                metrics.total_otras_actividades
            ]
        }

        fig_bar = px.bar(
            x=activities_data['Actividad'],
            y=activities_data['Cantidad'],
            title="Actividades Académicas (Aprobadas)",
            color=activities_data['Cantidad'],
            color_continuous_scale='Blues'
        )
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)


def show_form_review():
    """Show form review interface"""

    st.header("📋 Revisión de Formularios")

    # Get pending forms
    try:
        pending_forms = get_pending_forms()
    except Exception as e:
        st.error(f"Error al cargar formularios pendientes: {e}")
        return

    if not pending_forms:
        st.success("🎉 No hay formularios pendientes de revisión.")
        return

    st.info(f"Hay {len(pending_forms)} formularios pendientes de revisión.")

    # Form selection
    form_options = {
        f"ID {form.id} - {form.nombre_completo}": form for form in pending_forms}
    selected_form_key = st.selectbox(
        "Seleccionar formulario para revisar:", list(form_options.keys()))

    if selected_form_key:
        selected_form = form_options[selected_form_key]

        # Display form details
        st.subheader(f"📄 Detalles del Formulario ID: {selected_form.id}")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Información Personal:**")
            st.write(f"- **Nombre:** {selected_form.nombre_completo}")
            st.write(f"- **Email:** {selected_form.correo_institucional}")
            st.write(f"- **Período:** {selected_form.año_academico} - {selected_form.trimestre}" if hasattr(
                selected_form, 'año_academico') else "- **Período:** N/A")
            st.write(
                f"- **Fecha de envío:** {selected_form.fecha_envio.strftime('%Y-%m-%d %H:%M')}")

        with col2:
            st.write("**Estado:**")
            st.write(f"- **Estado actual:** {selected_form.estado.value}")
            if selected_form.fecha_revision:
                st.write(
                    f"- **Fecha revisión:** {selected_form.fecha_revision.strftime('%Y-%m-%d %H:%M')}")
            if selected_form.revisado_por:
                st.write(f"- **Estado:** Revisado")

        # Show related data
        st.subheader("📚 Contenido del Formulario")

        # Create tabs for different sections
        tabs = st.tabs(["Cursos", "Publicaciones", "Eventos", "Diseño Curricular",
                       "Movilidad", "Reconocimientos", "Certificaciones"])

        with tabs[0]:  # Cursos
            if selected_form.cursos_capacitacion:
                for i, curso in enumerate(selected_form.cursos_capacitacion, 1):
                    st.write(f"**Curso {i}:**")
                    st.write(f"- Nombre: {curso.nombre_curso}")
                    st.write(f"- Fecha: {curso.fecha}")
                    st.write(f"- Horas: {curso.horas}")
                    st.write("---")
            else:
                st.info("No hay cursos registrados.")

        with tabs[1]:  # Publicaciones
            if selected_form.publicaciones:
                for i, pub in enumerate(selected_form.publicaciones, 1):
                    st.write(f"**Publicación {i}:**")
                    st.write(f"- Autores: {pub.autores}")
                    st.write(f"- Título: {pub.titulo}")
                    st.write(f"- Evento/Revista: {pub.evento_revista}")
                    st.write(f"- Estatus: {pub.estatus.value}")
                    st.write("---")
            else:
                st.info("No hay publicaciones registradas.")

        with tabs[2]:  # Eventos
            if selected_form.eventos_academicos:
                for i, evento in enumerate(selected_form.eventos_academicos, 1):
                    st.write(f"**Evento {i}:**")
                    st.write(f"- Nombre: {evento.nombre_evento}")
                    st.write(f"- Fecha: {evento.fecha}")
                    st.write(
                        f"- Tipo de participación: {evento.tipo_participacion.value}")
                    st.write("---")
            else:
                st.info("No hay eventos registrados.")

        with tabs[3]:  # Diseño Curricular
            if selected_form.diseno_curricular:
                for i, diseno in enumerate(selected_form.diseno_curricular, 1):
                    st.write(f"**Diseño {i}:**")
                    st.write(f"- Curso: {diseno.nombre_curso}")
                    if diseno.descripcion:
                        st.write(f"- Descripción: {diseno.descripcion}")
                    st.write("---")
            else:
                st.info("No hay diseños curriculares registrados.")

        with tabs[4]:  # Movilidad
            if selected_form.movilidad:
                for i, mov in enumerate(selected_form.movilidad, 1):
                    st.write(f"**Movilidad {i}:**")
                    st.write(f"- Descripción: {mov.descripcion}")
                    st.write(f"- Tipo: {mov.tipo.value}")
                    st.write(f"- Fecha: {mov.fecha}")
                    st.write("---")
            else:
                st.info("No hay experiencias de movilidad registradas.")

        with tabs[5]:  # Reconocimientos
            if selected_form.reconocimientos:
                for i, rec in enumerate(selected_form.reconocimientos, 1):
                    st.write(f"**Reconocimiento {i}:**")
                    st.write(f"- Nombre: {rec.nombre}")
                    st.write(f"- Tipo: {rec.tipo.value}")
                    st.write(f"- Fecha: {rec.fecha}")
                    st.write("---")
            else:
                st.info("No hay reconocimientos registrados.")

        with tabs[6]:  # Certificaciones
            if selected_form.certificaciones:
                for i, cert in enumerate(selected_form.certificaciones, 1):
                    st.write(f"**Certificación {i}:**")
                    st.write(f"- Nombre: {cert.nombre}")
                    st.write(f"- Fecha obtención: {cert.fecha_obtencion}")
                    st.write("---")
            else:
                st.info("No hay certificaciones registradas.")

        # Action buttons
        st.subheader("⚡ Acciones")

        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            if st.button("✅ Aprobar", type="primary", key=f"approve_{selected_form.id}"):
                if approve_form(selected_form.id):
                    st.success("Formulario aprobado exitosamente!")
                    st.cache_data.clear()  # Clear cache to refresh data
                    st.rerun()
                else:
                    st.error("Error al aprobar el formulario.")

        with col2:
            if st.button("❌ Rechazar", key=f"reject_{selected_form.id}"):
                comment = st.text_area(
                    "Comentario (opcional):", key=f"comment_{selected_form.id}")
                if st.button("Confirmar Rechazo", key=f"confirm_reject_{selected_form.id}"):
                    if reject_form(selected_form.id, comment):
                        st.success("Formulario rechazado.")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Error al rechazar el formulario.")


def show_detailed_metrics(all_forms, metrics):
    """Show detailed metrics and analytics"""

    st.header("📊 Métricas Detalladas")

    # Time period selector
    col1, col2 = st.columns(2)

    with col1:
        year = st.selectbox("Año:", [2024, 2025], index=1)

    with col2:
        quarter = st.selectbox("Trimestre (opcional):", [
                               "Todos", "Q1", "Q2", "Q3", "Q4"])

    # Process data
    db = SessionLocal()
    try:
        processor = DataProcessor(db)
        calculator = MetricsCalculator(db)

        # Convert forms to DataFrame
        if all_forms:
            raw_data = []
            for form in all_forms:
                raw_data.append({
                    'id': form.id,
                    'nombre_completo': form.nombre_completo,
                    'correo_institucional': form.correo_institucional,
                    'estado': form.estado.value,
                    'fecha_envio': form.fecha_envio,
                    'year': form.fecha_envio.year if form.fecha_envio else None,
                    'quarter': (form.fecha_envio.month - 1) // 3 + 1 if form.fecha_envio else None
                })

            df = processor.clean_data(raw_data)

            # Calculate metrics based on selection
            if quarter != "Todos":
                quarter_num = int(quarter[1])
                period_metrics = calculator.calculate_quarterly_metrics(
                    df, quarter_num, year)
                st.subheader(f"📈 Métricas para {quarter} {year}")
            else:
                period_metrics = calculator.calculate_annual_metrics(df, year)
                st.subheader(f"📈 Métricas Anuales {year}")

            # Display metrics
            col1, col2 = st.columns(2)

            with col1:
                st.metric("Formularios Procesados", period_metrics.get(
                    'formularios_procesados', 0))

                # Show activity summary if available
                if 'resumen_actividades' in period_metrics:
                    st.write("**Resumen de Actividades:**")
                    resumen = period_metrics['resumen_actividades']

                    if 'capacitacion' in resumen:
                        cap = resumen['capacitacion']
                        st.write(
                            f"- Cursos: {cap.get('total_cursos', 0)} ({cap.get('total_horas', 0)} horas)")

                    if 'investigacion' in resumen:
                        inv = resumen['investigacion']
                        st.write(
                            f"- Publicaciones: {inv.get('total_publicaciones', 0)}")

                    if 'eventos_academicos' in resumen:
                        evt = resumen['eventos_academicos']
                        st.write(f"- Eventos: {evt.get('total_eventos', 0)}")

            with col2:
                # Show highlights if available
                if 'destacados' in period_metrics:
                    st.write("**Destacados:**")
                    for highlight in period_metrics['destacados']:
                        st.write(f"- {highlight}")

                # Show comparison if available
                if 'comparacion_anterior' in period_metrics:
                    st.write("**Comparación con período anterior:**")
                    comp = period_metrics['comparacion_anterior']
                    if 'cambios' in comp:
                        for activity, change in comp['cambios'].items():
                            if change > 0:
                                st.write(f"- {activity}: +{change}% 📈")
                            elif change < 0:
                                st.write(f"- {activity}: {change}% 📉")
                            else:
                                st.write(f"- {activity}: Sin cambios ➡️")

        else:
            st.info("No hay datos disponibles para el análisis.")

    finally:
        db.close()


def show_data_analysis(all_forms):
    """Show advanced data analysis"""

    st.header("🔍 Análisis de Datos")

    if not all_forms:
        st.info("No hay datos disponibles para análisis.")
        return

    # Data processing
    db = SessionLocal()
    try:
        processor = DataProcessor(db)

        # Convert to DataFrame
        raw_data = []
        for form in all_forms:
            raw_data.append({
                'id': form.id,
                'nombre_completo': form.nombre_completo,
                'correo_institucional': form.correo_institucional,
                'estado': form.estado.value,
                'fecha_envio': form.fecha_envio,
                'year': form.fecha_envio.year if form.fecha_envio else None,
                'month': form.fecha_envio.month if form.fecha_envio else None
            })

        df = processor.clean_data(raw_data)
        df_with_duplicates = processor.detect_duplicates(df)

        # Analysis tabs
        tab1, tab2, tab3 = st.tabs(
            ["Tendencias Temporales", "Calidad de Datos", "Estadísticas Generales"])

        with tab1:
            st.subheader("📈 Tendencias Temporales")

            if 'month' in df.columns and 'year' in df.columns:
                # Monthly submissions chart
                monthly_counts = df.groupby(
                    ['year', 'month']).size().reset_index(name='count')
                monthly_counts['period'] = monthly_counts['year'].astype(
                    str) + '-' + monthly_counts['month'].astype(str).str.zfill(2)

                fig_trend = px.line(
                    monthly_counts,
                    x='period',
                    y='count',
                    title='Formularios Enviados por Mes',
                    markers=True
                )
                fig_trend.update_layout(
                    xaxis_title="Período", yaxis_title="Cantidad de Formularios")
                st.plotly_chart(fig_trend, use_container_width=True)

                # Status distribution over time
                if 'estado' in df.columns:
                    status_time = df.groupby(
                        ['year', 'month', 'estado']).size().reset_index(name='count')
                    status_time['period'] = status_time['year'].astype(
                        str) + '-' + status_time['month'].astype(str).str.zfill(2)

                    fig_status = px.bar(
                        status_time,
                        x='period',
                        y='count',
                        color='estado',
                        title='Distribución de Estados por Mes',
                        color_discrete_map={
                            'PENDIENTE': '#ff9800',
                            'APROBADO': '#4caf50',
                            'RECHAZADO': '#f44336'
                        }
                    )
                    st.plotly_chart(fig_status, use_container_width=True)

        with tab2:
            st.subheader("🔍 Calidad de Datos")

            # Duplicate detection results
            if 'is_duplicate' in df_with_duplicates.columns:
                duplicates_count = df_with_duplicates['is_duplicate'].sum()
                st.metric("Posibles Duplicados Detectados", duplicates_count)

                if duplicates_count > 0:
                    st.warning(
                        f"Se detectaron {duplicates_count} posibles registros duplicados.")

                    # Show duplicate groups
                    duplicate_records = df_with_duplicates[df_with_duplicates['is_duplicate'] == True]
                    if not duplicate_records.empty:
                        st.write("**Registros Duplicados:**")
                        st.dataframe(duplicate_records[[
                                     'id', 'nombre_completo', 'correo_institucional', 'duplicate_group']])
                else:
                    st.success("No se detectaron duplicados.")

            # Data completeness
            st.write("**Completitud de Datos:**")
            completeness = {}
            for col in ['nombre_completo', 'correo_institucional']:
                if col in df.columns:
                    non_null = df[col].notna().sum()
                    total = len(df)
                    completeness[col] = (non_null / total) * \
                        100 if total > 0 else 0

            for field, percentage in completeness.items():
                st.progress(percentage / 100,
                            text=f"{field}: {percentage:.1f}%")

        with tab3:
            st.subheader("📊 Estadísticas Generales")

            # Generate statistics
            try:
                stats = processor.generate_statistics(df)

                if 'resumen_general' in stats:
                    resumen = stats['resumen_general']

                    col1, col2 = st.columns(2)

                    with col1:
                        st.write("**Resumen General:**")
                        st.write(
                            f"- Total registros: {resumen.get('total_registros', 0)}")
                        if resumen.get('periodo_inicio'):
                            st.write(
                                f"- Período inicio: {resumen['periodo_inicio'][:10]}")
                        if resumen.get('periodo_fin'):
                            st.write(
                                f"- Período fin: {resumen['periodo_fin'][:10]}")
                        st.write(
                            f"- Promedio mensual: {resumen.get('promedio_mensual', 0):.1f}")

                    with col2:
                        if 'estados_distribucion' in resumen:
                            st.write("**Distribución por Estado:**")
                            for estado, count in resumen['estados_distribucion'].items():
                                st.write(f"- {estado}: {count}")

                if 'calidad_datos' in stats:
                    st.write("**Calidad de Datos:**")
                    calidad = stats['calidad_datos']
                    for field, metrics in calidad.items():
                        if isinstance(metrics, dict):
                            st.write(
                                f"- {field}: {metrics.get('completitud', 0):.1f}% completo")

            except Exception as e:
                st.error(f"Error al generar estadísticas: {e}")

    finally:
        db.close()


def show_data_export(all_forms):
    """Show data export options"""

    st.header("📤 Exportar Datos")

    if not all_forms:
        st.info("No hay datos disponibles para exportar.")
        return

    # Export options
    col1, col2 = st.columns(2)

    with col1:
        export_format = st.selectbox("Formato de exportación:", [
                                     "CSV", "Excel", "JSON"])

    with col2:
        status_filter = st.selectbox("Filtrar por estado:", [
                                     "Todos", "APROBADO", "PENDIENTE", "RECHAZADO"])

    # Filter data
    filtered_forms = all_forms
    if status_filter != "Todos":
        filtered_forms = [
            f for f in all_forms if f.estado.value == status_filter]

    st.info(f"Se exportarán {len(filtered_forms)} registros.")

    if st.button("🔄 Generar Exportación"):
        try:
            # Prepare data for export
            export_data = []
            for form in filtered_forms:
                export_data.append({
                    'ID': form.id,
                    'Nombre Completo': form.nombre_completo,
                    'Correo Institucional': form.correo_institucional,
                    'Estado': form.estado.value,
                    'Fecha Envío': form.fecha_envio.strftime('%Y-%m-%d %H:%M') if form.fecha_envio else '',
                    'Fecha Revisión': form.fecha_revision.strftime('%Y-%m-%d %H:%M') if form.fecha_revision else '',
                    'Estado Revisión': 'Revisado' if form.revisado_por else 'Pendiente',
                    'Cursos': len(form.cursos_capacitacion),
                    'Publicaciones': len(form.publicaciones),
                    'Eventos': len(form.eventos_academicos),
                    'Diseños Curriculares': len(form.diseno_curricular),
                    'Movilidades': len(form.movilidad),
                    'Reconocimientos': len(form.reconocimientos),
                    'Certificaciones': len(form.certificaciones)
                })

            df_export = pd.DataFrame(export_data)

            if export_format == "CSV":
                csv = df_export.to_csv(index=False)
                st.download_button(
                    label="📥 Descargar CSV",
                    data=csv,
                    file_name=f"reportes_docentes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

            elif export_format == "Excel":
                # For Excel export, we'd need to use BytesIO
                st.info("Funcionalidad de Excel en desarrollo. Use CSV por ahora.")

            elif export_format == "JSON":
                json_data = df_export.to_json(orient='records', indent=2)
                st.download_button(
                    label="📥 Descargar JSON",
                    data=json_data,
                    file_name=f"reportes_docentes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

            st.success("✅ Exportación generada exitosamente!")

            # Show preview
            st.subheader("👀 Vista Previa")
            st.dataframe(df_export.head(10), use_container_width=True)

        except Exception as e:
            st.error(f"Error al generar exportación: {e}")


if __name__ == "__main__":
    main()
