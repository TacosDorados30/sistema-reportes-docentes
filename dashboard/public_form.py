#!/usr/bin/env python3
"""
Formulario público para docentes - Sin autenticación requerida
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connection import SessionLocal
from app.database.crud import FormularioCRUD
from app.models.schemas import FormData
from app.core.simple_audit import simple_audit
from app.models.audit import AuditActionEnum

# Page configuration
st.set_page_config(
    page_title="Formulario Docente - Sistema de Reportes",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2e7d32;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #2e7d32;
        padding-bottom: 0.5rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
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

def show_personal_info():
    """Show personal information section"""
    st.markdown('<div class="section-header">👤 Información Personal</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        nombre_completo = st.text_input(
            "Nombre Completo *",
            placeholder="Ej: Dr. Juan Carlos Pérez García",
            help="Ingrese su nombre completo como aparece en documentos oficiales"
        )
    
    with col2:
        correo_institucional = st.text_input(
            "Correo Institucional *",
            placeholder="Ej: juan.perez@universidad.edu.mx",
            help="Use su correo electrónico institucional oficial"
        )
    
    # Período académico
    st.markdown("### 📅 Período Académico")
    col3, col4 = st.columns(2)
    
    with col3:
        año_academico = st.selectbox(
            "Año Académico *",
            options=[2024, 2025, 2026],
            index=1,  # 2025 por defecto
            help="Seleccione el año académico al que corresponden las actividades"
        )
    
    with col4:
        trimestre = st.selectbox(
            "Trimestre *",
            options=["Trimestre 1", "Trimestre 2", "Trimestre 3"],
            help="Seleccione el trimestre académico"
        )
    
    return nombre_completo, correo_institucional, año_academico, trimestre

def show_cursos_section():
    """Show courses and training section"""
    st.markdown('<div class="section-header">🎓 Cursos y Capacitaciones</div>', unsafe_allow_html=True)
    
    st.info("📚 **Opcional:** Registre los cursos de capacitación, diplomados, talleres y seminarios en los que ha participado.")
    
    # Show existing courses first
    if st.session_state.cursos:
        st.write("**Cursos Registrados:**")
        for i, curso in enumerate(st.session_state.cursos):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{curso['nombre_curso']}** - {curso['fecha']} ({curso['horas']} horas)")
            with col2:
                if st.button("🗑️", key=f"del_curso_{i}", help="Eliminar curso"):
                    st.session_state.cursos.pop(i)
                    st.rerun()
        st.write("---")
    
    # Form to add new course
    with st.expander("➕ Agregar Curso de Capacitación", expanded=False):
        st.write("**Agregar nuevo curso:**")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            nombre_curso = st.text_input("Nombre del Curso *", key="nuevo_curso_nombre", placeholder="Ej: Metodologías Activas de Aprendizaje")
        
        with col2:
            fecha_curso = st.date_input("Fecha *", key="nuevo_curso_fecha", max_value=date.today())
        
        with col3:
            horas_curso = st.number_input("Horas *", min_value=1, max_value=500, value=20, key="nuevo_curso_horas")
        
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
    st.markdown('<div class="section-header">📚 Publicaciones</div>', unsafe_allow_html=True)
    
    st.info("📖 **Opcional:** Registre sus artículos, libros, capítulos de libro y otras publicaciones académicas.")
    
    # Form to add new publication
    with st.expander("➕ Agregar Publicación", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            autores = st.text_input("Autores", key="nueva_pub_autores", placeholder="Ej: Juan Pérez, María García")
            titulo = st.text_input("Título", key="nueva_pub_titulo")
        
        with col2:
            evento_revista = st.text_input("Evento/Revista", key="nueva_pub_evento")
            estatus = st.selectbox("Estatus", ["PUBLICADO", "EN_REVISION", "ACEPTADO"], key="nueva_pub_estatus")
        
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
    
    # Show existing publications
    if st.session_state.publicaciones:
        st.write("**Publicaciones Registradas:**")
        for i, pub in enumerate(st.session_state.publicaciones):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{pub['titulo']}** - {pub['autores']} ({pub['estatus']})")
                st.write(f"*{pub['evento_revista']}*")
            with col2:
                if st.button("🗑️", key=f"del_pub_{i}", help="Eliminar publicación"):
                    st.session_state.publicaciones.pop(i)
                    st.rerun()

def show_eventos_section():
    """Show academic events section"""
    st.markdown('<div class="section-header">🎤 Eventos Académicos</div>', unsafe_allow_html=True)
    
    st.info("🎯 **Opcional:** Registre su participación en congresos, seminarios, conferencias y otros eventos académicos.")
    
    # Form to add new event
    with st.expander("➕ Agregar Evento Académico", expanded=False):
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            nombre_evento = st.text_input("Nombre del Evento", key="nuevo_evento_nombre")
        
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
    
    # Show existing events
    if st.session_state.eventos:
        st.write("**Eventos Registrados:**")
        for i, evento in enumerate(st.session_state.eventos):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{evento['nombre_evento']}** - {evento['fecha']} ({evento['tipo_participacion']})")
            with col2:
                if st.button("🗑️", key=f"del_evento_{i}", help="Eliminar evento"):
                    st.session_state.eventos.pop(i)
                    st.rerun()

def show_diseno_section():
    """Show curriculum design section"""
    st.markdown('<div class="section-header">📖 Diseño Curricular</div>', unsafe_allow_html=True)
    
    st.info("📋 **Opcional:** Registre los cursos, programas o planes de estudio que ha diseñado o actualizado.")
    
    # Form to add new design
    with st.expander("➕ Agregar Diseño Curricular", expanded=False):
        nombre_curso_diseno = st.text_input("Nombre del Curso/Programa", key="nuevo_diseno_nombre")
        descripcion_diseno = st.text_area("Descripción", key="nuevo_diseno_desc", height=100)
        
        if st.button("➕ Agregar Diseño"):
            if nombre_curso_diseno:
                nuevo_diseno = {
                    'nombre_curso': nombre_curso_diseno,
                    'descripcion': descripcion_diseno
                }
                st.session_state.disenos.append(nuevo_diseno)
                st.success(f"✅ Diseño '{nombre_curso_diseno}' agregado exitosamente")
                st.rerun()
            else:
                st.error("❌ Por favor ingrese el nombre del curso/programa")
    
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

def show_movilidad_section():
    """Show academic mobility section"""
    st.markdown('<div class="section-header">✈️ Experiencias de Movilidad</div>', unsafe_allow_html=True)
    
    st.info("🌍 **Opcional:** Registre sus estancias de investigación, intercambios académicos y experiencias de movilidad.")
    
    # Form to add new mobility
    with st.expander("➕ Agregar Experiencia de Movilidad", expanded=False):
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            descripcion_movilidad = st.text_input("Descripción", key="nueva_movilidad_desc")
        
        with col2:
            tipo_movilidad = st.selectbox("Tipo", ["NACIONAL", "INTERNACIONAL"], key="nueva_movilidad_tipo")
        
        with col3:
            fecha_movilidad = st.date_input("Fecha", key="nueva_movilidad_fecha")
        
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
    
    # Show existing mobility experiences
    if st.session_state.movilidades:
        st.write("**Experiencias de Movilidad Registradas:**")
        for i, movilidad in enumerate(st.session_state.movilidades):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{movilidad['descripcion']}** - {movilidad['fecha']} ({movilidad['tipo']})")
            with col2:
                if st.button("🗑️", key=f"del_movilidad_{i}", help="Eliminar movilidad"):
                    st.session_state.movilidades.pop(i)
                    st.rerun()

def show_reconocimientos_section():
    """Show recognitions section"""
    st.markdown('<div class="section-header">🏆 Reconocimientos</div>', unsafe_allow_html=True)
    
    st.info("🎖️ **Opcional:** Registre los premios, distinciones y reconocimientos que ha recibido.")
    
    # Form to add new recognition
    with st.expander("➕ Agregar Reconocimiento", expanded=False):
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            nombre_reconocimiento = st.text_input("Nombre del Reconocimiento", key="nuevo_reconocimiento_nombre")
        
        with col2:
            tipo_reconocimiento = st.selectbox("Tipo", ["GRADO", "PREMIO", "DISTINCION"], key="nuevo_reconocimiento_tipo")
        
        with col3:
            fecha_reconocimiento = st.date_input("Fecha", key="nuevo_reconocimiento_fecha")
        
        if st.button("➕ Agregar Reconocimiento"):
            if nombre_reconocimiento and fecha_reconocimiento:
                nuevo_reconocimiento = {
                    'nombre': nombre_reconocimiento,
                    'tipo': tipo_reconocimiento,
                    'fecha': fecha_reconocimiento
                }
                st.session_state.reconocimientos.append(nuevo_reconocimiento)
                st.success(f"✅ Reconocimiento '{nombre_reconocimiento}' agregado exitosamente")
                st.rerun()
            else:
                st.error("❌ Por favor complete todos los campos obligatorios")
    
    # Show existing recognitions
    if st.session_state.reconocimientos:
        st.write("**Reconocimientos Registrados:**")
        for i, reconocimiento in enumerate(st.session_state.reconocimientos):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{reconocimiento['nombre']}** - {reconocimiento['fecha']} ({reconocimiento['tipo']})")
            with col2:
                if st.button("🗑️", key=f"del_reconocimiento_{i}", help="Eliminar reconocimiento"):
                    st.session_state.reconocimientos.pop(i)
                    st.rerun()

def show_certificaciones_section():
    """Show certifications section"""
    st.markdown('<div class="section-header">📜 Certificaciones</div>', unsafe_allow_html=True)
    
    st.info("🎓 **Opcional:** Registre sus certificaciones profesionales, técnicas y especializadas.")
    
    # Form to add new certification
    with st.expander("➕ Agregar Certificación", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_certificacion = st.text_input("Nombre de la Certificación", key="nueva_cert_nombre")
            fecha_obtencion = st.date_input("Fecha de Obtención", key="nueva_cert_obtencion")
        
        with col2:
            fecha_vencimiento = st.date_input("Fecha de Vencimiento", key="nueva_cert_vencimiento", value=None)
            vigente = st.checkbox("Vigente", key="nueva_cert_vigente", value=True)
        
        if st.button("➕ Agregar Certificación"):
            if nombre_certificacion and fecha_obtencion:
                nueva_certificacion = {
                    'nombre': nombre_certificacion,
                    'fecha_obtencion': fecha_obtencion,
                    'fecha_vencimiento': fecha_vencimiento,
                    'vigente': vigente
                }
                st.session_state.certificaciones.append(nueva_certificacion)
                st.success(f"✅ Certificación '{nombre_certificacion}' agregada exitosamente")
                st.rerun()
            else:
                st.error("❌ Por favor complete todos los campos obligatorios")
    
    # Show existing certifications
    if st.session_state.certificaciones:
        st.write("**Certificaciones Registradas:**")
        for i, cert in enumerate(st.session_state.certificaciones):
            col1, col2 = st.columns([4, 1])
            with col1:
                vigencia = "✅ Vigente" if cert['vigente'] else "❌ Vencida"
                vencimiento = f" (Vence: {cert['fecha_vencimiento']})" if cert['fecha_vencimiento'] else ""
                st.write(f"**{cert['nombre']}** - Obtenida: {cert['fecha_obtencion']} {vigencia}{vencimiento}")
            with col2:
                if st.button("🗑️", key=f"del_cert_{i}", help="Eliminar certificación"):
                    st.session_state.certificaciones.pop(i)
                    st.rerun()

def validate_form(nombre_completo, correo_institucional, año_academico, trimestre):
    """Validate form data"""
    errors = []
    
    if not nombre_completo or len(nombre_completo.strip()) < 3:
        errors.append("El nombre completo es obligatorio y debe tener al menos 3 caracteres")
    
    if not correo_institucional or "@" not in correo_institucional:
        errors.append("El correo institucional es obligatorio y debe tener un formato válido")
    
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
        errors.append("Debe agregar al menos una actividad académica en cualquiera de las secciones disponibles")
    
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
            formulario = crud.create_formulario(form_data)
            
            # Log the submission (simplified - no audit for now)
            print(f"Formulario enviado por {nombre_completo} ({correo_institucional})")
            
            return formulario.id
            
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

def main():
    """Main application"""
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">📝 Formulario de Actividades Académicas</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <h3>🎯 Bienvenido al Sistema de Reportes Docentes</h3>
        <p>Complete este formulario para registrar sus actividades académicas del período actual. 
        Toda la información será revisada por el área administrativa correspondiente.</p>
        <p><strong>Instrucciones importantes:</strong></p>
        <ul>
            <li>Los campos marcados con (*) son obligatorios</li>
            <li><strong>Debe completar al menos UNA sección</strong> de actividades académicas</li>
            <li>No es necesario llenar todas las secciones - solo las que apliquen a su caso</li>
            <li>Algunos docentes pueden tener solo certificaciones, otros solo cursos, etc.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Personal Information
    nombre_completo, correo_institucional, año_academico, trimestre = show_personal_info()
    
    # Academic Activities Sections
    show_cursos_section()
    show_publicaciones_section()
    show_eventos_section()
    show_diseno_section()
    show_movilidad_section()
    show_reconocimientos_section()
    show_certificaciones_section()
    
    # Submit Section
    st.markdown('<div class="section-header">📤 Envío del Formulario</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("📤 Enviar Formulario", type="primary", use_container_width=True):
            # Validate form
            errors = validate_form(nombre_completo, correo_institucional, año_academico, trimestre)
            
            if errors:
                st.error("❌ Por favor corrija los siguientes errores:")
                for error in errors:
                    st.error(f"• {error}")
            else:
                # Submit form
                formulario_id = submit_form(nombre_completo, correo_institucional, año_academico, trimestre)
                
                if formulario_id:
                    st.markdown(f"""
                    <div class="success-box">
                        <h3>🎉 ¡Formulario Enviado Exitosamente!</h3>
                        <p><strong>ID de Seguimiento:</strong> {formulario_id}</p>
                        <p><strong>Estado:</strong> PENDIENTE (En revisión)</p>
                        <p><strong>Fecha de Envío:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                        <p>Su formulario ha sido recibido y será revisado por el área administrativa. 
                        Guarde su ID de seguimiento para futuras consultas.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Clear form after successful submission
                    if st.button("🆕 Enviar Otro Formulario"):
                        clear_form()
                        st.rerun()
        
        if st.button("🗑️ Limpiar Formulario", help="Eliminar todos los datos ingresados"):
            clear_form()
            st.success("✅ Formulario limpiado exitosamente")
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>Sistema de Reportes Docentes v1.0 | 
        Para soporte técnico contacte al área de sistemas</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()