"""
Streamlit authentication middleware
"""

import streamlit as st
from typing import Optional, Dict, Any
from .auth_manager import AuthManager
from app.core.simple_audit import simple_audit


class StreamlitAuth:
    """Streamlit authentication wrapper"""

    def __init__(self):
        """Initialize Streamlit authentication"""

        self.auth_manager = AuthManager()

        # Initialize session state
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'session_id' not in st.session_state:
            st.session_state.session_id = None
        if 'user_info' not in st.session_state:
            st.session_state.user_info = None

    def require_authentication(self) -> bool:
        """Require authentication for current page"""

        # Check if already authenticated
        if st.session_state.authenticated and st.session_state.session_id:
            # Validate session
            session_data = self.auth_manager.validate_session(
                st.session_state.session_id)
            if session_data:
                st.session_state.user_info = session_data
                return True
            else:
                # Session expired
                self._clear_session()
                return False

        return False

    def show_login_form(self):
        """Display login form"""

        # Add minimal CSS for login page
        st.markdown("""
        <style>
            .login-header {
                text-align: center;
                color: #1f77b4;
                margin-bottom: 2rem;
            }
            .login-subtitle {
                text-align: center;
                color: #666;
                margin-bottom: 1rem;
            }
        </style>
        """, unsafe_allow_html=True)

        # Center the login form
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown(
                '<h1 class="login-header">🔐 Sistema de Reportes Docentes</h1>', unsafe_allow_html=True)
            st.markdown(
                '<h3 class="login-subtitle">Acceso Administrativo</h3>', unsafe_allow_html=True)
            st.markdown(
                '<p class="login-subtitle">Ingrese sus credenciales para acceder al sistema.</p>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            # Create login form
            with st.form("login_form"):
                username = st.text_input(
                    "Email", placeholder="Ingrese su correo electrónico")
                password = st.text_input(
                    "Contraseña", type="password", placeholder="Ingrese su contraseña")

                st.markdown("<br>", unsafe_allow_html=True)

                col_btn1, col_btn2 = st.columns([1, 1])

                with col_btn1:
                    login_button = st.form_submit_button(
                        "🚀 Iniciar Sesión", type="primary", use_container_width=True)

                with col_btn2:
                    forgot_button = st.form_submit_button(
                        "❓ ¿Olvidó su contraseña?", use_container_width=True)

            # Handle login
            if login_button:
                if username and password:
                    session_data = self.auth_manager.authenticate(
                        username, password)

                    if session_data:
                        # Successful login
                        st.session_state.authenticated = True
                        st.session_state.session_id = session_data["session_id"]
                        st.session_state.user_info = session_data

                        # Log successful login
                        try:
                            simple_audit.log_login(
                                user_id=session_data["username"],
                                user_name=session_data["name"],
                                success=True
                            )
                        except Exception as e:
                            print(f"Audit logging failed: {e}")

                        st.success(f"¡Bienvenido, {session_data['name']}!")
                        st.rerun()
                    else:
                        # Log failed login attempt
                        try:
                            simple_audit.log_login(
                                user_id=username,
                                user_name=username,
                                success=False
                            )
                        except Exception as e:
                            print(f"Audit logging failed: {e}")
                        st.error("❌ Email o contraseña incorrectos")
                else:
                    st.error("⚠️ Por favor, ingrese email y contraseña")

            if forgot_button:
                self._show_password_reset_info()

    def _show_password_reset_info(self):
        """Show password reset information"""

        st.info("""
        **Recuperación de Contraseña**
        
        Para recuperar su contraseña, contacte al administrador del sistema:
        - Email: admin@universidad.edu.mx
        - Teléfono: (555) 123-4567
        
        Por seguridad, las contraseñas no pueden ser recuperadas automáticamente.
        """)

    def logout(self):
        """Logout current user"""

        user_info = self.get_current_user()

        if st.session_state.session_id:
            self.auth_manager.logout(st.session_state.session_id)

        # Log logout
        if user_info:
            try:
                simple_audit.log_logout(
                    user_id=user_info["username"],
                    user_name=user_info["name"]
                )
            except Exception as e:
                print(f"Audit logging failed: {e}")

        self._clear_session()
        st.success("Sesión cerrada exitosamente")
        st.rerun()

    def _clear_session(self):
        """Clear session state"""

        st.session_state.authenticated = False
        st.session_state.session_id = None
        st.session_state.user_info = None

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user"""

        return st.session_state.user_info

    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False)

    def show_user_menu(self):
        """Show user menu in sidebar"""

        if not self.is_authenticated():
            return

        user_info = self.get_current_user()
        if not user_info:
            return

        st.sidebar.markdown("---")
        st.sidebar.subheader("👤 Usuario")
        st.sidebar.write(f"**{user_info['name']}**")
        st.sidebar.write(f"📧 {user_info['email']}")

        # Logout button - directly visible, not in expander
        if st.sidebar.button("🚪 Cerrar Sesión", type="secondary", use_container_width=True):
            self.logout()

    def show_admin_menu(self):
        """Show admin menu options"""

        if not self.is_authenticated():
            return

        st.sidebar.markdown("---")
        st.sidebar.subheader("⚙️ Administración")

        # Change password and email
        if st.sidebar.button("🔑 Cambiar Contraseña y Email"):
            st.session_state.show_password_change = True

    def show_user_management(self):
        """Show user management interface"""

        st.subheader("👥 Gestión de Usuarios")

        # Get current user info
        current_user = self.get_current_user()
        if not current_user:
            return

        # Show current user info
        st.write("**Usuario Actual:**")
        user_info = self.auth_manager.get_user_info(current_user['username'])
        if user_info:
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Nombre:** {user_info['name']}")
                st.write(f"**Email:** {user_info['email']}")
            with col2:
                st.write(f"**Usuario:** {current_user['username']}")
                st.write(
                    f"**Activo:** {'Sí' if user_info.get('active', True) else 'No'}")

        # Create new user form
        st.markdown("---")
        st.subheader("➕ Crear Nuevo Usuario")

        with st.form("create_user_form"):
            col1, col2 = st.columns(2)

            with col1:
                new_username = st.text_input(
                    "Usuario", placeholder="nuevo_usuario")
                new_name = st.text_input(
                    "Nombre Completo", placeholder="Nombre del usuario")

            with col2:
                new_email = st.text_input(
                    "Email", placeholder="usuario@universidad.edu.mx")
                new_password = st.text_input(
                    "Contraseña", type="password", placeholder="Mínimo 8 caracteres")

            if st.form_submit_button("Crear Usuario", type="primary"):
                if new_username and new_name and new_email and new_password:
                    if self.auth_manager.create_user(new_username, new_password, new_name, new_email):
                        st.success(
                            f"Usuario '{new_username}' creado exitosamente")
                    else:
                        st.error(
                            "Error al crear usuario. Verifique que el usuario no exista y la contraseña sea segura.")
                else:
                    st.error("Por favor, complete todos los campos")

    def show_session_management(self):
        """Show active sessions management"""

        st.subheader("🔐 Sesiones Activas")

        active_sessions = self.auth_manager.get_active_sessions()

        if not active_sessions:
            st.info("No hay sesiones activas")
            return

        st.write(f"**Total de sesiones activas:** {len(active_sessions)}")

        # Show sessions in a table
        for i, session in enumerate(active_sessions):
            with st.expander(f"Sesión {i+1}: {session['name']} ({session['username']})"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Usuario:** {session['username']}")
                    st.write(f"**Nombre:** {session['name']}")
                    st.write(f"**Inicio:** {session['created_at'][:19]}")

                with col2:
                    st.write(
                        f"**Última actividad:** {session['last_activity'][:19]}")
                    st.write(f"**Expira:** {session['expires_at'][:19]}")

                    # Logout button for other sessions
                    current_user = self.get_current_user()
                    if current_user and session['session_id'] != current_user.get('session_id'):
                        if st.button(f"Cerrar Sesión", key=f"logout_{session['session_id']}"):
                            if self.auth_manager.logout(session['session_id']):
                                st.success("Sesión cerrada")
                                st.rerun()

    def show_password_change(self):
        """Show password and email change form"""

        st.subheader("🔑 Cambiar Contraseña y Email")

        current_user = self.get_current_user()
        if not current_user:
            return

        # Show current info
        st.info(
            f"**Usuario actual:** {current_user['name']} ({current_user['email']})")

        # Create tabs for different changes
        tab1, tab2 = st.tabs(["🔑 Cambiar Contraseña", "📧 Cambiar Email"])

        with tab1:
            with st.form("change_password_form"):
                st.write("**Cambiar Contraseña:**")
                old_password = st.text_input(
                    "Contraseña Actual", type="password")
                new_password = st.text_input("Nueva Contraseña", type="password",
                                             help="Mínimo 8 caracteres, debe incluir caracteres especiales")
                confirm_password = st.text_input(
                    "Confirmar Nueva Contraseña", type="password")

                if st.form_submit_button("Cambiar Contraseña", type="primary"):
                    if not all([old_password, new_password, confirm_password]):
                        st.error("Por favor, complete todos los campos")
                    elif new_password != confirm_password:
                        st.error("Las contraseñas no coinciden")
                    elif len(new_password) < 8:
                        st.error(
                            "La contraseña debe tener al menos 8 caracteres")
                    else:
                        # First verify current password using email authentication
                        verify_session = self.auth_manager.authenticate(
                            current_user['email'], old_password)
                        if not verify_session:
                            st.error("❌ La contraseña actual es incorrecta")
                        elif self.auth_manager.change_password(current_user['username'], old_password, new_password):
                            st.success("✅ Contraseña cambiada exitosamente")
                            # Force re-authentication
                            self.logout()
                        else:
                            st.error(
                                "❌ La nueva contraseña no cumple con los requisitos de seguridad. Debe tener al menos 8 caracteres y contener al menos un carácter especial (!@#$%^&*()_+-=[]{}|;:,.<>?)")

        with tab2:
            with st.form("change_email_form"):
                st.write("**Cambiar Email:**")
                current_password = st.text_input(
                    "Contraseña Actual (para confirmar)", type="password")
                new_email = st.text_input("Nuevo Email",
                                          value=current_user['email'],
                                          help="Ingrese el nuevo email para el administrador")
                new_name = st.text_input("Nombre Completo",
                                         value=current_user['name'],
                                         help="Puede actualizar también su nombre")

                if st.form_submit_button("Actualizar Información", type="primary"):
                    if not all([current_password, new_email, new_name]):
                        st.error("Por favor, complete todos los campos")
                    elif "@" not in new_email or "." not in new_email:
                        st.error("Por favor, ingrese un email válido")
                    else:
                        # Verify current password first using current email
                        session_data = self.auth_manager.authenticate(
                            current_user['email'], current_password)
                        if session_data:
                            if self.auth_manager.update_user_info(current_user['username'], new_name, new_email):
                                st.success(
                                    "Información actualizada exitosamente")
                                # Update session info
                                st.session_state.user_info['email'] = new_email
                                st.session_state.user_info['name'] = new_name
                                st.rerun()
                            else:
                                st.error("Error al actualizar la información")
                        else:
                            st.error("Contraseña incorrecta")


# Global authentication instance
auth = StreamlitAuth()
