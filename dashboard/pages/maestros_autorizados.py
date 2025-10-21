"""
Página de Gestión de Maestros Autorizados
Permite al administrador agregar, editar y eliminar maestros autorizados
"""

import streamlit as st
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.connection import SessionLocal
from app.database.crud import MaestroAutorizadoCRUD
from app.auth.streamlit_auth import auth

def show_maestros_autorizados_page():
    """Muestra la página de gestión de maestros autorizados"""
    
    # Require authentication
    if not auth.is_authenticated():
        auth.show_login_form()
        return

    st.title("👨‍🏫 Gestión de Maestros Autorizados")
    st.markdown("Administre la lista de maestros que pueden enviar formularios.")

    # Crear tabs para diferentes acciones
    tab1, tab2 = st.tabs(["📋 Lista de Maestros", "➕ Agregar Maestro"])

    db = SessionLocal()
    crud = MaestroAutorizadoCRUD(db)

    try:
        with tab1:
            show_maestros_list(crud)
        
        with tab2:
            show_add_maestro_form(crud)
            
    finally:
        db.close()

def show_maestros_list(crud: MaestroAutorizadoCRUD):
    """Muestra la lista de maestros autorizados"""
    
    st.subheader("📋 Lista de Maestros Autorizados")
    
    # Mostrar mensajes de éxito/error si existen
    if 'maestro_message' in st.session_state:
        message_type, message_text = st.session_state.maestro_message
        if message_type == "success":
            # Crear un placeholder para el mensaje que se desvanece
            message_placeholder = st.empty()
            message_placeholder.success(message_text)
            
            # JavaScript para hacer que el mensaje se desvanezca después de 3 segundos
            st.markdown("""
            <script>
            setTimeout(function() {
                var elements = document.querySelectorAll('[data-testid="stAlert"]');
                if (elements.length > 0) {
                    elements[elements.length - 1].style.transition = 'opacity 0.5s';
                    elements[elements.length - 1].style.opacity = '0';
                    setTimeout(function() {
                        elements[elements.length - 1].style.display = 'none';
                    }, 500);
                }
            }, 3000);
            </script>
            """, unsafe_allow_html=True)
        elif message_type == "error":
            st.error(message_text)
        elif message_type == "info":
            st.info(message_text)
        # Limpiar el mensaje después de mostrarlo
        del st.session_state.maestro_message
    
    # Obtener todos los maestros
    maestros = crud.get_all_maestros()
    
    if not maestros:
        st.info("📝 No hay maestros autorizados registrados.")
        st.markdown("""
        **Para comenzar:**
        1. Vaya a la pestaña "➕ Agregar Maestro"
        2. Ingrese el nombre completo y correo del maestro
        3. Haga clic en "Agregar Maestro"
        
        Los maestros autorizados podrán enviar formularios usando el sistema.
        """)
        return
    

    
    # Mostrar tabla de maestros
    for i, maestro in enumerate(maestros):
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 3, 2, 2])
            
            with col1:
                st.write(f"**{maestro.nombre_completo}**")
            
            with col2:
                st.write(f"📧 {maestro.correo_institucional}")
            
            with col3:
                st.write(f"📅 {maestro.fecha_creacion.strftime('%Y-%m-%d')}")
            
            with col4:
                col_edit, col_delete = st.columns(2)
                
                with col_edit:
                    if st.button("✏️", key=f"edit_{maestro.id}", help="Editar maestro"):
                        st.session_state[f"editing_{maestro.id}"] = True
                        st.rerun()
                
                with col_delete:
                    if st.button("🗑️", key=f"delete_{maestro.id}", help="Eliminar maestro"):
                        st.session_state[f"confirm_delete_{maestro.id}"] = True
                        st.rerun()
            
            # Confirmación de eliminación
            if st.session_state.get(f"confirm_delete_{maestro.id}", False):
                st.warning(f"⚠️ **¿Está seguro de eliminar a {maestro.nombre_completo}?**")
                st.write("Esta acción no se puede deshacer.")
                
                col_confirm, col_cancel = st.columns(2)
                
                with col_confirm:
                    if st.button("✅ Sí, eliminar", key=f"confirm_delete_yes_{maestro.id}", type="primary"):
                        if crud.delete_maestro(maestro.id):
                            st.session_state.maestro_message = ("success", f"✅ {maestro.nombre_completo} eliminado correctamente")
                            st.session_state[f"confirm_delete_{maestro.id}"] = False
                            st.rerun()
                        else:
                            st.session_state.maestro_message = ("error", "❌ Error al eliminar el maestro. Inténtelo nuevamente.")
                            st.session_state[f"confirm_delete_{maestro.id}"] = False
                            st.rerun()
                
                with col_cancel:
                    if st.button("❌ Cancelar", key=f"confirm_delete_no_{maestro.id}"):
                        st.session_state[f"confirm_delete_{maestro.id}"] = False
                        st.rerun()
            
            # Formulario de edición inline
            if st.session_state.get(f"editing_{maestro.id}", False):
                with st.form(f"edit_form_{maestro.id}"):
                    st.write("**Editar Maestro:**")
                    
                    col_name, col_email = st.columns(2)
                    
                    with col_name:
                        new_name = st.text_input(
                            "Nombre completo:",
                            value=maestro.nombre_completo,
                            key=f"edit_name_{maestro.id}"
                        )
                    
                    with col_email:
                        new_email = st.text_input(
                            "Correo institucional:",
                            value=maestro.correo_institucional,
                            key=f"edit_email_{maestro.id}"
                        )
                    
                    col_save, col_cancel = st.columns(2)
                    
                    with col_save:
                        if st.form_submit_button("💾 Guardar", type="primary"):
                            if new_name.strip() and new_email.strip():
                                if crud.update_maestro(maestro.id, new_name.strip(), new_email.strip()):
                                    st.session_state.maestro_message = ("success", f"✅ {new_name.strip()} actualizado correctamente")
                                    st.session_state[f"editing_{maestro.id}"] = False
                                    st.rerun()
                                else:
                                    st.session_state.maestro_message = ("error", "❌ Error al actualizar. Verifique que el email no esté duplicado.")
                                    st.rerun()
                            else:
                                st.session_state.maestro_message = ("error", "❌ Todos los campos son obligatorios.")
                                st.rerun()
                    
                    with col_cancel:
                        if st.form_submit_button("❌ Cancelar"):
                            st.session_state[f"editing_{maestro.id}"] = False
                            st.rerun()
            
            st.divider()

def show_add_maestro_form(crud: MaestroAutorizadoCRUD):
    """Muestra el formulario para agregar un nuevo maestro"""
    
    st.subheader("➕ Agregar Nuevo Maestro")
    
    # Mostrar mensajes de éxito/error si existen
    if 'maestro_add_message' in st.session_state:
        message_type, message_text = st.session_state.maestro_add_message
        if message_type == "success":
            # Crear un placeholder para el mensaje que se desvanece
            message_placeholder = st.empty()
            message_placeholder.success(message_text)
            
            # JavaScript para hacer que el mensaje se desvanezca después de 3 segundos
            st.markdown("""
            <script>
            setTimeout(function() {
                var elements = document.querySelectorAll('[data-testid="stAlert"]');
                if (elements.length > 0) {
                    elements[elements.length - 1].style.transition = 'opacity 0.5s';
                    elements[elements.length - 1].style.opacity = '0';
                    setTimeout(function() {
                        elements[elements.length - 1].style.display = 'none';
                    }, 500);
                }
            }, 3000);
            </script>
            """, unsafe_allow_html=True)
        elif message_type == "error":
            st.error(message_text)
        elif message_type == "info":
            st.info(message_text)
        # Limpiar el mensaje después de mostrarlo
        del st.session_state.maestro_add_message
    
    # Valores por defecto (vacíos si se acaba de agregar un maestro)
    default_nombre = "" if st.session_state.get('clear_form', False) else ""
    default_correo = "" if st.session_state.get('clear_form', False) else ""
    
    # Limpiar la bandera
    if st.session_state.get('clear_form', False):
        st.session_state.clear_form = False
    
    with st.form("add_maestro_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_completo = st.text_input(
                "Nombre completo del maestro:",
                value=default_nombre,
                placeholder="Ej: Dr. Juan Pérez García",
                help="Nombre completo como aparecerá en los formularios"
            )
        
        with col2:
            correo_institucional = st.text_input(
                "Correo institucional:",
                value=default_correo,
                placeholder="Ej: juan.perez@universidad.edu",
                help="Email institucional del maestro"
            )
        
        submitted = st.form_submit_button("➕ Agregar Maestro", type="primary")
        
        if submitted:
            if nombre_completo.strip() and correo_institucional.strip():
                # Validar formato de email básico
                if "@" not in correo_institucional or "." not in correo_institucional:
                    st.session_state.maestro_add_message = ("error", "❌ Por favor ingrese un email válido.")
                else:
                    maestro = crud.create_maestro(
                        nombre_completo.strip(),
                        correo_institucional.strip().lower()
                    )
                    
                    if maestro:
                        st.session_state.maestro_add_message = ("success", f"✅ {nombre_completo.strip()} agregado correctamente")
                        st.session_state.clear_form = True
                    else:
                        st.session_state.maestro_add_message = ("error", "❌ Error al agregar el maestro. Verifique que el email no esté duplicado.")
                
                st.rerun()
            else:
                st.session_state.maestro_add_message = ("error", "❌ Todos los campos son obligatorios.")
                st.rerun()

if __name__ == "__main__":
    show_maestros_autorizados_page()