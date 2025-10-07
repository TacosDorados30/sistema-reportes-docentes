import streamlit as st
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.auth.streamlit_auth import auth

def show_login_page():
    """Show login page"""
    
    st.set_page_config(
        page_title="Login - Sistema de Reportes Docentes",
        page_icon="🔐",
        layout="centered"
    )
    
    # Check if already authenticated
    if auth.is_authenticated():
        st.success("Ya está autenticado")
        st.write("Puede acceder al dashboard desde el menú principal.")
        
        if st.button("Ir al Dashboard"):
            st.switch_page("dashboard/main.py")
        
        if st.button("Cerrar Sesión"):
            auth.logout()
        
        return
    
    # Show login form
    auth.require_authentication()

if __name__ == "__main__":
    show_login_page()