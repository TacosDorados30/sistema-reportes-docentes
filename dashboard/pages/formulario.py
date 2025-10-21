#!/usr/bin/env python3
"""
Formulario público para docentes - Versión corregida
"""

from app.models.audit import AuditActionEnum
from app.core.simple_audit import simple_audit
from app.models.schemas import FormData
from app.database.crud import FormularioCRUD
from app.database.connection import SessionLocal
from app.utils.correction_tokens import CorrectionTokenManager
import streamlit as st
import pandas as pd
from datetime import datetime, date
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Page configuration
st.set_page_config(
    page_title="Formulario Docente - Sistema de Reportes",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ocultar páginas específicas de la barra lateral solo en el formulario público

# Ocultar páginas no deseadas manipulando el registro de páginas
if hasattr(st, 'source_util'):
    try:
        # Obtener las páginas registradas
        pages_to_hide = [
            'advanced_analytics',
            'backup_management',
            'data_export',
            'form_review',
            'report_generation'
        ]

        # Limpiar el registro de páginas para este contexto
        if hasattr(st.source_util, '_pages_cache'):
            st.source_util._pages_cache.clear()
    except:
        pass

# Custom CSS - Ocultar completamente la barra lateral para optimizar recursos
st.markdown("""
<style>
    /* Ocultar completamente la barra lateral */
    .css-1d391kg, .css-1lcbmhc, .css-1cypcdb, .css-17eq0hr, 
    [data-testid="stSidebar"], .stSidebar, section[data-testid="stSidebar"] {
        display: none !important;
        visibility: hidden !important;
        width: 0px !important;
        min-width: 0px !important;
    }
    
    /* Ocultar botón de toggle de la barra lateral */
    .css-1rs6os, .css-17ziqus, [data-testid="collapsedControl"],
    button[kind="header"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Expandir contenido principal a pantalla completa */
    .css-18e3th9, .css-1d391kg, .main, .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-left: 0rem !important;
        max-width: 100% !important;
    }
    
    /* Estilos del formulario */
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.3rem;
        color: #2e7d32;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #2e7d32;
        padding-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'cursos' not in st.session_state:
        st.session_state.cursos = []
    if 'publicaciones' not in st.session_state:
        st.session_state.publicaciones = []
    if 'eventos' not in st.session_state:
        st.session_state.eventos = []
    if 'disenos' not in st.session_state:
        st.session_state.disenos = []
    if 'movilidades' not in st.session_state:
        st.session_state.movilidades = []
    if 'reconocimientos' not in st.session_state:
        st.session_state.reconocimientos = []
    if 'certificaciones' not in st.session_state:
        st.session_state.certificaciones = []
    if 'show_info_box' not in st.session_state:
        st.session_state.show_info_box = True


def show_info_box():
    """Show dismissible info box"""
    if st.session_state.show_info_box:
        col1, col2 = st.columns([20, 1])

        with col1:
            st.info("""
            **🎯 Bienvenido al Sistema de Reportes Docentes**
            
            Complete este formulario para registrar sus actividades académicas del período actual. 
            Toda la información será revisada por el área administrativa correspondiente.
            
            **Instrucciones importantes:**
            - Los campos marcados con (*) son obligatorios
            - **Debe completar al menos UNA sección** de actividades académicas
            - No es necesario llenar todas las secciones - solo las que apliquen a su caso
            - Algunos docentes pueden tener solo certificaciones, otros solo cursos, etc.
            """)

        with col2:
            # Botón de cerrar mejorado
            if st.button("✕", key="close_info_btn", help="Cerrar mensaje informativo", type="secondary"):
                st.session_state.show_info_box = False


def show_personal_info():
    """Show personal information section"""
    st.header("👤 Información Personal")

    # Obtener lista de maestros autorizados
    db = SessionLocal()
    try:
        from app.database.crud import MaestroAutorizadoCRUD
        maestros_crud = MaestroAutorizadoCRUD(db)
        maestros_options = maestros_crud.get_maestros_options()
    except Exception as e:
        st.error(f"Error al cargar lista de maestros: {e}")
        maestros_options = {}
    finally:
        db.close()

    if not maestros_options:
        st.error("⚠️ **No hay maestros autorizados registrados**")
        st.markdown("""
        **Para poder usar este formulario:**
        
        1. Un administrador debe agregar maestros autorizados al sistema
        2. Contacte al administrador para que agregue su nombre y correo
        3. Una vez agregado, podrá seleccionar su nombre de la lista
        
        **Administradores:** Vayan a la página "Maestros Autorizados" en el dashboard para agregar maestros.
        """)
        st.stop()

    col1, col2 = st.columns(2)

    with col1:
        # Usar datos de corrección si están disponibles
        default_nombre = st.session_state.get('nombre_completo_correction', '')
        
        # Encontrar el índice del maestro por defecto
        maestros_list = list(maestros_options.keys())
        default_index = 0
        if default_nombre and default_nombre in maestros_list:
            default_index = maestros_list.index(default_nombre)
        
        selected_maestro = st.selectbox(
            "Seleccione su nombre *",
            options=maestros_list,
            index=default_index,
            help="Seleccione su nombre de la lista de maestros autorizados",
            key="maestro_selector"
        )
        
        # El nombre completo es el seleccionado
        nombre_completo = selected_maestro
        
        # Actualizar el correo en session_state cuando cambie la selección del maestro
        if selected_maestro and selected_maestro in maestros_options:
            # Solo actualizar si no estamos en modo corrección o si el correo actual está vacío
            if not st.session_state.get('correo_institucional_correction') or not st.session_state.get('correo_input', ''):
                st.session_state.suggested_email = maestros_options[selected_maestro]

    with col2:
        # El correo se pre-llena automáticamente pero es editable
        default_correo = st.session_state.get('correo_institucional_correction', '')
        
        # Si no hay correo de corrección, usar el sugerido o el del maestro seleccionado
        if not default_correo:
            default_correo = st.session_state.get('suggested_email', '')
            if not default_correo and selected_maestro and selected_maestro in maestros_options:
                default_correo = maestros_options[selected_maestro]
        
        correo_institucional = st.text_input(
            "Correo Institucional *",
            value=default_correo,
            placeholder="Ej: juan.perez@universidad.edu.mx",
            help="Correo pre-llenado según el maestro seleccionado, pero puede editarlo si es necesario",
            key="correo_input"
        )
        
        # Mostrar sugerencia si el correo no coincide con el del maestro seleccionado
        if selected_maestro and selected_maestro in maestros_options:
            suggested_email = maestros_options[selected_maestro]
            if correo_institucional and correo_institucional != suggested_email:
                st.info(f"💡 Correo sugerido para {selected_maestro}: {suggested_email}")
                if st.button("📧 Usar correo sugerido", key="use_suggested_email"):
                    st.session_state.suggested_email = suggested_email
                    st.rerun()

    # Período académico
    st.subheader("📅 Período Académico")
    col3, col4 = st.columns(2)

    with col3:
        # Usar datos de corrección si están disponibles
        default_año = st.session_state.get('año_academico_correction', datetime.now().year)
        año_academico = st.number_input(
            "Año Académico *",
            min_value=2020,
            max_value=2050,
            value=default_año,
            step=1,
            key="year_input_simple",
            help="Use las flechitas del campo o escriba directamente el año"
        )

    with col4:
        default_trimestre = st.session_state.get('trimestre_correction', 'Trimestre 1')
        trimestre_options = ["Trimestre 1", "Trimestre 2", "Trimestre 3", "Trimestre 4"]
        default_index = 0
        if default_trimestre in trimestre_options:
            default_index = trimestre_options.index(default_trimestre)
        
        trimestre = st.selectbox(
            "Trimestre *",
            options=trimestre_options,
            index=default_index,
            help="Seleccione el trimestre académico"
        )

    return nombre_completo, correo_institucional, año_academico, trimestre


def show_cursos_section():
    """Show courses and training section"""
    st.header("🎓 Cursos y Capacitaciones")
    st.info("📚 **Opcional:** Registre los cursos de capacitación, diplomados, talleres y seminarios en los que ha participado.")

    # Show existing courses
    if st.session_state.cursos:
        st.write("**Cursos Registrados:**")
        for i, curso in enumerate(st.session_state.cursos):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(
                    f"**{curso['nombre_curso']}** - {curso['fecha']} ({curso['horas']} horas)")
            with col2:
                if st.button("🗑️", key=f"del_curso_{i}", help="Eliminar curso"):
                    st.session_state.cursos.pop(i)
                    st.rerun()
        st.divider()

    # Form to add new course
    with st.expander("➕ Agregar Curso de Capacitación", expanded=False):
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            nombre_curso = st.text_input(
                "Nombre del Curso *", key="nuevo_curso_nombre", placeholder="Ej: Metodologías Activas de Aprendizaje")

        with col2:
            fecha_curso = st.date_input(
                "Fecha *", key="nuevo_curso_fecha", max_value=date.today())

        with col3:
            horas_curso = st.number_input(
                "Horas *", min_value=1, max_value=500, value=20, key="nuevo_curso_horas")

        if st.button("➕ Agregar Curso"):
            if nombre_curso and fecha_curso:
                nuevo_curso = {
                    'nombre_curso': nombre_curso,
                    'fecha': fecha_curso,
                    'horas': horas_curso
                }
                st.session_state.cursos.append(nuevo_curso)
                st.success(f"✅ Curso '{nombre_curso}' agregado exitosamente")
                st.rerun()
            else:
                st.error("❌ Por favor complete todos los campos obligatorios")


def show_publicaciones_section():
    """Show publications section"""
    st.header("📚 Publicaciones")
    st.info("📖 **Opcional:** Registre sus artículos, libros, capítulos de libro y otras publicaciones académicas.")

    # Show existing publications
    if st.session_state.publicaciones:
        st.write("**Publicaciones Registradas:**")
        for i, pub in enumerate(st.session_state.publicaciones):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(
                    f"**{pub['titulo']}** - {pub['autores']} ({pub['estatus']})")
                st.write(f"*{pub['evento_revista']}*")
            with col2:
                if st.button("🗑️", key=f"del_pub_{i}", help="Eliminar publicación"):
                    st.session_state.publicaciones.pop(i)
                    st.rerun()
        st.divider()

    # Form to add new publication
    with st.expander("➕ Agregar Publicación", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            autores = st.text_input(
                "Autores", key="nueva_pub_autores", placeholder="Ej: Juan Pérez, María García")
            titulo = st.text_input("Título", key="nueva_pub_titulo")

        with col2:
            evento_revista = st.text_input(
                "Evento/Revista", key="nueva_pub_evento")
            estatus = st.selectbox(
                "Estatus", ["PUBLICADO", "EN_REVISION", "ACEPTADO"], key="nueva_pub_estatus")

        if st.button("➕ Agregar Publicación"):
            if autores and titulo and evento_revista:
                nueva_pub = {
                    'autores': autores,
                    'titulo': titulo,
                    'evento_revista': evento_revista,
                    'estatus': estatus
                }
                st.session_state.publicaciones.append(nueva_pub)
                st.success(f"✅ Publicación '{titulo}' agregada exitosamente")
                st.rerun()
            else:
                st.error("❌ Por favor complete todos los campos obligatorios")


def show_eventos_section():
    """Show academic events section"""
    st.header("🎤 Eventos Académicos")
    st.info("🎯 **Opcional:** Registre su participación en congresos, seminarios, conferencias y otros eventos académicos.")

    # Show existing events
    if st.session_state.eventos:
        st.write("**Eventos Registrados:**")
        for i, evento in enumerate(st.session_state.eventos):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(
                    f"**{evento['nombre_evento']}** - {evento['fecha']} ({evento['tipo_participacion']})")
            with col2:
                if st.button("🗑️", key=f"del_evento_{i}", help="Eliminar evento"):
                    st.session_state.eventos.pop(i)
                    st.rerun()
        st.divider()

    # Form to add new event
    with st.expander("➕ Agregar Evento Académico", expanded=False):
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            nombre_evento = st.text_input(
                "Nombre del Evento", key="nuevo_evento_nombre")

        with col2:
            fecha_evento = st.date_input("Fecha", key="nuevo_evento_fecha")

        with col3:
            tipo_participacion = st.selectbox(
                "Tipo de Participación",
                ["PONENTE", "PARTICIPANTE", "ORGANIZADOR"],
                key="nuevo_evento_tipo"
            )

        if st.button("➕ Agregar Evento"):
            if nombre_evento and fecha_evento:
                nuevo_evento = {
                    'nombre_evento': nombre_evento,
                    'fecha': fecha_evento,
                    'tipo_participacion': tipo_participacion
                }
                st.session_state.eventos.append(nuevo_evento)
                st.success(f"✅ Evento '{nombre_evento}' agregado exitosamente")
                st.rerun()
            else:
                st.error("❌ Por favor complete todos los campos obligatorios")


def show_diseno_curricular():
    """Show curriculum design section"""
    st.header("📖 Diseño Curricular")
    st.info("📋 **Opcional:** Registre los cursos, programas o planes de estudio que ha diseñado o actualizado.")

    # Show existing designs
    if st.session_state.disenos:
        st.write("**Diseños Curriculares Registrados:**")
        for i, diseno in enumerate(st.session_state.disenos):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{diseno['nombre_curso']}**")
                if diseno['descripcion']:
                    st.write(f"*{diseno['descripcion']}*")
            with col2:
                if st.button("🗑️", key=f"del_diseno_{i}", help="Eliminar diseño"):
                    st.session_state.disenos.pop(i)
                    st.rerun()
        st.divider()

    # Form to add new design
    with st.expander("➕ Agregar Diseño Curricular", expanded=False):
        nombre_curso_diseno = st.text_input(
            "Nombre del Curso/Programa", key="nuevo_diseno_nombre")
        descripcion_diseno = st.text_area(
            "Descripción", key="nuevo_diseno_desc", height=100)

        if st.button("➕ Agregar Diseño"):
            if nombre_curso_diseno:
                nuevo_diseno = {
                    'nombre_curso': nombre_curso_diseno,
                    'descripcion': descripcion_diseno
                }
                st.session_state.disenos.append(nuevo_diseno)
                st.success(
                    f"✅ Diseño '{nombre_curso_diseno}' agregado exitosamente")
                st.rerun()
            else:
                st.error("❌ Por favor ingrese el nombre del curso/programa")


def show_movilidad():
    """Show academic mobility section"""
    st.header("✈️ Experiencias de Movilidad")
    st.info("🌍 **Opcional:** Registre sus estancias de investigación, intercambios académicos y experiencias de movilidad.")

    # Show existing mobility experiences
    if st.session_state.movilidades:
        st.write("**Experiencias de Movilidad Registradas:**")
        for i, movilidad in enumerate(st.session_state.movilidades):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(
                    f"**{movilidad['descripcion']}** - {movilidad['fecha']} ({movilidad['tipo']})")
            with col2:
                if st.button("🗑️", key=f"del_movilidad_{i}", help="Eliminar movilidad"):
                    st.session_state.movilidades.pop(i)
                    st.rerun()
        st.divider()

    # Form to add new mobility
    with st.expander("➕ Agregar Experiencia de Movilidad", expanded=False):
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            descripcion_movilidad = st.text_input(
                "Descripción", key="nueva_movilidad_desc")

        with col2:
            tipo_movilidad = st.selectbox(
                "Tipo", ["NACIONAL", "INTERNACIONAL"], key="nueva_movilidad_tipo")

        with col3:
            fecha_movilidad = st.date_input(
                "Fecha", key="nueva_movilidad_fecha")

        if st.button("➕ Agregar Movilidad"):
            if descripcion_movilidad and fecha_movilidad:
                nueva_movilidad = {
                    'descripcion': descripcion_movilidad,
                    'tipo': tipo_movilidad,
                    'fecha': fecha_movilidad
                }
                st.session_state.movilidades.append(nueva_movilidad)
                st.success(f"✅ Movilidad agregada exitosamente")
                st.rerun()
            else:
                st.error("❌ Por favor complete todos los campos obligatorios")


def show_reconocimientos():
    """Show recognitions section"""
    st.header("🏆 Reconocimientos")
    st.info("🎖️ **Opcional:** Registre los premios, distinciones y reconocimientos que ha recibido.")

    # Show existing recognitions
    if st.session_state.reconocimientos:
        st.write("**Reconocimientos Registrados:**")
        for i, reconocimiento in enumerate(st.session_state.reconocimientos):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(
                    f"**{reconocimiento['nombre']}** - {reconocimiento['fecha']} ({reconocimiento['tipo']})")
            with col2:
                if st.button("🗑️", key=f"del_reconocimiento_{i}", help="Eliminar reconocimiento"):
                    st.session_state.reconocimientos.pop(i)
                    st.rerun()
        st.divider()

    # Form to add new recognition
    with st.expander("➕ Agregar Reconocimiento", expanded=False):
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            nombre_reconocimiento = st.text_input(
                "Nombre del Reconocimiento", key="nuevo_reconocimiento_nombre")

        with col2:
            tipo_reconocimiento = st.selectbox(
                "Tipo", ["GRADO", "PREMIO", "DISTINCION"], key="nuevo_reconocimiento_tipo")

        with col3:
            fecha_reconocimiento = st.date_input(
                "Fecha", key="nuevo_reconocimiento_fecha")

        if st.button("➕ Agregar Reconocimiento"):
            if nombre_reconocimiento and fecha_reconocimiento:
                nuevo_reconocimiento = {
                    'nombre': nombre_reconocimiento,
                    'tipo': tipo_reconocimiento,
                    'fecha': fecha_reconocimiento
                }
                st.session_state.reconocimientos.append(nuevo_reconocimiento)
                st.success(
                    f"✅ Reconocimiento '{nombre_reconocimiento}' agregado exitosamente")
                st.rerun()
            else:
                st.error("❌ Por favor complete todos los campos obligatorios")


def show_certificaciones():
    """Show certifications section"""
    st.header("📜 Certificaciones")
    st.info("🎓 **Opcional:** Registre sus certificaciones profesionales, técnicas y especializadas.")

    # Show existing certifications
    if st.session_state.certificaciones:
        st.write("**Certificaciones Registradas:**")
        for i, cert in enumerate(st.session_state.certificaciones):
            col1, col2 = st.columns([4, 1])
            with col1:
                vigencia = "✅ Vigente" if cert['vigente'] else "❌ Vencida"
                vencimiento = f" (Vence: {cert['fecha_vencimiento']})" if cert['fecha_vencimiento'] else ""
                st.write(
                    f"**{cert['nombre']}** - Obtenida: {cert['fecha_obtencion']} {vigencia}{vencimiento}")
            with col2:
                if st.button("🗑️", key=f"del_cert_{i}", help="Eliminar certificación"):
                    st.session_state.certificaciones.pop(i)
                    st.rerun()
        st.divider()

    # Form to add new certification
    with st.expander("➕ Agregar Certificación", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            nombre_certificacion = st.text_input(
                "Nombre de la Certificación", key="nueva_cert_nombre")
            fecha_obtencion = st.date_input(
                "Fecha de Obtención", key="nueva_cert_obtencion")

        with col2:
            fecha_vencimiento = st.date_input(
                "Fecha de Vencimiento", key="nueva_cert_vencimiento", value=None)
            vigente = st.checkbox(
                "Vigente", key="nueva_cert_vigente", value=True)

        if st.button("➕ Agregar Certificación"):
            if nombre_certificacion and fecha_obtencion:
                nueva_certificacion = {
                    'nombre': nombre_certificacion,
                    'fecha_obtencion': fecha_obtencion,
                    'fecha_vencimiento': fecha_vencimiento,
                    'vigente': vigente
                }
                st.session_state.certificaciones.append(nueva_certificacion)
                st.success(
                    f"✅ Certificación '{nombre_certificacion}' agregada exitosamente")
                st.rerun()
            else:
                st.error("❌ Por favor complete todos los campos obligatorios")


def validate_form(nombre_completo, correo_institucional, año_academico, trimestre):
    """Validate form data"""
    errors = []

    if not nombre_completo or len(nombre_completo.strip()) < 3:
        errors.append(
            "El nombre completo es obligatorio y debe tener al menos 3 caracteres")

    if not correo_institucional or "@" not in correo_institucional:
        errors.append(
            "El correo institucional es obligatorio y debe tener un formato válido")

    # Verificar que el maestro esté autorizado
    db = SessionLocal()
    try:
        from app.database.crud import MaestroAutorizadoCRUD
        maestros_crud = MaestroAutorizadoCRUD(db)
        if not maestros_crud.is_maestro_autorizado(correo_institucional):
            errors.append(
                "Este correo no está autorizado para enviar formularios. Contacte al administrador.")
    except Exception as e:
        errors.append(f"Error verificando autorización: {e}")
    finally:
        db.close()

    if not año_academico:
        errors.append("El año académico es obligatorio")

    if not trimestre:
        errors.append("El trimestre es obligatorio")

    # Check if we have at least some academic activity
    total_activities = (len(st.session_state.cursos) +
                        len(st.session_state.publicaciones) +
                        len(st.session_state.eventos) +
                        len(st.session_state.disenos) +
                        len(st.session_state.movilidades) +
                        len(st.session_state.reconocimientos) +
                        len(st.session_state.certificaciones))

    if total_activities == 0:
        errors.append(
            "Debe agregar al menos una actividad académica en cualquiera de las secciones disponibles")

    return errors


def submit_form(nombre_completo, correo_institucional, año_academico, trimestre):
    """Submit the form to database"""
    try:
        # Create form data
        form_data = FormData(
            nombre_completo=nombre_completo.strip(),
            correo_institucional=correo_institucional.strip(),
            año_academico=año_academico,
            trimestre=trimestre,
            cursos_capacitacion=st.session_state.cursos,
            publicaciones=st.session_state.publicaciones,
            eventos_academicos=st.session_state.eventos,
            diseno_curricular=st.session_state.disenos,
            movilidad=st.session_state.movilidades,
            reconocimientos=st.session_state.reconocimientos,
            certificaciones=st.session_state.certificaciones
        )

        # Save to database
        db = SessionLocal()
        try:
            crud = FormularioCRUD(db)
            
            # Verificar si es una corrección
            if st.session_state.get('is_correction', False) and st.session_state.get('original_form_id'):
                # Crear nueva versión
                formulario = crud.create_formulario_version(
                    original_id=st.session_state.original_form_id,
                    form_data=form_data
                )
                
                # Invalidar token de corrección
                if st.session_state.get('correction_token'):
                    token_manager = CorrectionTokenManager()
                    token_manager.invalidate_token(st.session_state.correction_token)
                
                print(f"Nueva versión creada por {nombre_completo} ({correo_institucional})")
            else:
                # Crear formulario normal
                formulario = crud.create_formulario(form_data)
                print(f"Formulario enviado por {nombre_completo} ({correo_institucional})")

            return formulario.id if formulario else None

        finally:
            db.close()

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        st.error(f"Error al enviar el formulario: {str(e)}")
        st.error(f"Detalles técnicos: {error_details}")
        return None


def clear_form():
    """Clear all form data"""
    st.session_state.cursos = []
    st.session_state.publicaciones = []
    st.session_state.eventos = []
    st.session_state.disenos = []
    st.session_state.movilidades = []
    st.session_state.reconocimientos = []
    st.session_state.certificaciones = []


def load_correction_data(token: str):
    """Carga datos de corrección usando el token"""
    try:
        token_manager = CorrectionTokenManager()
        form_data = token_manager.get_formulario_by_token(token)
        
        if not form_data:
            st.error("❌ Token de corrección inválido o expirado.")
            return
        
        # Cargar datos personales en session_state
        st.session_state.nombre_completo_correction = form_data.get('nombre_completo', '')
        st.session_state.correo_institucional_correction = form_data.get('correo_institucional', '')
        st.session_state.año_academico_correction = form_data.get('año_academico', 2024)
        st.session_state.trimestre_correction = form_data.get('trimestre', 'Primero')
        
        # Cargar actividades
        st.session_state.cursos = form_data.get('cursos_capacitacion', [])
        st.session_state.publicaciones = form_data.get('publicaciones', [])
        st.session_state.eventos = form_data.get('eventos_academicos', [])
        st.session_state.disenos = form_data.get('diseno_curricular', [])
        st.session_state.movilidades = form_data.get('experiencias_movilidad', [])
        st.session_state.reconocimientos = form_data.get('reconocimientos', [])
        st.session_state.certificaciones = form_data.get('certificaciones', [])
        
        # Guardar información de la versión original
        st.session_state.original_form_id = form_data.get('id')
        st.session_state.original_version = form_data.get('version', 1)
        
        # Obtener el estado original para mostrar información
        db = SessionLocal()
        try:
            crud = FormularioCRUD(db)
            original_form = crud.get_formulario(form_data.get('id'))
            if original_form:
                st.session_state.original_estado = original_form.estado.value
        finally:
            db.close()
        
        estado_msg = st.session_state.get('original_estado', 'DESCONOCIDO')
        st.success(f"✅ Datos cargados correctamente. Versión original: {st.session_state.original_version} (Estado: {estado_msg})")
        
    except Exception as e:
        st.error(f"❌ Error cargando datos de corrección: {e}")


def main():
    """Main application"""

    # Initialize session state
    initialize_session_state()
    
    # Verificar si hay un token de corrección en la URL
    try:
        # Intentar la nueva sintaxis de Streamlit
        query_params = st.query_params
        correction_token = query_params.get("token")
        is_correction_mode = query_params.get("mode") == "correction"
    except AttributeError:
        # Usar la sintaxis antigua de Streamlit
        query_params = st.experimental_get_query_params()
        correction_token = query_params.get("token", [None])[0]
        is_correction_mode = query_params.get("mode", [None])[0] == "correction"
    
    # Si hay token de corrección, cargar datos existentes
    if correction_token and is_correction_mode:
        if 'correction_data_loaded' not in st.session_state:
            load_correction_data(correction_token)
            st.session_state.correction_data_loaded = True
            st.session_state.correction_token = correction_token
            st.session_state.is_correction = True

    # Header
    header_text = "🔄 Corrección de Formulario" if is_correction_mode else "📝 Formulario de Actividades Académicas"
    st.markdown(f'<h1 class="main-header">{header_text}</h1>', unsafe_allow_html=True)
    
    # Mostrar información de corrección si aplica
    if is_correction_mode:
        estado_original = st.session_state.get('original_estado', 'DESCONOCIDO')
        
        if estado_original == "APROBADO":
            st.warning("⚠️ **Modo Corrección - Formulario Aprobado:** Su formulario anterior fue aprobado, pero puede hacer correcciones. La nueva versión requerirá aprobación nuevamente.")
        elif estado_original == "RECHAZADO":
            st.info("📝 **Modo Corrección - Formulario Rechazado:** Puede corregir los problemas identificados y reenviar su formulario.")
        else:
            st.info("📝 **Modo Corrección:** Está editando una versión anterior de su formulario. Los campos aparecen pre-llenados con su información anterior.")

    # Info box
    show_info_box()

    # Personal Information
    nombre_completo, correo_institucional, año_academico, trimestre = show_personal_info()

    # Academic Activities Sections
    show_cursos_section()
    show_publicaciones_section()
    show_eventos_section()

    # Other sections as individual sections
    show_diseno_curricular()
    show_movilidad()
    show_reconocimientos()
    show_certificaciones()

    # Submit Section
    st.header("📤 Envío del Formulario")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.button("📤 Enviar Formulario", type="primary", use_container_width=True):
            # Validate form
            errors = validate_form(
                nombre_completo, correo_institucional, año_academico, trimestre)

            if errors:
                st.error("❌ Por favor corrija los siguientes errores:")
                for error in errors:
                    st.error(f"• {error}")
            else:
                # Submit form
                formulario_id = submit_form(
                    nombre_completo, correo_institucional, año_academico, trimestre)

                if formulario_id:
                    # Mensaje diferente para correcciones
                    if st.session_state.get('is_correction', False):
                        estado_original = st.session_state.get('original_estado', 'DESCONOCIDO')
                        
                        if estado_original == "APROBADO":
                            st.success(f"""
                            🔄 **¡Corrección de Formulario Aprobado Enviada!**
                            
                            **ID de Nueva Versión:** {formulario_id}  
                            **Estado:** PENDIENTE (Requiere nueva aprobación)  
                            **Fecha de Corrección:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                            **Versión Anterior:** {st.session_state.get('original_version', 1)} (Estaba APROBADA)
                            
                            ⚠️ **Importante:** Su formulario anterior estaba aprobado, pero esta nueva versión 
                            requerirá aprobación nuevamente. El área administrativa revisará los cambios.
                            """)
                        elif estado_original == "RECHAZADO":
                            st.success(f"""
                            🔄 **¡Corrección Enviada Exitosamente!**
                            
                            **ID de Nueva Versión:** {formulario_id}  
                            **Estado:** PENDIENTE (En revisión)  
                            **Fecha de Corrección:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                            **Versión Anterior:** {st.session_state.get('original_version', 1)} (Estaba RECHAZADA)
                            
                            ✅ Su corrección ha sido recibida. El área administrativa revisará 
                            que se hayan corregido los problemas identificados anteriormente.
                            """)
                        else:
                            st.success(f"""
                            🔄 **¡Corrección Enviada Exitosamente!**
                            
                            **ID de Nueva Versión:** {formulario_id}  
                            **Estado:** PENDIENTE (En revisión)  
                            **Fecha de Corrección:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                            **Versión Anterior:** {st.session_state.get('original_version', 1)}
                            
                            Su corrección ha sido recibida y será revisada por el área administrativa. 
                            Esta nueva versión reemplazará a la anterior una vez aprobada.
                            """)
                    else:
                        st.success(f"""
                        🎉 **¡Formulario Enviado Exitosamente!**
                        
                        **ID de Seguimiento:** {formulario_id}  
                        **Estado:** PENDIENTE (En revisión)  
                        **Fecha de Envío:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                        
                        Su formulario ha sido recibido y será revisado por el área administrativa. 
                        Guarde su ID de seguimiento para futuras consultas.
                        """)

                    # Clear form after successful submission
                    if st.button("🆕 Enviar Otro Formulario"):
                        clear_form()
                        st.rerun()

        if st.button("🗑️ Limpiar Formulario", help="Eliminar todos los datos ingresados"):
            clear_form()
            st.success("✅ Formulario limpiado exitosamente")
            st.rerun()

    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>Sistema de Reportes Docentes v1.0 | 
        Para soporte técnico contacte al área de sistemas</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
