import streamlit as st
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.connection import SessionLocal
from app.database.crud import FormularioCRUD
from app.models.database import EstadoFormularioEnum

def show_form_review_page():
    """Dedicated page for form review with enhanced functionality"""
    
    # Require authentication
    from app.auth.streamlit_auth import auth
    if not auth.require_authentication():
        return
    
    st.title("📋 Revisión Detallada de Formularios")
    
    # Get pending forms
    db = SessionLocal()
    try:
        crud = FormularioCRUD(db)
        pending_forms = crud.get_formularios_by_estado(EstadoFormularioEnum.PENDIENTE, limit=100)
        
        if not pending_forms:
            st.success("🎉 No hay formularios pendientes de revisión.")
            
            # Show recently reviewed forms
            st.subheader("📚 Formularios Revisados Recientemente")
            recent_approved = crud.get_formularios_by_estado(EstadoFormularioEnum.APROBADO, limit=10)
            recent_rejected = crud.get_formularios_by_estado(EstadoFormularioEnum.RECHAZADO, limit=10)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Recientemente Aprobados:**")
                for form in recent_approved:
                    st.write(f"- {form.nombre_completo} (ID: {form.id})")
            
            with col2:
                st.write("**Recientemente Rechazados:**")
                for form in recent_rejected:
                    st.write(f"- {form.nombre_completo} (ID: {form.id})")
            
            return
        
        st.info(f"📊 Hay {len(pending_forms)} formularios pendientes de revisión.")
        
        # Bulk actions
        st.subheader("⚡ Acciones en Lote")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ Aprobar Todos", help="Aprobar todos los formularios pendientes"):
                if st.checkbox("Confirmar aprobación en lote"):
                    approved_count = 0
                    for form in pending_forms:
                        if crud.aprobar_formulario(form.id, "streamlit_admin_bulk"):
                            approved_count += 1
                    st.success(f"Se aprobaron {approved_count} formularios.")
                    st.rerun()
        
        with col2:
            st.write("") # Spacer
        
        with col3:
            selected_forms = st.multiselect(
                "Seleccionar formularios:",
                options=[f"ID {form.id} - {form.nombre_completo}" for form in pending_forms],
                help="Seleccionar múltiples formularios para acciones en lote"
            )
        
        # Individual form review
        st.subheader("🔍 Revisión Individual")
        
        # Create tabs for each pending form
        if len(pending_forms) <= 5:
            # If few forms, show as tabs
            tab_names = [f"ID {form.id}" for form in pending_forms]
            tabs = st.tabs(tab_names)
            
            for i, (tab, form) in enumerate(zip(tabs, pending_forms)):
                with tab:
                    show_form_details(form, crud, f"tab_{i}")
        else:
            # If many forms, use selectbox
            form_options = {f"ID {form.id} - {form.nombre_completo}": form for form in pending_forms}
            selected_form_key = st.selectbox("Seleccionar formulario:", list(form_options.keys()))
            
            if selected_form_key:
                selected_form = form_options[selected_form_key]
                show_form_details(selected_form, crud, "selectbox")
    
    finally:
        db.close()

def show_form_details(form, crud, key_suffix):
    """Show detailed form information with action buttons"""
    
    # Form header
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write(f"**👤 {form.nombre_completo}**")
        st.write(f"📧 {form.correo_institucional}")
        st.write(f"📅 Enviado: {form.fecha_envio.strftime('%Y-%m-%d %H:%M')}")
    
    with col2:
        # Quick stats
        total_items = (
            len(form.cursos_capacitacion) +
            len(form.publicaciones) +
            len(form.eventos_academicos) +
            len(form.diseno_curricular) +
            len(form.movilidad) +
            len(form.reconocimientos) +
            len(form.certificaciones)
        )
        st.metric("Total Items", total_items)
    
    # Detailed content in expandable sections
    with st.expander("📚 Cursos de Capacitación", expanded=len(form.cursos_capacitacion) > 0):
        if form.cursos_capacitacion:
            for i, curso in enumerate(form.cursos_capacitacion, 1):
                st.write(f"**{i}.** {curso.nombre_curso}")
                st.write(f"   📅 {curso.fecha} | ⏱️ {curso.horas} horas")
        else:
            st.info("No hay cursos registrados.")
    
    with st.expander("📄 Publicaciones", expanded=len(form.publicaciones) > 0):
        if form.publicaciones:
            for i, pub in enumerate(form.publicaciones, 1):
                st.write(f"**{i}.** {pub.titulo}")
                st.write(f"   👥 {pub.autores}")
                st.write(f"   📖 {pub.evento_revista}")
                
                # Status badge
                status_color = {
                    'ACEPTADO': '🟢',
                    'PUBLICADO': '🔵',
                    'EN_REVISION': '🟡',
                    'RECHAZADO': '🔴'
                }
                st.write(f"   {status_color.get(pub.estatus.value, '⚪')} {pub.estatus.value}")
        else:
            st.info("No hay publicaciones registradas.")
    
    with st.expander("🎯 Eventos Académicos", expanded=len(form.eventos_academicos) > 0):
        if form.eventos_academicos:
            for i, evento in enumerate(form.eventos_academicos, 1):
                st.write(f"**{i}.** {evento.nombre_evento}")
                st.write(f"   📅 {evento.fecha}")
                
                # Participation type badge
                tipo_icon = {
                    'ORGANIZADOR': '👑',
                    'PARTICIPANTE': '👤',
                    'PONENTE': '🎤'
                }
                st.write(f"   {tipo_icon.get(evento.tipo_participacion.value, '👤')} {evento.tipo_participacion.value}")
        else:
            st.info("No hay eventos registrados.")
    
    with st.expander("🎓 Diseño Curricular", expanded=len(form.diseno_curricular) > 0):
        if form.diseno_curricular:
            for i, diseno in enumerate(form.diseno_curricular, 1):
                st.write(f"**{i}.** {diseno.nombre_curso}")
                if diseno.descripcion:
                    st.write(f"   📝 {diseno.descripcion}")
        else:
            st.info("No hay diseños curriculares registrados.")
    
    with st.expander("✈️ Experiencias de Movilidad", expanded=len(form.movilidad) > 0):
        if form.movilidad:
            for i, mov in enumerate(form.movilidad, 1):
                tipo_icon = '🌍' if mov.tipo.value == 'INTERNACIONAL' else '🏠'
                st.write(f"**{i}.** {tipo_icon} {mov.tipo.value}")
                st.write(f"   📝 {mov.descripcion}")
                st.write(f"   📅 {mov.fecha}")
        else:
            st.info("No hay experiencias de movilidad registradas.")
    
    with st.expander("🏆 Reconocimientos", expanded=len(form.reconocimientos) > 0):
        if form.reconocimientos:
            for i, rec in enumerate(form.reconocimientos, 1):
                tipo_icon = {
                    'GRADO': '🎓',
                    'PREMIO': '🏆',
                    'DISTINCION': '🌟'
                }
                st.write(f"**{i}.** {tipo_icon.get(rec.tipo.value, '🏆')} {rec.nombre}")
                st.write(f"   📅 {rec.fecha} | 📋 {rec.tipo.value}")
        else:
            st.info("No hay reconocimientos registrados.")
    
    with st.expander("📜 Certificaciones", expanded=len(form.certificaciones) > 0):
        if form.certificaciones:
            for i, cert in enumerate(form.certificaciones, 1):
                vigente_icon = '✅' if cert.vigente else '❌'
                st.write(f"**{i}.** {vigente_icon} {cert.nombre}")
                st.write(f"   📅 Obtenida: {cert.fecha_obtencion}")
                if cert.fecha_vencimiento:
                    st.write(f"   ⏰ Vence: {cert.fecha_vencimiento}")
                st.write(f"   📊 Estado: {'Vigente' if cert.vigente else 'Vencida'}")
        else:
            st.info("No hay certificaciones registradas.")
    
    # Action buttons
    st.write("---")
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("✅ Aprobar", type="primary", key=f"approve_{form.id}_{key_suffix}"):
            if crud.aprobar_formulario(form.id, "streamlit_admin"):
                st.success("✅ Formulario aprobado exitosamente!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("❌ Error al aprobar el formulario.")
    
    with col2:
        if st.button("❌ Rechazar", key=f"reject_{form.id}_{key_suffix}"):
            st.session_state[f"show_reject_{form.id}_{key_suffix}"] = True
    
    # Rejection form
    if st.session_state.get(f"show_reject_{form.id}_{key_suffix}", False):
        with col3:
            comment = st.text_area(
                "Motivo del rechazo:",
                key=f"comment_{form.id}_{key_suffix}",
                placeholder="Especifique el motivo del rechazo..."
            )
            
            col_confirm, col_cancel = st.columns(2)
            
            with col_confirm:
                if st.button("Confirmar Rechazo", key=f"confirm_reject_{form.id}_{key_suffix}"):
                    if crud.rechazar_formulario(form.id, "streamlit_admin", comment):
                        st.success("❌ Formulario rechazado.")
                        st.session_state[f"show_reject_{form.id}_{key_suffix}"] = False
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Error al rechazar el formulario.")
            
            with col_cancel:
                if st.button("Cancelar", key=f"cancel_reject_{form.id}_{key_suffix}"):
                    st.session_state[f"show_reject_{form.id}_{key_suffix}"] = False
                    st.rerun()

if __name__ == "__main__":
    show_form_review_page()