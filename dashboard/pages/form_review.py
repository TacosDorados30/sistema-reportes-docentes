"""
Página de Revisión de Formularios
Permite aprobar o rechazar formularios enviados por docentes
"""

import streamlit as st
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.connection import SessionLocal
from app.database.crud import FormularioCRUD
from app.models.database import EstadoFormularioEnum
from app.auth.streamlit_auth import auth
from app.core.simple_audit import simple_audit

def get_complete_form_data(form_id: int):
    """Get complete form data with all relationships"""
    db = SessionLocal()
    try:
        crud = FormularioCRUD(db)
        form = crud.get_formulario(form_id)
        if not form:
            return None
            
        # Convert to dict with all data to avoid session issues
        form_data = {
            'id': form.id,
            'nombre_completo': form.nombre_completo,
            'correo_institucional': form.correo_institucional,
            'fecha_envio': form.fecha_envio,
            'estado': form.estado,
            'fecha_revision': form.fecha_revision,
            'revisado_por': form.revisado_por,
            'año_academico': getattr(form, 'año_academico', None),
            'trimestre': getattr(form, 'trimestre', None),
            'cursos_capacitacion': [],
            'publicaciones': [],
            'eventos_academicos': [],
            'diseno_curricular': [],
            'experiencias_movilidad': [],
            'reconocimientos': [],
            'certificaciones': []
        }
        
        # Load relationships safely
        try:
            if form.cursos_capacitacion:
                form_data['cursos_capacitacion'] = [{
                    'nombre_curso': c.nombre_curso,
                    'fecha': c.fecha,
                    'horas': c.horas
                } for c in form.cursos_capacitacion]
        except: pass
        
        try:
            if form.publicaciones:
                form_data['publicaciones'] = [{
                    'autores': p.autores,
                    'titulo': p.titulo,
                    'evento_revista': p.evento_revista,
                    'estatus': p.estatus
                } for p in form.publicaciones]
        except: pass
        
        try:
            if form.eventos_academicos:
                form_data['eventos_academicos'] = [{
                    'nombre_evento': e.nombre_evento,
                    'fecha': e.fecha,
                    'tipo_participacion': e.tipo_participacion
                } for e in form.eventos_academicos]
        except: pass
        
        try:
            if form.diseno_curricular:
                form_data['diseno_curricular'] = [{
                    'nombre_curso': d.nombre_curso,
                    'descripcion': getattr(d, 'descripcion', '')
                } for d in form.diseno_curricular]
        except: pass
        
        try:
            if form.experiencias_movilidad:
                form_data['experiencias_movilidad'] = [{
                    'descripcion': m.descripcion,
                    'tipo': m.tipo,
                    'fecha': m.fecha
                } for m in form.experiencias_movilidad]
        except: pass
        
        try:
            if form.reconocimientos:
                form_data['reconocimientos'] = [{
                    'nombre': r.nombre,
                    'tipo': r.tipo,
                    'fecha': r.fecha
                } for r in form.reconocimientos]
        except: pass
        
        try:
            if form.certificaciones:
                form_data['certificaciones'] = [{
                    'nombre': c.nombre,
                    'fecha_obtencion': c.fecha_obtencion,
                    'fecha_vencimiento': getattr(c, 'fecha_vencimiento', None),
                    'vigente': getattr(c, 'vigente', True)
                } for c in form.certificaciones]
        except: pass
        
        return form_data
        
    except Exception as e:
        print(f"Error getting form data: {e}")
        return None
    finally:
        db.close()

def show_form_review_page():
    """Show form review interface as a separate page"""
    
    # Require authentication
    if not auth.is_authenticated():
        auth.show_login_form()
        return

    st.title("📋 Revisión de Formularios")
    st.markdown("Revise y apruebe o rechace formularios enviados por docentes.")

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
    form_options = {f"ID {form['id']} - {form['nombre_completo']}": form for form in pending_forms}
    selected_form_key = st.selectbox("Seleccionar formulario para revisar:", list(form_options.keys()))

    if selected_form_key:
        selected_form_data = form_options[selected_form_key]
        
        # Get complete form data with relationships
        selected_form = get_complete_form_data(selected_form_data['id'])

        # Display form details
        st.subheader(f"📄 Detalles del Formulario ID: {selected_form_data['id']}")

        if not selected_form:
            st.error("No se pudo cargar el formulario seleccionado.")
            return
            
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Información Personal:**")
            st.write(f"- **Nombre:** {selected_form['nombre_completo']}")
            st.write(f"- **Email:** {selected_form['correo_institucional']}")
            if selected_form.get('año_academico'):
                st.write(f"- **Período:** {selected_form['año_academico']} - {selected_form.get('trimestre', 'N/A')}")
            else:
                st.write("- **Período:** N/A")
            st.write(f"- **Fecha de envío:** {selected_form['fecha_envio'].strftime('%Y-%m-%d %H:%M')}")

        with col2:
            st.write("**Estado:**")
            st.write(f"- **Estado actual:** {selected_form['estado'].value}")
            if selected_form.get('fecha_revision'):
                st.write(f"- **Fecha revisión:** {selected_form['fecha_revision'].strftime('%Y-%m-%d %H:%M')}")
            if selected_form.get('revisado_por'):
                st.write(f"- **Revisado por:** {selected_form['revisado_por']}")

        # Show related data
        st.subheader("📚 Contenido del Formulario")

        # Create tabs for different sections
        tabs = st.tabs(["Cursos", "Publicaciones", "Eventos", "Diseño Curricular", "Movilidad", "Reconocimientos", "Certificaciones"])

        with tabs[0]:  # Cursos
            if selected_form['cursos_capacitacion']:
                for i, curso in enumerate(selected_form['cursos_capacitacion'], 1):
                    st.write(f"**Curso {i}:**")
                    st.write(f"- Nombre: {curso['nombre_curso']}")
                    st.write(f"- Fecha: {curso['fecha']}")
                    st.write(f"- Horas: {curso['horas']}")
                    st.write("---")
            else:
                st.info("No hay cursos registrados.")

        with tabs[1]:  # Publicaciones
            if selected_form['publicaciones']:
                for i, pub in enumerate(selected_form['publicaciones'], 1):
                    st.write(f"**Publicación {i}:**")
                    st.write(f"- Autores: {pub['autores']}")
                    st.write(f"- Título: {pub['titulo']}")
                    st.write(f"- Evento/Revista: {pub['evento_revista']}")
                    st.write(f"- Estatus: {pub['estatus'].value}")
                    st.write("---")
            else:
                st.info("No hay publicaciones registradas.")

        with tabs[2]:  # Eventos
            if selected_form['eventos_academicos']:
                for i, evento in enumerate(selected_form['eventos_academicos'], 1):
                    st.write(f"**Evento {i}:**")
                    st.write(f"- Nombre: {evento['nombre_evento']}")
                    st.write(f"- Fecha: {evento['fecha']}")
                    st.write(f"- Tipo de participación: {evento['tipo_participacion']}")
                    st.write("---")
            else:
                st.info("No hay eventos registrados.")

        with tabs[3]:  # Diseño Curricular
            if selected_form['diseno_curricular']:
                for i, diseno in enumerate(selected_form['diseno_curricular'], 1):
                    st.write(f"**Diseño {i}:**")
                    st.write(f"- Curso: {diseno['nombre_curso']}")
                    if diseno.get('descripcion'):
                        st.write(f"- Descripción: {diseno['descripcion']}")
                    st.write("---")
            else:
                st.info("No hay diseños curriculares registrados.")

        with tabs[4]:  # Movilidad
            if selected_form['experiencias_movilidad']:
                for i, mov in enumerate(selected_form['experiencias_movilidad'], 1):
                    st.write(f"**Movilidad {i}:**")
                    st.write(f"- Descripción: {mov['descripcion']}")
                    st.write(f"- Tipo: {mov['tipo']}")
                    st.write(f"- Fecha: {mov['fecha']}")
                    st.write("---")
            else:
                st.info("No hay experiencias de movilidad registradas.")

        with tabs[5]:  # Reconocimientos
            if selected_form['reconocimientos']:
                for i, rec in enumerate(selected_form['reconocimientos'], 1):
                    st.write(f"**Reconocimiento {i}:**")
                    st.write(f"- Nombre: {rec['nombre']}")
                    st.write(f"- Tipo: {rec['tipo']}")
                    st.write(f"- Fecha: {rec['fecha']}")
                    st.write("---")
            else:
                st.info("No hay reconocimientos registrados.")

        with tabs[6]:  # Certificaciones
            if selected_form['certificaciones']:
                for i, cert in enumerate(selected_form['certificaciones'], 1):
                    st.write(f"**Certificación {i}:**")
                    st.write(f"- Nombre: {cert['nombre']}")
                    st.write(f"- Fecha obtención: {cert['fecha_obtencion']}")
                    if cert.get('fecha_vencimiento'):
                        st.write(f"- Fecha vencimiento: {cert['fecha_vencimiento']}")
                    st.write(f"- Vigente: {'Sí' if cert.get('vigente', True) else 'No'}")
                    st.write("---")
            else:
                st.info("No hay certificaciones registradas.")

        # Action buttons
        st.subheader("⚡ Acciones")

        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            if st.button("✅ Aprobar", type="primary", key=f"approve_{selected_form['id']}"):
                if approve_form(selected_form['id']):
                    st.success("Formulario aprobado exitosamente!")
                    st.cache_data.clear()  # Clear cache to refresh data
                    st.rerun()
                else:
                    st.error("Error al aprobar el formulario.")

        with col2:
            # Initialize session state for rejection
            if f"rejecting_{selected_form['id']}" not in st.session_state:
                st.session_state[f"rejecting_{selected_form['id']}"] = False
            
            if not st.session_state[f"rejecting_{selected_form['id']}"]:
                if st.button("❌ Rechazar", key=f"reject_{selected_form['id']}"):
                    st.session_state[f"rejecting_{selected_form['id']}"] = True
                    st.rerun()
            else:
                st.write("**Rechazar formulario:**")
                comment = st.text_area("Comentario:", key=f"comment_{selected_form['id']}", placeholder="Escriba el motivo del rechazo...")
                
                col_confirm, col_cancel = st.columns(2)
                with col_confirm:
                    if st.button("✅ Confirmar", key=f"confirm_reject_{selected_form['id']}", type="primary"):
                        if reject_form(selected_form['id'], comment):
                            st.success("Formulario rechazado.")
                            st.session_state[f"rejecting_{selected_form['id']}"] = False
                            st.rerun()
                        else:
                            st.error("Error al rechazar el formulario.")
                
                with col_cancel:
                    if st.button("❌ Cancelar", key=f"cancel_reject_{selected_form['id']}"):
                        st.session_state[f"rejecting_{selected_form['id']}"] = False
                        st.rerun()


def get_pending_forms():
    """Get pending forms for review"""
    db = SessionLocal()
    try:
        crud = FormularioCRUD(db)
        forms = crud.get_formularios_by_estado(EstadoFormularioEnum.PENDIENTE, limit=20)
        # Convert to simple dict to avoid session issues
        simple_forms = []
        for form in forms:
            simple_forms.append({
                'id': form.id,
                'nombre_completo': form.nombre_completo,
                'correo_institucional': form.correo_institucional,
                'fecha_envio': form.fecha_envio,
                'estado': form.estado
            })
        return simple_forms
    finally:
        db.close()


def approve_form(form_id: int):
    """Approve a form"""
    db = SessionLocal()
    try:
        crud = FormularioCRUD(db)
        user_info = auth.get_current_user()
        user_id = user_info.get("username") if user_info else "unknown"
        
        # Get form details for logging
        form = crud.get_formulario(form_id)
        if not form:
            return False
        
        # Check if form is in valid state for approval
        if form.estado.value != "PENDIENTE":
            return False
        
        success = crud.aprobar_formulario(form_id, "streamlit_admin")
        
        if success:
            # Log the approval action
            try:
                if user_info:
                    simple_audit.log_form_approval(
                        form_id=form_id,
                        form_owner=form.nombre_completo,
                        approved_by=user_info["name"]
                    )
            except Exception as e:
                print(f"Audit logging failed: {e}")
        
        return success
        
    except Exception as e:
        print(f"Error approving form: {e}")
        return False
    finally:
        db.close()


def reject_form(form_id: int, comment: str = ""):
    """Reject a form"""
    db = SessionLocal()
    try:
        crud = FormularioCRUD(db)
        user_info = auth.get_current_user()
        user_id = user_info.get("username") if user_info else "unknown"
        
        # Get form details for logging
        form = crud.get_formulario(form_id)
        if not form:
            return False
        
        # Check if form is in valid state for rejection
        if form.estado.value != "PENDIENTE":
            return False
        
        success = crud.rechazar_formulario(form_id, "streamlit_admin", comment)
        
        if success:
            # Log the rejection action
            try:
                if user_info:
                    simple_audit.log_form_rejection(
                        form_id=form_id,
                        form_owner=form.nombre_completo,
                        rejected_by=user_info["name"],
                        reason=comment
                    )
            except Exception as e:
                print(f"Audit logging failed: {e}")
        
        return success
        
    except Exception as e:
        print(f"Error rejecting form: {e}")
        return False
    finally:
        db.close()


# Execute the page
if __name__ == "__main__":
    show_form_review_page()
else:
    show_form_review_page()