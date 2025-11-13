"""
Página de Seguimiento de Maestros
Muestra maestros que no han enviado formularios y permite enviar recordatorios
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.connection import SessionLocal
from app.utils.email_notifications import EmailNotificationManager
from app.auth.streamlit_auth import auth

def show_seguimiento_maestros_page():
    """Muestra la página de seguimiento de maestros"""
    
    # Obtener URL de la aplicación desde variable de entorno
    app_url = os.getenv("APP_URL", "http://localhost:8501")
    
    # Require authentication
    if not auth.is_authenticated():
        auth.show_login_form()
        return

    st.title("📧 Seguimiento de Maestros")
    st.markdown("Monitoree maestros que no han enviado formularios y envíe recordatorios automáticos.")

    # Crear tabs para diferentes funciones
    tab1, tab2 = st.tabs(["📋 Maestros Pendientes", "📧 Enviar Recordatorios"])

    db = SessionLocal()
    email_manager = EmailNotificationManager(db)

    try:
        with tab1:
            show_maestros_pendientes(email_manager)
        
        with tab2:
            show_envio_recordatorios(email_manager)
            
    finally:
        db.close()

def get_available_periods():
    """Obtiene los períodos académicos disponibles dinámicamente desde la base de datos"""
    db = SessionLocal()
    try:
        from app.models.database import FormularioEnvioDB
        
        # Obtener períodos únicos de formularios activos
        periods = db.query(
            FormularioEnvioDB.año_academico,
            FormularioEnvioDB.trimestre
        ).filter(
            FormularioEnvioDB.es_version_activa == True
        ).distinct().all()
        
        # Convertir a formato "YYYY-QX"
        period_list = []
        for year, trimestre in periods:
            if year and trimestre:
                # Convertir "Trimestre X" a "QX"
                quarter_num = trimestre.replace("Trimestre ", "Q")
                period_str = f"{year}-{quarter_num}"
                period_list.append(period_str)
        
        # Ordenar los períodos
        period_list.sort()
        
        return ["-- Seleccione un período --"] + period_list
        
    except Exception as e:
        print(f"Error obteniendo períodos: {e}")
        return ["-- Seleccione un período --"]
    finally:
        db.close()

def show_maestros_pendientes(email_manager: EmailNotificationManager):
    """Muestra la lista de maestros que no han enviado formularios"""
    
    # Obtener URL de la aplicación desde variable de entorno
    app_url = os.getenv("APP_URL", "http://localhost:8501")
    
    st.subheader("📋 Maestros Sin Formulario Enviado")
    
    # Filtros
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        # Obtener períodos disponibles dinámicamente
        available_periods = get_available_periods()
        periodo_filter = st.selectbox(
            "Filtrar por período:",
            available_periods,
            help="Seleccione un período específico o vea todos (solo se muestran períodos con formularios)"
        )
    
    with col2:
        ordenar_por = st.selectbox(
            "Ordenar por:",
            ["Nombre", "Fecha de registro", "Última notificación", "Total notificaciones"],
            help="Criterio de ordenamiento"
        )
    
    with col3:
        if st.button("🔄 Actualizar"):
            st.rerun()
    
    # Verificar si se seleccionó un período válido
    if periodo_filter == "-- Seleccione un período --":
        st.info("📋 Por favor seleccione un período específico para ver los maestros pendientes.")
        return
    
    # Obtener datos
    periodo_academico = periodo_filter
    maestros_pendientes = email_manager.get_maestros_sin_formulario(periodo_academico)
    
    if not maestros_pendientes:
        st.success("🎉 ¡Excelente! Todos los maestros autorizados han enviado sus formularios.")
        return
    
    # Ordenar resultados
    if ordenar_por == "Nombre":
        maestros_pendientes.sort(key=lambda x: x['nombre_completo'])
    elif ordenar_por == "Fecha de registro":
        maestros_pendientes.sort(key=lambda x: x['fecha_creacion'], reverse=True)
    elif ordenar_por == "Última notificación":
        maestros_pendientes.sort(key=lambda x: x['ultima_notificacion'] or datetime.min, reverse=True)
    elif ordenar_por == "Total notificaciones":
        maestros_pendientes.sort(key=lambda x: x['total_notificaciones'], reverse=True)
    
    # Mostrar estadísticas
    st.error(f"⚠️ **{len(maestros_pendientes)} maestros** no han enviado su formulario")
    
    # Estadísticas adicionales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sin_notificaciones = sum(1 for m in maestros_pendientes if m['total_notificaciones'] == 0)
        st.metric("Sin Notificaciones", sin_notificaciones)
    
    with col2:
        con_recordatorios = sum(1 for m in maestros_pendientes if m['total_notificaciones'] > 0)
        st.metric("Con Recordatorios", con_recordatorios)
    
    with col3:
        # Maestros con última notificación hace más de 7 días
        hace_semana = datetime.now() - timedelta(days=7)
        necesitan_seguimiento = sum(1 for m in maestros_pendientes 
                                  if not m['ultima_notificacion'] or m['ultima_notificacion'] < hace_semana)
        st.metric("Necesitan Seguimiento", necesitan_seguimiento)
    
    # Tabla detallada
    st.subheader("📊 Detalle de Maestros Pendientes")
    
    for i, maestro in enumerate(maestros_pendientes):
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            
            with col1:
                st.write(f"**{maestro['nombre_completo']}**")
                st.write(f"📧 {maestro['correo_institucional']}")
            
            with col2:
                st.write(f"📅 Registrado: {maestro['fecha_creacion'].strftime('%Y-%m-%d')}")
                if maestro['ultima_notificacion']:
                    dias_desde_ultima = (datetime.now() - maestro['ultima_notificacion']).days
                    st.write(f"🔔 Última notif: hace {dias_desde_ultima} días")
                else:
                    st.write("🔔 Sin notificaciones")
            
            with col3:
                st.write(f"📊 Total notificaciones: {maestro['total_notificaciones']}")
                if maestro['tipo_ultima_notificacion']:
                    color = {"RECORDATORIO": "🟡", "URGENTE": "🟠", "FINAL": "🔴"}
                    emoji = color.get(maestro['tipo_ultima_notificacion'], "⚪")
                    st.write(f"{emoji} Último tipo: {maestro['tipo_ultima_notificacion']}")
            
            with col4:
                # Botón de acción rápida
                if maestro['total_notificaciones'] == 0:
                    if st.button("📧 Enviar Recordatorio", key=f"quick_reminder_{maestro['id']}"):
                        # Usar el mensaje personalizado si está disponible
                        mensaje_personalizado = st.session_state.get('mensaje_recordatorio', 
                            f"Hola {{nombre}},\n\nEspero que te encuentres muy bien. Te escribo para recordarte de manera amistosa que aún no hemos recibido tu informe de actividades académicas del período {{periodo}}.\n\n**¿Qué necesitas hacer?**\n1. Entra al formulario en línea: {app_url}\n2. Completa la información de tus actividades académicas\n3. Envía el formulario para que podamos revisarlo\n\n**Información importante:**\n- Tu correo registrado es: {{email}}\n- El formulario incluye secciones para cursos, publicaciones, eventos y otras actividades\n- Una vez que lo envíes, lo revisaremos\n\nSi tienes alguna duda o problema técnico, no dudes en escribirme o llamarme.\n\nSaludos cordiales,\nCoordinación Académica\n\nP.D.: Agradezco mucho tu colaboración con este proceso.")
                        
                        exito = email_manager.enviar_notificacion_personalizada(maestro, mensaje_personalizado, periodo_academico)
                        if exito:
                            st.success(f"✅ Recordatorio enviado a {maestro['nombre_completo']}")
                            st.rerun()
                        else:
                            st.error("❌ Error enviando recordatorio")
                elif maestro['ultima_notificacion'] and (datetime.now() - maestro['ultima_notificacion']).days > 7:
                    if st.button("🔔 Seguimiento", key=f"followup_{maestro['id']}"):
                        # Usar el mensaje personalizado para seguimiento también
                        mensaje_personalizado = st.session_state.get('mensaje_recordatorio', 
                            f"Hola {{nombre}},\n\nEspero que te encuentres muy bien. Te escribo para recordarte de manera amistosa que aún no hemos recibido tu informe de actividades académicas del período {{periodo}}.\n\n**¿Qué necesitas hacer?**\n1. Entra al formulario en línea: {app_url}\n2. Completa la información de tus actividades académicas\n3. Envía el formulario para que podamos revisarlo\n\n**Información importante:**\n- Tu correo registrado es: {{email}}\n- El formulario incluye secciones para cursos, publicaciones, eventos y otras actividades\n- Una vez que lo envíes, lo revisaremos\n\nSi tienes alguna duda o problema técnico, no dudes en escribirme o llamarme.\n\nSaludos cordiales,\nCoordinación Académica\n\nP.D.: Agradezco mucho tu colaboración con este proceso.")
                        
                        exito = email_manager.enviar_notificacion_personalizada(maestro, mensaje_personalizado, periodo_academico)
                        if exito:
                            st.success(f"✅ Seguimiento enviado a {maestro['nombre_completo']}")
                            st.rerun()
                        else:
                            st.error("❌ Error enviando seguimiento")
                else:
                    st.write("✅ Notificado recientemente")
            
            st.divider()

def show_envio_recordatorios(email_manager: EmailNotificationManager):
    """Muestra la interfaz para envío masivo de recordatorios"""
    
    # Obtener URL de la aplicación desde variable de entorno
    app_url = os.getenv("APP_URL", "http://localhost:8501")
    
    st.subheader("📧 Envío Masivo de Recordatorios")
    
    # Configuración del envío
    col1, col2 = st.columns(2)
    
    with col1:
        # Obtener períodos disponibles dinámicamente
        available_periods = get_available_periods()  # Ya incluye "-- Seleccione un período --"
        periodo_academico = st.selectbox(
            "Período académico:",
            available_periods,
            help="Seleccione el período para el cual se solicita el formulario"
        )
    
    with col2:
        st.write("**Personalizar Mensaje:**")
        
        # Campo para personalizar el mensaje
        mensaje_personalizado = st.text_area(
            "Mensaje del recordatorio:",
            value=f"Hola {{nombre}},\n\nEspero que te encuentres muy bien. Te escribo para recordarte de manera amistosa que aún no hemos recibido tu informe de actividades académicas del período {{periodo}}.\n\n**¿Qué necesitas hacer?**\n1. Entra al formulario en línea: {app_url}\n2. Completa la información de tus actividades académicas\n3. Envía el formulario para que podamos revisarlo\n\n**Información importante:**\n- Tu correo registrado es: {{email}}\n- El formulario incluye secciones para cursos, publicaciones, eventos y otras actividades\n- Una vez que lo envíes, lo revisaremos\n\nSi tienes alguna duda o problema técnico, no dudes en escribirme o llamarme.\n\nSaludos cordiales,\nCoordinación Académica\n\nP.D.: Agradezco mucho tu colaboración con este proceso.",
            height=200,
            help="Puede usar {nombre}, {periodo} y {email} como variables que se reemplazarán automáticamente"
        )
        
        # Guardar el mensaje en session_state para usarlo en botones individuales
        st.session_state.mensaje_recordatorio = mensaje_personalizado
    
    # Verificar si se seleccionó un período válido
    if periodo_academico == "-- Seleccione un período --":
        st.info("📋 Por favor seleccione un período específico para enviar recordatorios.")
        return
    
    # Obtener maestros pendientes
    maestros_pendientes = email_manager.get_maestros_sin_formulario(periodo_academico)
    
    if not maestros_pendientes:
        st.success("🎉 No hay maestros pendientes para este período.")
        return
    
    # Mostrar lista de destinatarios
    st.write(f"**📋 Destinatarios ({len(maestros_pendientes)} maestros):**")
    
    # Crear DataFrame para mostrar
    df_maestros = pd.DataFrame([{
        'Nombre': m['nombre_completo'],
        'Email': m['correo_institucional'],
        'Notificaciones Previas': m['total_notificaciones'],
        'Última Notificación': m['ultima_notificacion'].strftime('%Y-%m-%d') if m['ultima_notificacion'] else 'Nunca'
    } for m in maestros_pendientes])
    
    st.dataframe(df_maestros, use_container_width=True)
    
    # Confirmación y envío
    st.subheader("🚀 Confirmar Envío")
    
    col1, col2 = st.columns(2)
    
    with col1:
        confirmar_envio = st.checkbox(
            f"Confirmo que deseo enviar {len(maestros_pendientes)} recordatorios",
            help="Marque esta casilla para habilitar el envío"
        )
    
    with col2:
        if confirmar_envio:
            if st.button("📧 Enviar Recordatorios Masivos", type="primary"):
                with st.spinner("Enviando recordatorios..."):
                    # Enviar recordatorios con mensaje personalizado
                    resultados = email_manager.enviar_recordatorios_masivos_personalizado(
                        periodo_academico, mensaje_personalizado)
                
                # Mostrar resultados
                st.success(f"✅ Proceso completado!")
                
                col_res1, col_res2, col_res3 = st.columns(3)
                with col_res1:
                    st.metric("Total Maestros", resultados['total_maestros'])
                with col_res2:
                    st.metric("Enviados Exitosos", resultados['enviados_exitosos'])
                with col_res3:
                    st.metric("Errores", resultados['errores'])
                
                # Detalles
                if resultados['detalles']:
                    st.write("**📊 Detalles del Envío:**")
                    df_resultados = pd.DataFrame(resultados['detalles'])
                    st.dataframe(df_resultados, use_container_width=True)
                
                if resultados['errores'] > 0:
                    st.warning(f"⚠️ {resultados['errores']} recordatorios no pudieron enviarse. Revise la configuración de email.")



if __name__ == "__main__":
    show_seguimiento_maestros_page()