"""
Página de Revisión de Formularios
Permite aprobar o rechazar formularios enviados por docentes
"""

from app.utils.correction_tokens import CorrectionTokenManager
from app.core.simple_audit import simple_audit
from app.auth.streamlit_auth import auth
from app.models.database import EstadoFormularioEnum
from app.database.crud import FormularioCRUD
from app.database.connection import SessionLocal
import streamlit as st
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))


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
        except:
            pass

        try:
            if form.publicaciones:
                form_data['publicaciones'] = [{
                    'autores': p.autores,
                    'titulo': p.titulo,
                    'evento_revista': p.evento_revista,
                    'estatus': p.estatus
                } for p in form.publicaciones]
        except:
            pass

        try:
            if form.eventos_academicos:
                form_data['eventos_academicos'] = [{
                    'nombre_evento': e.nombre_evento,
                    'fecha': e.fecha,
                    'tipo_participacion': e.tipo_participacion
                } for e in form.eventos_academicos]
        except:
            pass

        try:
            if form.diseno_curricular:
                form_data['diseno_curricular'] = [{
                    'nombre_curso': d.nombre_curso,
                    'descripcion': getattr(d, 'descripcion', '')
                } for d in form.diseno_curricular]
        except:
            pass

        try:
            if form.experiencias_movilidad:
                form_data['experiencias_movilidad'] = [{
                    'descripcion': m.descripcion,
                    'tipo': m.tipo,
                    'fecha': m.fecha
                } for m in form.experiencias_movilidad]
        except:
            pass

        try:
            if form.reconocimientos:
                form_data['reconocimientos'] = [{
                    'nombre': r.nombre,
                    'tipo': r.tipo,
                    'fecha': r.fecha
                } for r in form.reconocimientos]
        except:
            pass

        try:
            if form.certificaciones:
                form_data['certificaciones'] = [{
                    'nombre': c.nombre,
                    'fecha_obtencion': c.fecha_obtencion,
                    'fecha_vencimiento': getattr(c, 'fecha_vencimiento', None),
                    'vigente': getattr(c, 'vigente', True)
                } for c in form.certificaciones]
        except:
            pass

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

    # Filtro para tipo de formularios
    col1, col2 = st.columns([2, 1])

    with col1:
        filter_type = st.selectbox(
            "Mostrar formularios:",
            ["Solo Pendientes", "Todos los Formularios",
                "Solo Aprobados", "Solo Rechazados"],
            key="form_filter_type_main",
            help="Seleccione qué formularios desea revisar"
        )

    with col2:
        if st.button("🔄 Actualizar Lista"):
            st.rerun()

    # Get forms based on filter
    try:
        if filter_type == "Solo Pendientes":
            forms = get_pending_forms()
            status_msg = f"Hay {len(forms)} formularios pendientes de revisión."
        elif filter_type == "Todos los Formularios":
            forms = get_all_forms_for_review()
            status_msg = f"Mostrando {len(forms)} formularios en total."
        elif filter_type == "Solo Aprobados":
            forms = get_forms_by_status("APROBADO")
            status_msg = f"Hay {len(forms)} formularios aprobados."
        else:  # Solo Rechazados
            forms = get_forms_by_status("RECHAZADO")
            status_msg = f"Hay {len(forms)} formularios rechazados."

    except Exception as e:
        st.error(f"Error al cargar formularios: {e}")
        return

    if not forms:
        if filter_type == "Solo Pendientes":
            st.success("🎉 No hay formularios pendientes de revisión.")
        else:
            st.info(
                f"No hay formularios con el filtro seleccionado: {filter_type}")
        return

    # Mostrar información según el filtro
    if filter_type == "Solo Pendientes":
        st.info(status_msg)
    elif filter_type == "Solo Aprobados":
        st.success(
            status_msg + " Puede generar links de corrección si es necesario.")
    elif filter_type == "Solo Rechazados":
        st.warning(
            status_msg + " Puede generar links de corrección para que los docentes corrijan.")
    else:
        st.info(status_msg)

    # Form selection
    form_options = {
        f"ID {form['id']} - {form['nombre_completo']} ({form['estado'].value})": form for form in forms}
    selected_form_key = st.selectbox("Seleccionar formulario para revisar:", list(
        form_options.keys()), key="form_selection_main")

    if selected_form_key:
        selected_form_data = form_options[selected_form_key]

        # Get complete form data with relationships
        selected_form = get_complete_form_data(selected_form_data['id'])

        # Display form details
        st.subheader(
            f"📄 Detalles del Formulario ID: {selected_form_data['id']}")

        if not selected_form:
            st.error("No se pudo cargar el formulario seleccionado.")
            return

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Información Personal:**")
            st.write(f"- **Nombre:** {selected_form['nombre_completo']}")
            st.write(f"- **Email:** {selected_form['correo_institucional']}")
            if selected_form.get('año_academico'):
                st.write(
                    f"- **Período:** {selected_form['año_academico']} - {selected_form.get('trimestre', 'N/A')}")
            else:
                st.write("- **Período:** N/A")
            st.write(
                f"- **Fecha de envío:** {selected_form['fecha_envio'].strftime('%Y-%m-%d %H:%M')}")

        with col2:
            st.write("**Estado:**")
            st.write(f"- **Estado actual:** {selected_form['estado'].value}")
            if selected_form.get('fecha_revision'):
                st.write(
                    f"- **Fecha revisión:** {selected_form['fecha_revision'].strftime('%Y-%m-%d %H:%M')}")
            if selected_form.get('revisado_por'):
                st.write(
                    f"- **Revisado por:** {selected_form['revisado_por']}")

        # Show related data
        st.subheader("📚 Contenido del Formulario")

        # Create tabs for different sections
        tabs = st.tabs(["Cursos", "Publicaciones", "Eventos", "Diseño Curricular",
                       "Movilidad", "Reconocimientos", "Certificaciones"])

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
                    st.write(
                        f"- Tipo de participación: {evento['tipo_participacion']}")
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
                        st.write(
                            f"- Fecha vencimiento: {cert['fecha_vencimiento']}")
                    st.write(
                        f"- Vigente: {'Sí' if cert.get('vigente', True) else 'No'}")
                    st.write("---")
            else:
                st.info("No hay certificaciones registradas.")

        # Mostrar si el formulario ha sido corregido
        if selected_form.get('token_correccion'):
            st.info("🔄 **Este formulario tiene un link de corrección activo**")

        # Mostrar historial de cambios si existe
        db = SessionLocal()
        try:
            # Verificar si hay logs de actualización para este formulario
            from sqlalchemy import text
            result = db.execute(text("""
                SELECT COUNT(*) FROM audit_logs 
                WHERE resource_id = :form_id AND action LIKE '%ACTUALIZADO%'
            """), {"form_id": selected_form['id']})

            update_count = result.fetchone()[0] if result.fetchone() else 0

            if update_count > 0:
                st.info(
                    f"📝 **Este formulario ha sido actualizado {update_count} vez(es)**")
        except:
            pass
        finally:
            db.close()

        # Action buttons
        st.subheader("⚡ Acciones")

        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

        with col1:
            estado_actual = selected_form['estado'].value

            if estado_actual == "PENDIENTE":
                if st.button("✅ Aprobar", type="primary", key=f"approve_{selected_form['id']}"):
                    if approve_form(selected_form['id']):
                        st.success("Formulario aprobado exitosamente!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Error al aprobar el formulario.")
            elif estado_actual == "APROBADO":
                st.success("✅ **Ya Aprobado**")
                if st.button("🔄 Revertir a Pendiente", key=f"revert_{selected_form['id']}"):
                    if revert_to_pending(selected_form['id']):
                        st.success("Formulario revertido a pendiente!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Error al revertir el formulario.")
            else:  # RECHAZADO
                st.error("❌ **Rechazado**")
                if st.button("🔄 Revertir a Pendiente", key=f"revert_rejected_{selected_form['id']}"):
                    if revert_to_pending(selected_form['id']):
                        st.success("Formulario revertido a pendiente!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Error al revertir el formulario.")

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
                comment = st.text_area(
                    "Comentario:", key=f"comment_{selected_form['id']}", placeholder="Escriba el motivo del rechazo...")

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

        with col3:
            # Mostrar información del estado antes del botón
            estado_actual = selected_form['estado'].value

            if estado_actual == "APROBADO":
                st.warning("⚠️ **Formulario ya aprobado**")
                st.write(
                    "Generar corrección creará una nueva versión en estado PENDIENTE.")
            elif estado_actual == "RECHAZADO":
                st.info("ℹ️ **Formulario rechazado**")
                st.write("La corrección permitirá al docente reenviar.")

            if st.button("🔗 Generar Link de Corrección", key=f"correction_{selected_form['id']}"):
                token_manager = CorrectionTokenManager()
                # Generar token y crear URL manualmente
                token = token_manager.create_correction_token(
                    selected_form['id'])

                if token:
                    # URL del formulario público en el mismo sistema
                    correction_url = f"http://192.168.1.15:8502/formulario?token={token}&mode=correction"
                else:
                    correction_url = None

                if correction_url:
                    st.success("✅ Link de corrección generado!")
                    st.code(correction_url, language=None)

                    # Mensaje específico según el estado
                    if estado_actual == "APROBADO":
                        st.info(
                            "📧 **Importante:** La nueva versión requerirá aprobación nuevamente.")
                    elif estado_actual == "RECHAZADO":
                        st.info(
                            "📧 **Nota:** El docente podrá corregir los problemas identificados.")
                    else:
                        st.info(
                            "📧 Envía este link al docente para que pueda corregir su formulario.")

                    # Botón para copiar al portapapeles (usando JavaScript)
                    st.markdown(f"""
                    <button onclick="navigator.clipboard.writeText('{correction_url}')">
                        📋 Copiar Link
                    </button>
                    """, unsafe_allow_html=True)
                else:
                    st.error("❌ Error al generar el link de corrección.")

        with col4:
            st.write("**Información:**")
            st.write(
                f"📅 Enviado: {selected_form['fecha_envio'].strftime('%Y-%m-%d')}")

            # Mostrar si tiene token de corrección activo
            if selected_form.get('token_correccion'):
                st.write("🔗 **Link activo:** Corrección disponible")

            # Mostrar última actualización si existe
            if selected_form.get('fecha_revision'):
                st.write(
                    f"📝 Revisado: {selected_form['fecha_revision'].strftime('%Y-%m-%d')}")

            if selected_form.get('revisado_por'):
                st.write(f"👤 Por: {selected_form['revisado_por']}")


def get_pending_forms():
    """Get pending forms for review - only active versions"""
    return get_forms_by_status("PENDIENTE")


def get_all_forms_for_review():
    """Get all forms for review - only active versions"""
    db = SessionLocal()
    try:
        from sqlalchemy import text

        # Obtener solo las versiones activas de todos los formularios
        result = db.execute(text("""
            SELECT id, nombre_completo, correo_institucional, fecha_envio, estado
            FROM formularios_envio 
            WHERE es_version_activa = 1
            ORDER BY fecha_envio DESC
            LIMIT 50
        """))

        forms = result.fetchall()

        # Convert to simple dict to avoid session issues
        simple_forms = []
        for form in forms:
            # Determinar el enum correcto según el estado
            if form.estado == 'PENDIENTE':
                estado_enum = EstadoFormularioEnum.PENDIENTE
            elif form.estado == 'APROBADO':
                estado_enum = EstadoFormularioEnum.APROBADO
            else:
                estado_enum = EstadoFormularioEnum.RECHAZADO

            simple_forms.append({
                'id': form.id,
                'nombre_completo': form.nombre_completo,
                'correo_institucional': form.correo_institucional,
                'fecha_envio': form.fecha_envio,
                'estado': estado_enum
            })
        return simple_forms
    finally:
        db.close()


def get_forms_by_status(status: str):
    """Get forms by specific status - only active versions"""
    db = SessionLocal()
    try:
        from sqlalchemy import text

        # Obtener solo las versiones activas del estado especificado
        result = db.execute(text("""
            SELECT id, nombre_completo, correo_institucional, fecha_envio, estado
            FROM formularios_envio 
            WHERE estado = :status 
            AND es_version_activa = 1
            ORDER BY fecha_envio DESC
            LIMIT 30
        """), {"status": status})

        forms = result.fetchall()

        # Convert to simple dict to avoid session issues
        simple_forms = []
        for form in forms:
            # Determinar el enum correcto según el estado
            if form.estado == 'PENDIENTE':
                estado_enum = EstadoFormularioEnum.PENDIENTE
            elif form.estado == 'APROBADO':
                estado_enum = EstadoFormularioEnum.APROBADO
            else:
                estado_enum = EstadoFormularioEnum.RECHAZADO

            simple_forms.append({
                'id': form.id,
                'nombre_completo': form.nombre_completo,
                'correo_institucional': form.correo_institucional,
                'fecha_envio': form.fecha_envio,
                'estado': estado_enum
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


def revert_to_pending(form_id: int):
    """Revierte un formulario aprobado o rechazado a estado pendiente"""
    db = SessionLocal()
    try:
        from sqlalchemy import text

        # Actualizar el estado a PENDIENTE
        result = db.execute(text("""
            UPDATE formularios_envio 
            SET estado = 'PENDIENTE',
                fecha_revision = NULL,
                revisado_por = NULL
            WHERE id = :form_id
        """), {"form_id": form_id})

        db.commit()

        # Log the action
        try:
            user_info = auth.get_current_user()
            if user_info:
                simple_audit.log_form_approval(
                    form_id=form_id,
                    form_owner="Sistema",
                    approved_by=f"{user_info['name']} (Revertido a Pendiente)"
                )
        except Exception as e:
            print(f"Audit logging failed: {e}")

        return result.rowcount > 0

    except Exception as e:
        print(f"Error revirtiendo formulario: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    show_form_review_page()
